ALTER TABLE paid_difference_events DROP CONSTRAINT IF EXISTS paid_difference_events_required_pair;
DROP INDEX IF EXISTS uq_paid_difference_new_input_version_id;
DROP INDEX IF EXISTS uq_paid_difference_new_decision_id;
CREATE UNIQUE INDEX IF NOT EXISTS uq_paid_difference_basis ON paid_difference_events(handover_id,new_input_version_id,new_decision_id) NULLS NOT DISTINCT;
