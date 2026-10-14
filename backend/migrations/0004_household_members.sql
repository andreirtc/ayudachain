CREATE FUNCTION validate_household_members() RETURNS trigger LANGUAGE plpgsql AS $$
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
    CREATE CONSTRAINT TRIGGER household_members_parent AFTER INSERT ON member_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION validate_household_members();
