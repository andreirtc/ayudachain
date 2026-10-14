ALTER TABLE nominations ADD CONSTRAINT uq_nominations_run_id_office_id_candidate_actor_id_id UNIQUE (run_id, office_id, candidate_actor_id, id);
ALTER TABLE amount_input_versions ADD CONSTRAINT amount_input_versions_required_pair CHECK (mode!='wage_formula' OR wage_centavos IS NOT NULL);
ALTER TABLE amount_rules ADD CONSTRAINT amount_rules_required_pair CHECK (num_nonnulls(day_count,fixed_centavos)=1);
ALTER TABLE entitlement_versions ADD CONSTRAINT entitlement_versions_required_pair CHECK ((amount_centavos IS NULL)=(input_version_id IS NULL));
CREATE UNIQUE INDEX uq_paid_difference_basis ON paid_difference_events (handover_id, new_input_version_id, new_decision_id) NULLS NOT DISTINCT;
ALTER TABLE actors ADD CONSTRAINT rel_actors_id_current_member_link_id FOREIGN KEY(run_id, office_id, id, current_member_link_id) REFERENCES actor_member_links (run_id, office_id, actor_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT rel_actor_versions_actor_id_nomination_id FOREIGN KEY(run_id, office_id, actor_id, nomination_id) REFERENCES nominations (run_id, office_id, candidate_actor_id, id) DEFERRABLE INITIALLY DEFERRED;
