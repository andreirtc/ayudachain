"""Deterministic DDL compiler for explicit migration tooling only."""
from sqlalchemy import create_mock_engine
from backend.app.models.mvp import metadata, IMMUTABLE, FROZEN_PROJECTIONS, AUDITED


def relational_guards():
    return '''CREATE FUNCTION validate_household_members() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE version_id uuid; household uuid;
    BEGIN
      IF TG_TABLE_NAME='household_versions' THEN version_id:=NEW.id;
      ELSE version_id:=NEW.household_version_id; END IF;
      SELECT household_id INTO household FROM household_versions WHERE id=version_id;
      IF (SELECT count(*) FROM member_versions WHERE household_version_id=version_id AND is_head)!=1
        OR EXISTS(SELECT 1 FROM member_versions m JOIN household_members h ON h.id=m.member_id WHERE m.household_version_id=version_id AND h.household_id!=household)
      THEN RAISE EXCEPTION 'exactly one head and same household members required' USING ERRCODE='23514'; END IF;
      RETURN NEW;
    END $$;
    CREATE CONSTRAINT TRIGGER household_members_complete AFTER INSERT ON household_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION validate_household_members();
    CREATE CONSTRAINT TRIGGER household_members_parent AFTER INSERT ON member_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION validate_household_members();'''


def paid_guards():
    return '''CREATE FUNCTION preserve_paid_entitlement() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF EXISTS(SELECT 1 FROM recorded_handovers WHERE entitlement_id=OLD.id)
        AND (NEW.current_version_id IS DISTINCT FROM OLD.current_version_id OR NEW.business_status!='handed_over')
      THEN RAISE EXCEPTION 'paid entitlement is permanently locked' USING ERRCODE='23514'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER preserve_paid_entitlement BEFORE UPDATE ON entitlements FOR EACH ROW EXECUTE FUNCTION preserve_paid_entitlement();
    CREATE FUNCTION preserve_paid_attempt() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF EXISTS(SELECT 1 FROM recorded_handovers WHERE transaction_id=OLD.id)
        AND NEW.current_attempt_id IS DISTINCT FROM OLD.current_attempt_id
      THEN RAISE EXCEPTION 'paid transaction attempt is permanently locked' USING ERRCODE='23514'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER preserve_paid_attempt BEFORE UPDATE ON payout_transactions FOR EACH ROW EXECUTE FUNCTION preserve_paid_attempt();'''


def ddl():
    statements=[]
    indexes=[];deferred=[]
    from sqlalchemy.schema import CreateIndex,AddConstraint
    def emit(statement,*args,**kwargs):
        target=indexes if isinstance(statement,CreateIndex) else deferred if isinstance(statement,AddConstraint) else statements
        target.append(str(statement.compile(dialect=engine.dialect))+';')
    engine=create_mock_engine('postgresql+psycopg://',emit)
    metadata.create_all(engine)
    # Preserve dependency-ordered tables; SQLAlchemy stores indexes and cyclic
    # FK constraints in sets, so emit those after tables in stable text order.
    statements.extend(sorted(indexes));statements.extend(sorted(deferred))
    statements.append('CREATE SEQUENCE audit_sequence;')
    statements.append('''CREATE FUNCTION immutable_fact() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'append-only history' USING ERRCODE='55000'; END $$;''')
    for name in sorted(IMMUTABLE):
        statements.append(f'CREATE TRIGGER immutable_{name} BEFORE UPDATE OR DELETE ON {name} FOR EACH ROW EXECUTE FUNCTION immutable_fact();')
    statements.append('''CREATE FUNCTION frozen_content() RETURNS trigger LANGUAGE plpgsql AS $$
       DECLARE allowed text[]:=string_to_array(TG_ARGV[0],',');
       BEGIN
         IF TG_OP='DELETE' OR (to_jsonb(NEW)-allowed) IS DISTINCT FROM (to_jsonb(OLD)-allowed)
         THEN RAISE EXCEPTION 'immutable content' USING ERRCODE='55000'; END IF;
         RETURN NEW;
       END $$;''')
    for name,allowed in sorted(FROZEN_PROJECTIONS.items()):
        statements.append(f"CREATE TRIGGER frozen_{name} BEFORE UPDATE OR DELETE ON {name} FOR EACH ROW EXECUTE FUNCTION frozen_content('{','.join(sorted(allowed))}');")
    statements.append('''CREATE FUNCTION require_audit_target() RETURNS trigger LANGUAGE plpgsql AS $$
       DECLARE found boolean;
       BEGIN
         EXECUTE format('SELECT EXISTS(SELECT 1 FROM audit_targets WHERE %I=$1)',TG_ARGV[0]) INTO found USING NEW.id;
         IF NOT found THEN RAISE EXCEPTION 'business change requires typed audit' USING ERRCODE='23514'; END IF;
         RETURN NEW;
       END $$;''')
    for name,slot in sorted(AUDITED.items()):
        statements.append(f"CREATE CONSTRAINT TRIGGER audit_{name} AFTER INSERT ON {name} DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('{slot}');")
    statements.append('''CREATE FUNCTION audit_not_empty() RETURNS trigger LANGUAGE plpgsql AS $$
       BEGIN
         IF NOT EXISTS(SELECT 1 FROM audit_targets WHERE audit_event_id=NEW.id)
         THEN RAISE EXCEPTION 'empty audit event' USING ERRCODE='23514'; END IF;
         RETURN NEW;
       END $$;
       CREATE CONSTRAINT TRIGGER audit_not_empty AFTER INSERT ON audit_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION audit_not_empty();''')
    statements.append('''CREATE FUNCTION validate_correction() RETURNS trigger LANGUAGE plpgsql AS $$
       DECLARE o fund_entries; r fund_entries; p fund_entries;
       BEGIN
         SELECT * INTO o FROM fund_entries WHERE id=NEW.original_entry_id;
         SELECT * INTO r FROM fund_entries WHERE id=NEW.reversal_entry_id;
         SELECT * INTO p FROM fund_entries WHERE id=NEW.replacement_entry_id;
         IF o.kind NOT IN ('release','replacement') OR r.kind!='reversal' OR p.kind!='replacement'
           OR r.original_entry_id!=o.id OR p.original_entry_id!=o.id OR r.correction_set_id!=NEW.id OR p.correction_set_id!=NEW.id
           OR r.delta_centavos != -o.delta_centavos OR r.source_root_id!=o.source_root_id OR p.source_root_id!=o.source_root_id
           OR r.disaster_id!=o.disaster_id OR p.disaster_id!=o.disaster_id
         THEN RAISE EXCEPTION 'invalid atomic correction' USING ERRCODE='23514'; END IF;
         RETURN NEW;
       END $$;
       CREATE CONSTRAINT TRIGGER complete_correction AFTER INSERT ON fund_correction_sets DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION validate_correction();''')
    statements.append(relational_guards())
    statements.append(paid_guards())
    return '\n'.join(statements)


def migrate(db):
    db.execute('CREATE TABLE IF NOT EXISTS mvp_migrations(version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT clock_timestamp())')
    if db.execute("SELECT 1 FROM mvp_migrations WHERE version='0001'").fetchone():
        if not db.execute("SELECT 1 FROM mvp_migrations WHERE version='0005'").fetchone():
            # A paid difference can depend on both a later decision and input.
            # Preserve facts while removing the erroneous exclusive-or guard.
            db.execute('ALTER TABLE paid_difference_events DROP CONSTRAINT IF EXISTS paid_difference_events_required_pair')
            db.execute('DROP INDEX IF EXISTS uq_paid_difference_new_input_version_id')
            db.execute('DROP INDEX IF EXISTS uq_paid_difference_new_decision_id')
            db.execute("INSERT INTO mvp_migrations(version) VALUES('0005')")
        changed=extend_constraints(db)
        if not db.execute("SELECT 1 FROM mvp_migrations WHERE version='0003'").fetchone():
            statement=ddl().split('CREATE FUNCTION validate_correction()',1)[1].split('CREATE CONSTRAINT TRIGGER complete_correction',1)[0]
            db.execute('CREATE OR REPLACE FUNCTION validate_correction()'+statement)
            db.execute("INSERT INTO mvp_migrations(version) VALUES('0003')")
            changed=True
        if not db.execute("SELECT 1 FROM mvp_migrations WHERE version='0004'").fetchone():
            db.execute(relational_guards())
            db.execute("INSERT INTO mvp_migrations(version) VALUES('0004')")
            changed=True
        if not db.execute("SELECT 1 FROM mvp_migrations WHERE version='0006'").fetchone():
            db.execute(paid_guards())
            db.execute("INSERT INTO mvp_migrations(version) VALUES('0006')")
            changed=True
        if not db.execute("SELECT 1 FROM mvp_migrations WHERE version='0007'").fetchone():
            db.execute('ALTER TABLE release_document_uses DROP CONSTRAINT pk_release_document_uses')
            db.execute('ALTER TABLE release_document_uses ADD CONSTRAINT pk_release_document_uses PRIMARY KEY(run_id,byte_sha256)')
            db.execute("INSERT INTO mvp_migrations(version) VALUES('0007')")
            changed=True
        return changed
    db.execute(ddl())
    db.execute("INSERT INTO mvp_migrations(version) VALUES('0001')")
    db.execute("INSERT INTO mvp_migrations(version) VALUES('0004')")
    db.execute("INSERT INTO mvp_migrations(version) VALUES('0005')")
    db.execute("INSERT INTO mvp_migrations(version) VALUES('0006')")
    db.execute("INSERT INTO mvp_migrations(version) VALUES('0007')")
    return True


def extend_constraints(db):
    """Explicit approved T02 relationship/grant upgrade; no data rewriting."""
    from sqlalchemy.schema import AddConstraint,CreateIndex
    from sqlalchemy.dialects.postgresql import dialect
    from sqlalchemy import ForeignKeyConstraint,UniqueConstraint,CheckConstraint
    d=dialect()
    known={r['conname'] for r in db.execute('SELECT conname FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname=current_schema()').fetchall()}
    indexes={r['indexname'] for r in db.execute('SELECT indexname FROM pg_indexes WHERE schemaname=current_schema()').fetchall()}
    changes=[]
    foreign_keys=[]
    for table in metadata.tables.values():
        for constraint in table.constraints:
            if isinstance(constraint,(ForeignKeyConstraint,UniqueConstraint,CheckConstraint)):
                name=d.identifier_preparer.format_constraint(constraint).strip('"')
                if name not in known:
                    statement=str(AddConstraint(constraint).compile(dialect=d))+';'
                    (foreign_keys if isinstance(constraint,ForeignKeyConstraint) else changes).append(statement)
                    known.add(name)
        for index in table.indexes:
            name=d.identifier_preparer.format_index(index).strip('"')
            if name not in indexes:
                changes.append(str(CreateIndex(index).compile(dialect=d))+';');indexes.add(name)
    changes.extend(foreign_keys)
    if changes:
        db.execute('\n'.join(changes))
        from backend.app.config import ROOT
        (ROOT/'backend/migrations/0002_relationships.sql').write_text('\n'.join(changes)+'\n',encoding='utf-8')
        db.execute("INSERT INTO mvp_migrations(version) VALUES('0002') ON CONFLICT DO NOTHING")
    return bool(changes)
