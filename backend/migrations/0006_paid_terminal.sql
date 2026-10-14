CREATE FUNCTION preserve_paid_entitlement() RETURNS trigger LANGUAGE plpgsql AS $$
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
    CREATE TRIGGER preserve_paid_attempt BEFORE UPDATE ON payout_transactions FOR EACH ROW EXECUTE FUNCTION preserve_paid_attempt();
