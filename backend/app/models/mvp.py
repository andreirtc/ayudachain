"""Typed PostgreSQL catalogue implementing docs/system/erd.md.

Only migration tooling creates these tables. Compact declarations expand to real
columns, composite foreign keys and indexes; no generic workflow/JSON datastore.
"""
from sqlalchemy import (MetaData, Table, Column, ForeignKeyConstraint, UniqueConstraint,
                        CheckConstraint, Index, text, String, Text, Integer, BigInteger,
                        Boolean, Date, DateTime, LargeBinary, Numeric)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INTERVAL
from sqlalchemy.sql.elements import conv

metadata = MetaData(naming_convention={'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
                                     'pk': 'pk_%(table_name)s', 'uq': 'uq_%(table_name)s_%(column_0_N_name)s'})
IMMUTABLE = set()
AUDITED = {}
SCOPED = set()
TYPES = {'text': Text, 'int': Integer, 'bigint': BigInteger, 'bool': Boolean,
         'date': Date, 'time': DateTime(timezone=True), 'bytes': LargeBinary,
         'json': JSONB, 'uuid': UUID(as_uuid=True), 'numeric': Numeric(78, 0),
         'strings': ARRAY(Text), 'interval': INTERVAL}


def table(name, fields='', *, mutable=False, parent=None, pk=('id',), global_table=False, checks=(), unique=(), audit=None):
    cols = []
    refs = []
    enums = []
    if 'id' in pk:
        cols.append(Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')))
    if not global_table:
        SCOPED.add(name)
        cols.extend([Column('run_id', UUID(as_uuid=True), nullable=False,primary_key='run_id' in pk), Column('office_id', UUID(as_uuid=True), nullable=False,primary_key='office_id' in pk)])
        refs.append(ForeignKeyConstraint(['run_id', 'office_id'], ['evaluation_runs.id', 'evaluation_runs.office_id'], deferrable=True, initially='DEFERRED'))
    for item in fields.split():
        nullable = item.endswith('?')
        item = item.rstrip('?')
        if '@' in item:
            key, target = item.split('@')
            typ = 'uuid'
            if global_table or target in {'field_offices', 'evaluation_runs'}:
                refs.append(ForeignKeyConstraint([key], [target+'.id'], deferrable=True, initially='DEFERRED'))
            else:
                refs.append(ForeignKeyConstraint(['run_id', 'office_id', key], [target+'.run_id', target+'.office_id', target+'.id'],
                                                 name='fk_'+name+'_'+key, deferrable=True, initially='DEFERRED'))
        else:
            key, typ = item.split(':', 1)
        if typ.startswith('enum='):
            values = typ[5:].split(',')
            typ = 'text'
            enums.append(CheckConstraint(key+' IN ('+','.join("'"+v+"'" for v in values)+')', name=name+'_'+key+'_enum'))
        cols.append(Column(key, TYPES[typ], nullable=nullable, primary_key=key in pk))
    if not global_table:
        cols.extend([Column('created_at', DateTime(timezone=True), nullable=False, server_default=text('clock_timestamp()')),
                     Column('created_by', UUID(as_uuid=True), nullable=False),
                     Column('identity_assurance', Text, nullable=False, server_default=text("'claimed_unverified'"))])
        refs.append(ForeignKeyConstraint(['run_id', 'office_id', 'created_by'], ['actors.run_id', 'actors.office_id', 'actors.id'],
                                        name='fk_'+name+'_created_by', deferrable=True, initially='DEFERRED'))
        if 'id' in pk: unique = (*unique, ('run_id','office_id','id'))
    t = Table(name, metadata, *cols, *refs, *enums, *(CheckConstraint(c, name=name+'_check_'+str(i)) for i,c in enumerate(checks)),
              *(UniqueConstraint(*u) for u in unique))
    if not mutable and not global_table: IMMUTABLE.add(name)
    if parent:
        t.append_constraint(UniqueConstraint('run_id','office_id',parent,'id'))
        if 'predecessor_id' in t.c:
            t.append_constraint(ForeignKeyConstraint(['run_id','office_id',parent,'predecessor_id'], [name+'.run_id',name+'.office_id',name+'.'+parent,name+'.id'],
                                                    name='fk_'+name+'_predecessor_parent', deferrable=True, initially='DEFERRED'))
            Index('uq_'+name+'_predecessor', t.c.predecessor_id, unique=True, postgresql_where=t.c.predecessor_id.is_not(None))
            Index('uq_'+name+'_initial', t.c[parent], unique=True, postgresql_where=t.c.predecessor_id.is_(None))
    if audit: AUDITED[name] = audit
    for col in t.c:
        if col.name.endswith('_id') and col.name not in {'id','run_id','office_id'}:
            Index('ix_'+name+'_'+col.name, col)
    return t


table('field_offices', 'name:text revision:int check_data_revision:int', mutable=True, global_table=True,
      checks=('revision>=0','check_data_revision>=0'))
table('evaluation_runs', 'office_id@field_offices namespace:bytes state:enum=active,retired clock_mode:enum=wall_clock,simulated clock_offset:interval created_at:time',
      mutable=True, global_table=True, unique=(('id','office_id'),), checks=('octet_length(namespace)=32',))
Index('uq_active_run', metadata.tables['evaluation_runs'].c.office_id, unique=True, postgresql_where=text("state='active'"))
table('barangays','name:text zone_description:text?', mutable=True)
table('disasters','name:text external_reference:text? current_input_version_id@amount_input_versions? inputs_locked_at:time? revision:int', mutable=True)
table('damage_categories','code:text label:text', unique=(('run_id','code'),))
table('actors','role:enum=dswd,barangay,beneficiary,disbursing,auditor,system display_name:text email:text? current_version_id@actor_versions current_member_link_id@actor_member_links? revision:int', mutable=True)
table('actor_versions','actor_id@actors predecessor_id@actor_versions? status:enum=pending,active,deactivated barangay_id@barangays? position:text? nomination_id@nominations? approved_by@actors? reason:text?', parent='actor_id', audit='actor_version_id')
table('nominations','candidate_actor_id@actors barangay_id@barangays position:text nominator_name:text entered_by@actors')
table('households','display_id:text current_version_id@household_versions current_pin_id@assisted_pins? registered_without_id:bool revision:int', mutable=True,
      unique=(('run_id','display_id'),), checks=("display_id ~ '^DFC-2026-[A-Z0-9]{4,}$'",))
table('household_members','household_id@households')
table('household_versions','household_id@households predecessor_id@household_versions? declared_barangay_id@barangays address:text zone:text residence_state:enum=unconfirmed,confirmed,disputed identity_state:enum=evidence_recorded,pending_field_check,field_checked_with_photo_id id_type:text? id_number:text? head_photo_evidence_id@evidence_versions? id_evidence_id@evidence_versions? assister_id@actors? registry_review_id@registry_reviews?', parent='household_id', audit='household_version_id')
table('member_versions','household_version_id@household_versions member_id@household_members name:text birth_date:date? relationship:text is_head:bool', pk=('household_version_id','member_id'))
Index('uq_one_head', metadata.tables['member_versions'].c.household_version_id, unique=True, postgresql_where=text('is_head'))
table('household_link_versions','household_id@households predecessor_id@household_link_versions? beneficiary_actor_id@actors? phone:text? basis_review_id@registry_reviews? reason:text?', parent='household_id', audit='link_version_id')
table('household_links','household_id@households link_version_id@household_link_versions beneficiary_actor_id@actors?', mutable=True, pk=('household_id',))
Index('uq_current_beneficiary_link',metadata.tables['household_links'].c.beneficiary_actor_id,unique=True,postgresql_where=text('beneficiary_actor_id IS NOT NULL'))
table('actor_member_links','actor_id@actors member_id@household_members predecessor_id@actor_member_links? basis_review_id@registry_reviews? reason:text',parent='actor_id')
table('registry_reviews','household_id@households prior_version_id@household_versions? result_version_id@household_versions? action:enum=residence_confirm,residence_dispute,residence_resolve,field_check,facts_correct,contact_relink,id_check reason:text accepted_id_type:text? person_photo_compared:bool? prior_link_id@household_link_versions? result_link_id@household_link_versions?',audit='registry_review_id')
table('claim_operations','disaster_id@disasters current_version_id@operation_versions business_status:enum=not_open,open,closed revision:int',mutable=True,unique=(('disaster_id',),))
table('operation_versions','operation_id@claim_operations predecessor_id@operation_versions? action:enum=open,close response_hours:int reason:text?',parent='operation_id',checks=('response_hours>0',),audit='operation_version_id')
table('operation_barangays','operation_version_id@operation_versions barangay_id@barangays',pk=('operation_version_id','barangay_id'))
table('claims','household_id@households disaster_id@disasters operation_id@claim_operations current_submission_id@claim_submissions current_decision_id@claim_decisions? business_status:enum=waiting_barangay,awaiting_dswd,referred,approved,declined,reversed revision:int resubmissions:int',mutable=True,unique=(('household_id','disaster_id'),),checks=('resubmissions BETWEEN 0 AND 1',))
table('claim_submissions','claim_id@claims registry_version_id@household_versions link_version_id@household_link_versions? predecessor_id@claim_submissions? stated_category_id@damage_categories damage_description:text new_information:text? submitted_at:time',parent='claim_id',audit='submission_id')
table('claim_rounds','submission_id@claim_submissions referral_decision_id@claim_decisions? response_hours:int deadline_at:time state:enum=waiting,routed,closed route_kind:enum=barangay_submission,system_fallback,referral_answer,referral_timeout? primary_snapshot_id@submission_snapshots? routed_response_id@claim_responses? revision:int',mutable=True,checks=('response_hours>0',),audit='round_id')
Index('uq_initial_round',metadata.tables['claim_rounds'].c.submission_id,unique=True,postgresql_where=text('referral_decision_id IS NULL'))
Index('uq_referral_round',metadata.tables['claim_rounds'].c.referral_decision_id,unique=True,postgresql_where=text('referral_decision_id IS NOT NULL'))
table('claim_responses','round_id@claim_rounds parent_response_id@claim_responses? actor_id@actors kind:enum=endorse,not_endorse,withdraw,reverse,referral_answer residence_attested:bool? affected_attested:bool? category_opinion_id@damage_categories? category_disputed:bool related_declared:bool reason:text?',audit='response_id')
table('check_runs','submission_id@claim_submissions round_id@claim_rounds purpose:enum=intake,review,recheck,duplicate_attempt algorithm_version:text compared_data_revision:int risk_score:int simulation_adapter:text simulation_result:json simulated:bool',checks=('simulated','risk_score>=0'),audit='check_run_id')
table('check_flags','check_run_id@check_runs code:text weight:int matched_household_id@households? matched_member_id@household_members? matched_link_version_id@household_link_versions? scores:json',checks=('weight>=0',))
table('claim_decisions','claim_id@claims submission_id@claim_submissions round_id@claim_rounds predecessor_id@claim_decisions? check_run_id@check_runs action:enum=approve,decline,refer,category_change,reverse_approval category_id@damage_categories? reason:text? question:text? confirmed_by@actors? bulk_group_id:uuid? challenge_event_id@challenge_events?',parent='claim_id',checks=('confirmed_by IS NULL',),audit='decision_id')
table('submission_snapshots','disaster_id@disasters barangay_id@barangays kind:enum=barangay_submission,system_fallback sender_id@actors? resolution_evidence_id@evidence_versions? fallback_reason:enum=no_eligible_endorser,no_barangay_response,no_barangay_submission? fallback_details:json submitted_at:time',checks=("(kind='barangay_submission' AND sender_id IS NOT NULL AND resolution_evidence_id IS NOT NULL AND fallback_reason IS NULL) OR (kind='system_fallback' AND sender_id IS NULL AND resolution_evidence_id IS NULL AND fallback_reason IS NOT NULL)",),audit='snapshot_id')
table('snapshot_items','snapshot_id@submission_snapshots round_id@claim_rounds submission_id@claim_submissions registry_version_id@household_versions',pk=('snapshot_id','round_id'))
table('snapshot_response_refs','snapshot_id@submission_snapshots response_id@claim_responses',pk=('snapshot_id','response_id'))
table('amount_input_versions','disaster_id@disasters predecessor_id@amount_input_versions? mode:enum=wage_formula,fixed_category wage_centavos:bigint? reason:text?',parent='disaster_id',checks=("(mode='wage_formula' AND wage_centavos>0) OR (mode='fixed_category' AND wage_centavos IS NULL)",),audit='input_version_id')
table('amount_rules','input_version_id@amount_input_versions category_id@damage_categories day_count:int? fixed_centavos:bigint?',unique=(('input_version_id','category_id'),),checks=('(day_count>0 AND fixed_centavos IS NULL) OR (day_count IS NULL AND fixed_centavos>0)',))
table('entitlements','claim_id@claims household_id@households disaster_id@disasters current_version_id@entitlement_versions business_status:enum=awaiting_amount,awaiting_publication,available,in_transaction,held,handed_over,cancelled hold_reasons:strings revision:int',mutable=True,unique=(('claim_id',),('household_id','disaster_id')))
table('entitlement_versions','entitlement_id@entitlements predecessor_id@entitlement_versions? decision_id@claim_decisions registry_version_id@household_versions registry_review_id@registry_reviews? category_id@damage_categories input_version_id@amount_input_versions? amount_centavos:bigint? calculation:json',parent='entitlement_id',checks=('(amount_centavos IS NULL AND input_version_id IS NULL) OR (amount_centavos>0 AND input_version_id IS NOT NULL)',),audit='entitlement_version_id')
table('paid_difference_events','handover_id@recorded_handovers new_input_version_id@amount_input_versions? new_decision_id@claim_decisions? hypothetical_centavos:bigint locked_centavos:bigint delta_centavos:bigint',checks=('num_nonnulls(new_input_version_id,new_decision_id)>0','delta_centavos=hypothetical_centavos-locked_centavos'))
table('list_heads','disaster_id@disasters barangay_id@barangays eligibility_revision:int newest_requested_id@approved_list_versions? current_published_id@approved_list_versions?',mutable=True,unique=(('disaster_id','barangay_id'),))
table('approved_list_versions','list_head_id@list_heads predecessor_published_id@approved_list_versions? based_on_revision:int basis_input_version_id@amount_input_versions requested_at:time business_status:enum=pending_publication,published,historical,stale published_at:time?',mutable=True,audit='list_version_id')
table('approved_list_entries','list_version_id@approved_list_versions entitlement_id@entitlements entitlement_version_id@entitlement_versions submission_id@claim_submissions display_decision_id@claim_decisions registry_version_id@household_versions registry_review_id@registry_reviews? frozen_name:text frozen_zone:text display_category_id@damage_categories',unique=(('list_version_id','entitlement_id'),))
table('payout_sessions','disaster_id@disasters barangay_id@barangays current_version_id@session_versions business_status:enum=scheduled,open,closed,cancelled revision:int',mutable=True)
table('session_versions','session_id@payout_sessions predecessor_id@session_versions? action:enum=schedule,open,close,cancel,amend,followup_assign date:date site:text original_list_version_id@approved_list_versions reason:text?',parent='session_id',audit='session_version_id')
table('session_assignments','session_version_id@session_versions actor_id@actors assignment_kind:enum=cash,followup',unique=(('session_version_id','actor_id','assignment_kind'),))
table('session_entries','session_version_id@session_versions list_entry_id@approved_list_entries entitlement_id@entitlements entitlement_version_id@entitlement_versions',unique=(('session_version_id','entitlement_id'),))
table('active_session_memberships','entitlement_id@entitlements session_id@payout_sessions session_entry_id@session_entries entitlement_version_id@entitlement_versions',mutable=True,pk=('entitlement_id',))
table('payout_transactions','entitlement_id@entitlements current_attempt_id@payout_attempts? current_outcome_id@outcome_versions? revision:int',mutable=True,unique=(('entitlement_id',),))
table('payout_attempts','transaction_id@payout_transactions attempt_number:int session_entry_id@session_entries entitlement_version_id@entitlement_versions path:enum=own_device,assisted recipient_actor_id@actors opened_at:time expires_at:time business_status:enum=open,presented,stopped,expired,handed_over current_id_check_id@identity_checks? bad_code_count:int',mutable=True,unique=(('transaction_id','attempt_number'),),checks=('bad_code_count>=0','attempt_number>0'))
Index('uq_active_attempt',metadata.tables['payout_attempts'].c.transaction_id,unique=True,postgresql_where=text("business_status IN ('open','presented')"))
table('attempt_events','attempt_id@payout_attempts action:enum=open,present,stop,expire,handover identity_check_id@identity_checks? reason:text?',checks=("action NOT IN ('stop','expire') OR length(reason)>0",),audit='attempt_event_id')
table('identity_checks','session_id@payout_sessions household_version_id@household_versions checked_by@actors result:enum=pass,fail accepted_id_type:text? person_photo_compared:bool reason:text?',checks=("(result='pass' AND person_photo_compared AND accepted_id_type IS NOT NULL) OR (result='fail' AND length(reason)>0)",))
table('payout_codes','attempt_id@payout_attempts salt:bytes digest:bytes algorithm:text expires_at:time consumed_at:time?',mutable=True,pk=('attempt_id',),checks=('octet_length(salt)=32','octet_length(digest)=32'))
table('assisted_pins','household_id@households established_after_check_id@identity_checks salt:bytes digest:bytes algorithm:text',checks=('octet_length(salt)=32','octet_length(digest)=32'))
table('credential_counters','pin_id@assisted_pins failed_count:int window_start:time? locked_until:time?',mutable=True,pk=('pin_id',),checks=('failed_count>=0',))
table('transaction_clearances','transaction_id@payout_transactions stopped_attempt_id@payout_attempts reason:text cleared_at:time',unique=(('stopped_attempt_id',),))
table('recorded_handovers','transaction_id@payout_transactions entitlement_id@entitlements attempt_id@payout_attempts entitlement_version_id@entitlement_versions input_version_id@amount_input_versions session_entry_id@session_entries current_session_entry_id@session_entries session_version_id@session_versions current_list_entry_id@approved_list_entries identity_check_id@identity_checks payer_id@actors recipient_actor_id@actors checker_assignment_id@session_assignments? path:enum=own_device,assisted amount_centavos:bigint handed_at:time authorization_result:json',unique=(('transaction_id',),('entitlement_id',),('attempt_id',)),checks=('amount_centavos>0',"(path='assisted' AND checker_assignment_id IS NOT NULL) OR (path='own_device' AND checker_assignment_id IS NULL)"),audit='handover_id')
table('transaction_notes','transaction_id@payout_transactions actor_id@actors note:text')
table('outcome_versions','transaction_id@payout_transactions handover_id@recorded_handovers predecessor_id@outcome_versions? answer:enum=received_full,received_less,not_received,unconfirmed recorder_actor_id@actors supplied_by_household:bool effective_at:time late:bool',parent='transaction_id',audit='outcome_version_id')
Index('uq_one_timeout',metadata.tables['outcome_versions'].c.transaction_id,unique=True,postgresql_where=text("answer='unconfirmed'"))
table('grievances','transaction_id@payout_transactions household_id@households business_status:enum=open,under_review,closed revision:int',mutable=True,unique=(('transaction_id',),))
table('grievance_events','grievance_id@grievances predecessor_id@grievance_events? kind:enum=open,report,review,note,resolve,reopen outcome_version_id@outcome_versions? report_text:text? resolution:text?',parent='grievance_id',checks=("kind!='resolve' OR length(resolution)>0",),audit='grievance_event_id')
table('list_challenges','list_entry_id@approved_list_entries reporting_household_id@households business_status:enum=open,under_review,closed revision:int',mutable=True)
table('challenge_events','challenge_id@list_challenges predecessor_id@challenge_events? action:enum=report,review,substantiate,dismiss,note reason:text decision_id@claim_decisions?',parent='challenge_id',audit='challenge_event_id')
table('fund_entries','disaster_id@disasters kind:enum=release,reversal,replacement delta_centavos:bigint source_root_id@fund_entries original_entry_id@fund_entries? correction_set_id@fund_correction_sets? document_type:text reference_number:text issued_date:date purpose:text covered_area:text extracted_fields:json? confirmed_fields:json amount_review:json entered_by@actors approved_by@actors?',checks=("(kind='release' AND delta_centavos>0 AND original_entry_id IS NULL AND correction_set_id IS NULL AND source_root_id=id) OR (kind='reversal' AND delta_centavos<0 AND original_entry_id IS NOT NULL AND correction_set_id IS NOT NULL) OR (kind='replacement' AND delta_centavos>0 AND original_entry_id IS NOT NULL AND correction_set_id IS NOT NULL)",'approved_by IS NULL'),audit='fund_entry_id')
table('fund_correction_sets','original_entry_id@fund_entries reversal_entry_id@fund_entries replacement_entry_id@fund_entries correction_kind:enum=transcription,source_amendment reason:text',unique=(('original_entry_id',),('reversal_entry_id',),('replacement_entry_id',)),audit='correction_set_id')
table('fund_heads','source_root_id@fund_entries current_entry_id@fund_entries revision:int',mutable=True,pk=('source_root_id',),unique=(('current_entry_id',),))
table('fund_signatories','entry_id@fund_entries ordinal:int printed_name:text printed_role:text signature_state:enum=not_validated,validated validation_evidence_id@evidence_versions?',pk=('entry_id','ordinal'),checks=('ordinal>=0',"signature_state='not_validated' OR validation_evidence_id IS NOT NULL"))
table('fund_area_lines','entry_id@fund_entries ordinal:int area_code:text area_name:text amount_centavos:bigint',pk=('entry_id','ordinal'),checks=('ordinal>=0','amount_centavos>=0'))
table('release_document_uses','byte_sha256:bytes source_root_id@fund_entries evidence_version_id@evidence_versions role:enum=primary,supporting',pk=('run_id','byte_sha256'),checks=('octet_length(byte_sha256)=32',))
table('evidence_versions','predecessor_id@evidence_versions? uploaded_by@actors prepared_for_actor_id@actors? purpose:enum=nomination,operation_basis,identity_photo,identity_document,field_check,damage,council_resolution,wage,days,fixed_amount,release_source,supporting,amended_source,private_report,clearance mime_type:enum=application/pdf,image/png,image/jpeg byte_length:bigint byte_sha256:bytes storage_key:text storage_version:text? uploaded_at:time extraction_state:enum=extracted,manual_required,failed extraction_version:text? extracted_fields:json? signature_state:enum=not_validated,validated',unique=(('storage_key',),),checks=('byte_length>0 AND byte_length<=10485760','octet_length(byte_sha256)=32',"signature_state='not_validated'"),audit='evidence_version_id')

EVIDENCE_OWNERS = {'nomination_id':'nominations','operation_version_id':'operation_versions','household_version_id':'household_versions','registry_review_id':'registry_reviews','submission_id':'claim_submissions','response_id':'claim_responses','snapshot_id':'submission_snapshots','input_version_id':'amount_input_versions','amount_rule_id':'amount_rules','fund_entry_id':'fund_entries','clearance_id':'transaction_clearances','grievance_event_id':'grievance_events','challenge_event_id':'challenge_events'}
TARGETS = dict((slot, name) for name,slot in AUDITED.items()) | {'anchor_job_id':'anchor_jobs','notification_id':'notifications','evaluation_run_id':'evaluation_runs'}
PROOF_OWNERS = {'evidence_version_id':'evidence_versions','fund_entry_id':'fund_entries','input_version_id':'amount_input_versions','snapshot_id':'submission_snapshots','list_version_id':'approved_list_versions','handover_id':'recorded_handovers','outcome_version_id':'outcome_versions'}


def arc(name, fields, owners, **kw):
    t=table(name,fields+' '+ ' '.join(k+'@'+v+'?' for k,v in owners.items()),
            checks=(*kw.pop('checks',()), 'num_nonnulls('+','.join(owners)+')=1'), **kw)
    dedup={'evidence_links':('evidence_version_id','attachment_role','input_field'),
           'audit_targets':('audit_event_id',),'auditor_access_targets':('access_event_id',),
           'command_result_refs':('actor_id','command_name','idempotency_key'),
           'notifications':('household_id','purpose','channel')}.get(name)
    if dedup:
        for owner in owners:
            Index('uq_'+name+'_'+owner,*(t.c[k] for k in (*dedup,owner)),unique=True,
                  postgresql_where=t.c[owner].is_not(None),postgresql_nulls_not_distinct=True)
    return t


arc('evidence_links','evidence_version_id@evidence_versions attachment_role:text input_field:text?',EVIDENCE_OWNERS)
table('deployments','protocol:enum=ayudachain.evidence.v1,legacy.receipt.v1 chain_id:numeric address:bytes deployment_uid:bytes? genesis_hash:bytes deploy_block_number:bigint deploy_block_hash:bytes runtime_code_hash:bytes abi_reference:text confirmation_policy:text state:enum=active,retired,lost',mutable=True,checks=('octet_length(address)=20','octet_length(genesis_hash)=32','octet_length(deploy_block_hash)=32','octet_length(runtime_code_hash)=32'),unique=(('chain_id','address','deploy_block_hash'),))
arc('commitments','public_id:bytes protocol:text kind:enum=document,amount_input,barangay_submission,system_fallback,approved_list,handover,outcome,fund_release,fund_reversal,fund_replacement predecessor_commitment_id@commitments? public_context:bytes public_related:bytes? canonical_bytes:bytes content_hash:bytes private_nonce:bytes deployment_id@deployments',PROOF_OWNERS,unique=(('public_id',),*[(k,) for k in PROOF_OWNERS]),checks=('octet_length(public_id)=32','octet_length(content_hash)=32','octet_length(private_nonce)=32','octet_length(public_context)=32'))
table('anchor_jobs','deployment_id@deployments operation:enum=anchor_record,fund_release,fund_correction state:enum=pending,prepared,submitted,uncertain,retry_wait,mined_unapplied,confirmed,conflict,deployment_lost next_attempt_at:time lease_owner:text? lease_until:time? last_error_code:text?',mutable=True)
table('anchor_job_items','commitment_id@commitments job_id@anchor_jobs ordinal:int',pk=('commitment_id',),unique=(('job_id','ordinal'),),checks=('ordinal>=0',))
table('anchor_dependencies','job_id@anchor_jobs prerequisite_job_id@anchor_jobs',pk=('job_id','prerequisite_job_id'),checks=('job_id!=prerequisite_job_id',))
table('anchor_submissions','job_id@anchor_jobs attempt_number:int signer_address:bytes nonce:numeric raw_signed_tx:bytes candidate_tx_hash:bytes prepared_at:time',unique=(('job_id','attempt_number'),),checks=('octet_length(signer_address)=20','octet_length(candidate_tx_hash)=32','nonce>=0','attempt_number>0'))
table('anchor_submission_events','job_id@anchor_jobs submission_id@anchor_submissions? action:text observed_tx_hash:bytes? receipt_status:int? block_number:bigint? block_hash:bytes? gas_used:numeric? gas_price:numeric? log_index:int? error_code:text? safe_details:json observed_at:time')
table('anchor_observations','job_id@anchor_jobs submission_id@anchor_submissions? verdict:enum=mined_match,transport_failure,reverted,conflict,deployment_lost observed_tx_hash:bytes? receipt_json:json? chain_record_json:json? checked_at:time')
table('anchor_applications','observation_id@anchor_observations audit_event_id@audit_events applied_at:time',pk=('observation_id',))
table('audit_events','sequence:bigint actor_id@actors action:text request_id:uuid reason:text? effective_at:time safe_details:json',audit=None,unique=(('sequence',),))
arc('audit_targets','audit_event_id@audit_events',TARGETS)
ACCESS_TARGETS = TARGETS | {'household_id':'households','claim_id':'claims','transaction_id':'payout_transactions','commitment_id':'commitments','disaster_id':'disasters'}
table('auditor_access_events','auditor_actor_id@actors action:enum=browse,open,file,identity,integrity,material fields_opened:strings success:bool checked_at:time integrity_result:text? safe_error:text?')
arc('auditor_access_targets','access_event_id@auditor_access_events',ACCESS_TARGETS)
NOTICE_SOURCES = {'session_version_id':'session_versions','entitlement_version_id':'entitlement_versions','decision_id':'claim_decisions','operation_version_id':'operation_versions'}
arc('notifications','household_id@households link_version_id@household_link_versions? purpose:text channel:enum=in_app,simulated_notice_sms content:json simulated:bool state:enum=pending,delivered,failed,no_contact',NOTICE_SOURCES,mutable=True)
table('notification_attempts','notification_id@notifications attempt_number:int adapter:text simulated:bool result:enum=delivered,failed,no_contact safe_failure:text? attempted_at:time',unique=(('notification_id','attempt_number'),))
table('command_results','actor_id@actors command_name:text idempotency_key:text request_digest:bytes status_code:int',pk=('actor_id','command_name','idempotency_key'),checks=('octet_length(request_digest)=32',))
arc('command_result_refs','actor_id@actors command_name:text idempotency_key:text',ACCESS_TARGETS)
metadata.tables['command_result_refs'].append_constraint(ForeignKeyConstraint(['actor_id','command_name','idempotency_key'],['command_results.actor_id','command_results.command_name','command_results.idempotency_key'],deferrable=True,initially='DEFERRED'))
table('legacy_records','source_db_sha256:bytes source_table:enum=relief_batches,allocations,beneficiaries,distributions,audit_events source_key:text original_fields:json original_receipt_hash:bytes? deployment_id@deployments? imported_at:time',unique=(('source_db_sha256','source_table','source_key'),))

# Explicit same-parent links; nullable references retain their mandatory FK too.
def relation(source, columns, target, target_columns):
    t = metadata.tables[target]
    key = ('run_id','office_id',*target_columns)
    if not any(isinstance(c,UniqueConstraint) and tuple(x.name for x in c.columns)==key for c in t.constraints):
        t.append_constraint(UniqueConstraint(*key))
    metadata.tables[source].append_constraint(ForeignKeyConstraint(['run_id','office_id',*columns],[target+'.'+c for c in key],
                                                name='rel_'+source+'_'+'_'.join(columns),deferrable=True,initially='DEFERRED'))

for root,version,parent in [('actors','actor_versions','actor_id'),('households','household_versions','household_id'),('claim_operations','operation_versions','operation_id'),('claims','claim_submissions','claim_id'),('entitlements','entitlement_versions','entitlement_id'),('payout_sessions','session_versions','session_id')]:
    relation(root, ['id','current_version_id' if root!='claims' else 'current_submission_id'],version,[parent,'id'])
relation('household_links',['household_id','link_version_id'],'household_link_versions',['household_id','id'])
relation('household_links',['household_id','link_version_id','beneficiary_actor_id'],'household_link_versions',['household_id','id','beneficiary_actor_id'])
relation('claim_responses',['round_id','parent_response_id'],'claim_responses',['round_id','id'])
relation('snapshot_items',['submission_id','round_id'],'claim_rounds',['submission_id','id'])
relation('snapshot_items',['submission_id','registry_version_id'],'claim_submissions',['id','registry_version_id'])
relation('approved_list_entries',['entitlement_id','entitlement_version_id'],'entitlement_versions',['entitlement_id','id'])
relation('session_entries',['list_entry_id','entitlement_id','entitlement_version_id'],'approved_list_entries',['id','entitlement_id','entitlement_version_id'])
relation('active_session_memberships',['session_entry_id','entitlement_id','entitlement_version_id'],'session_entries',['id','entitlement_id','entitlement_version_id'])
relation('payout_attempts',['session_entry_id','entitlement_version_id'],'session_entries',['id','entitlement_version_id'])
relation('payout_transactions',['id','current_attempt_id'],'payout_attempts',['transaction_id','id'])
relation('payout_transactions',['id','current_outcome_id'],'outcome_versions',['transaction_id','id'])
relation('recorded_handovers',['transaction_id','attempt_id'],'payout_attempts',['transaction_id','id'])
relation('recorded_handovers',['entitlement_id','entitlement_version_id','amount_centavos','input_version_id'],'entitlement_versions',['entitlement_id','id','amount_centavos','input_version_id'])
relation('recorded_handovers',['session_entry_id','entitlement_id','entitlement_version_id'],'session_entries',['id','entitlement_id','entitlement_version_id'])
relation('recorded_handovers',['current_session_entry_id','session_version_id','entitlement_id','entitlement_version_id'],'session_entries',['id','session_version_id','entitlement_id','entitlement_version_id'])
relation('recorded_handovers',['current_list_entry_id','entitlement_id','entitlement_version_id'],'approved_list_entries',['id','entitlement_id','entitlement_version_id'])
relation('outcome_versions',['transaction_id','handover_id'],'recorded_handovers',['transaction_id','id'])
relation('grievance_events',['outcome_version_id'],'outcome_versions',['id'])
relation('claims',['id','current_decision_id'],'claim_decisions',['claim_id','id'])
relation('list_heads',['id','newest_requested_id'],'approved_list_versions',['list_head_id','id'])
relation('list_heads',['id','current_published_id'],'approved_list_versions',['list_head_id','id'])
relation('disasters',['id','current_input_version_id'],'amount_input_versions',['disaster_id','id'])
relation('households',['id','current_pin_id'],'assisted_pins',['household_id','id'])
relation('actors',['id','current_member_link_id'],'actor_member_links',['actor_id','id'])
relation('actor_versions',['actor_id','nomination_id'],'nominations',['candidate_actor_id','id'])
for name,condition in [
 ('amount_input_versions',"mode!='wage_formula' OR wage_centavos IS NOT NULL"),
 ('amount_rules','num_nonnulls(day_count,fixed_centavos)=1'),
 ('entitlement_versions','(amount_centavos IS NULL)=(input_version_id IS NULL)')]:
    metadata.tables[name].append_constraint(CheckConstraint(condition,name=name+'_required_pair'))
Index('uq_paid_difference_basis',metadata.tables['paid_difference_events'].c.handover_id,metadata.tables['paid_difference_events'].c.new_input_version_id,metadata.tables['paid_difference_events'].c.new_decision_id,unique=True,postgresql_nulls_not_distinct=True)

ROLE_OWNERS={
 'nomination_id':['nomination'],'operation_version_id':['operation_basis'],
 'household_version_id':['identity_photo','identity_document'],
 'registry_review_id':['field_check','identity_photo','identity_document'],
 'submission_id':['damage'],'response_id':['damage'],'snapshot_id':['council_resolution'],
 'input_version_id':['wage'],'amount_rule_id':['days','fixed_amount'],
 'fund_entry_id':['release_source','supporting','amended_source'],
 'clearance_id':['clearance'],'grievance_event_id':['private_report'],'challenge_event_id':['private_report']}
metadata.tables['evidence_links'].append_constraint(CheckConstraint(' OR '.join('('+k+' IS NOT NULL AND attachment_role IN ('+','.join("'"+r+"'" for r in roles)+'))' for k,roles in ROLE_OWNERS.items()),name='evidence_link_owner_role'))
for t in metadata.tables.values():
    for col in t.c:
        if col.name.endswith('_centavos'):
            t.append_constraint(CheckConstraint(col.name+' BETWEEN -9000000000000000000 AND 9000000000000000000',name=t.name+'_'+col.name+'_range'))

# Immutable content with selected mutable projections, enforced by migration triggers.
FROZEN_PROJECTIONS = {
 'claim_rounds':{'state','route_kind','primary_snapshot_id','routed_response_id','revision'},
 'approved_list_versions':{'business_status','published_at'},
 'payout_attempts':{'business_status','current_id_check_id','bad_code_count'},
 'payout_codes':{'consumed_at'}, 'notifications':{'state'}, 'deployments':{'state'},
}

# SQLAlchemy's deterministic truncation preserves uniqueness for PostgreSQL's
# 63-byte identifier limit, including long explicit same-parent relations.
for typed_table in metadata.tables.values():
    for constraint in typed_table.constraints:
        if constraint.name: constraint.name = conv(constraint.name)
    for index in typed_table.indexes:
        index.name = conv(index.name)
