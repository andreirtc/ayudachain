
CREATE TABLE field_offices (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	name TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	check_data_revision INTEGER NOT NULL, 
	CONSTRAINT pk_field_offices PRIMARY KEY (id), 
	CONSTRAINT field_offices_check_0 CHECK (revision>=0), 
	CONSTRAINT field_offices_check_1 CHECK (check_data_revision>=0)
)

;

CREATE TABLE barangays (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	name TEXT NOT NULL, 
	zone_description TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_barangays PRIMARY KEY (id), 
	CONSTRAINT uq_barangays_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE disasters (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	name TEXT NOT NULL, 
	external_reference TEXT, 
	current_input_version_id UUID, 
	inputs_locked_at TIMESTAMP WITH TIME ZONE, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_disasters PRIMARY KEY (id), 
	CONSTRAINT uq_disasters_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE actors (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	role TEXT NOT NULL, 
	display_name TEXT NOT NULL, 
	email TEXT, 
	current_version_id UUID NOT NULL, 
	current_member_link_id UUID, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_actors PRIMARY KEY (id), 
	CONSTRAINT actors_role_enum CHECK (role IN ('dswd','barangay','beneficiary','disbursing','auditor','system')), 
	CONSTRAINT uq_actors_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE actor_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	actor_id UUID NOT NULL, 
	predecessor_id UUID, 
	status TEXT NOT NULL, 
	barangay_id UUID, 
	position TEXT, 
	nomination_id UUID, 
	approved_by UUID, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_actor_versions PRIMARY KEY (id), 
	CONSTRAINT actor_versions_status_enum CHECK (status IN ('pending','active','deactivated')), 
	CONSTRAINT uq_actor_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_actor_versions_run_id_office_id_actor_id_id UNIQUE (run_id, office_id, actor_id, id)
)

;

CREATE TABLE nominations (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	candidate_actor_id UUID NOT NULL, 
	barangay_id UUID NOT NULL, 
	position TEXT NOT NULL, 
	nominator_name TEXT NOT NULL, 
	entered_by UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_nominations PRIMARY KEY (id), 
	CONSTRAINT uq_nominations_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_nominations_run_id_office_id_candidate_actor_id_id UNIQUE (run_id, office_id, candidate_actor_id, id)
)

;

CREATE TABLE households (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	display_id TEXT NOT NULL, 
	current_version_id UUID NOT NULL, 
	current_pin_id UUID, 
	registered_without_id BOOLEAN NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_households PRIMARY KEY (id), 
	CONSTRAINT households_check_0 CHECK (display_id ~ '^DFC-2026-[A-Z0-9]{4,}$'), 
	CONSTRAINT uq_households_run_id_display_id UNIQUE (run_id, display_id), 
	CONSTRAINT uq_households_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE household_members (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_household_members PRIMARY KEY (id), 
	CONSTRAINT uq_household_members_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE household_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	predecessor_id UUID, 
	declared_barangay_id UUID NOT NULL, 
	address TEXT NOT NULL, 
	zone TEXT NOT NULL, 
	residence_state TEXT NOT NULL, 
	identity_state TEXT NOT NULL, 
	id_type TEXT, 
	id_number TEXT, 
	head_photo_evidence_id UUID, 
	id_evidence_id UUID, 
	assister_id UUID, 
	registry_review_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_household_versions PRIMARY KEY (id), 
	CONSTRAINT household_versions_residence_state_enum CHECK (residence_state IN ('unconfirmed','confirmed','disputed')), 
	CONSTRAINT household_versions_identity_state_enum CHECK (identity_state IN ('evidence_recorded','pending_field_check','field_checked_with_photo_id')), 
	CONSTRAINT uq_household_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_household_versions_run_id_office_id_household_id_id UNIQUE (run_id, office_id, household_id, id)
)

;

CREATE TABLE household_link_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	predecessor_id UUID, 
	beneficiary_actor_id UUID, 
	phone TEXT, 
	basis_review_id UUID, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_household_link_versions PRIMARY KEY (id), 
	CONSTRAINT uq_household_link_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_household_link_versions_run_id_office_id_household_id_id UNIQUE (run_id, office_id, household_id, id), 
	CONSTRAINT uq_household_link_versions_run_id_office_id_household_i_e117 UNIQUE (run_id, office_id, household_id, id, beneficiary_actor_id)
)

;

CREATE TABLE actor_member_links (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	actor_id UUID NOT NULL, 
	member_id UUID NOT NULL, 
	predecessor_id UUID, 
	basis_review_id UUID, 
	reason TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_actor_member_links PRIMARY KEY (id), 
	CONSTRAINT uq_actor_member_links_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_actor_member_links_run_id_office_id_actor_id_id UNIQUE (run_id, office_id, actor_id, id)
)

;

CREATE TABLE registry_reviews (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	prior_version_id UUID, 
	result_version_id UUID, 
	action TEXT NOT NULL, 
	reason TEXT NOT NULL, 
	accepted_id_type TEXT, 
	person_photo_compared BOOLEAN, 
	prior_link_id UUID, 
	result_link_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_registry_reviews PRIMARY KEY (id), 
	CONSTRAINT registry_reviews_action_enum CHECK (action IN ('residence_confirm','residence_dispute','residence_resolve','field_check','facts_correct','contact_relink','id_check')), 
	CONSTRAINT uq_registry_reviews_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE claim_operations (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	current_version_id UUID NOT NULL, 
	business_status TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_claim_operations PRIMARY KEY (id), 
	CONSTRAINT claim_operations_business_status_enum CHECK (business_status IN ('not_open','open','closed')), 
	CONSTRAINT uq_claim_operations_disaster_id UNIQUE (disaster_id), 
	CONSTRAINT uq_claim_operations_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE operation_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	operation_id UUID NOT NULL, 
	predecessor_id UUID, 
	action TEXT NOT NULL, 
	response_hours INTEGER NOT NULL, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_operation_versions PRIMARY KEY (id), 
	CONSTRAINT operation_versions_action_enum CHECK (action IN ('open','close')), 
	CONSTRAINT operation_versions_check_0 CHECK (response_hours>0), 
	CONSTRAINT uq_operation_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_operation_versions_run_id_office_id_operation_id_id UNIQUE (run_id, office_id, operation_id, id)
)

;

CREATE TABLE claims (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	operation_id UUID NOT NULL, 
	current_submission_id UUID NOT NULL, 
	current_decision_id UUID, 
	business_status TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	resubmissions INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_claims PRIMARY KEY (id), 
	CONSTRAINT claims_business_status_enum CHECK (business_status IN ('waiting_barangay','awaiting_dswd','referred','approved','declined','reversed')), 
	CONSTRAINT claims_check_0 CHECK (resubmissions BETWEEN 0 AND 1), 
	CONSTRAINT uq_claims_household_id_disaster_id UNIQUE (household_id, disaster_id), 
	CONSTRAINT uq_claims_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE claim_submissions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	claim_id UUID NOT NULL, 
	registry_version_id UUID NOT NULL, 
	link_version_id UUID, 
	predecessor_id UUID, 
	stated_category_id UUID NOT NULL, 
	damage_description TEXT NOT NULL, 
	new_information TEXT, 
	submitted_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_claim_submissions PRIMARY KEY (id), 
	CONSTRAINT uq_claim_submissions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_claim_submissions_run_id_office_id_claim_id_id UNIQUE (run_id, office_id, claim_id, id), 
	CONSTRAINT uq_claim_submissions_run_id_office_id_id_registry_version_id UNIQUE (run_id, office_id, id, registry_version_id)
)

;

CREATE TABLE claim_rounds (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	submission_id UUID NOT NULL, 
	referral_decision_id UUID, 
	response_hours INTEGER NOT NULL, 
	deadline_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	state TEXT NOT NULL, 
	route_kind TEXT, 
	primary_snapshot_id UUID, 
	routed_response_id UUID, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_claim_rounds PRIMARY KEY (id), 
	CONSTRAINT claim_rounds_state_enum CHECK (state IN ('waiting','routed','closed')), 
	CONSTRAINT claim_rounds_route_kind_enum CHECK (route_kind IN ('barangay_submission','system_fallback','referral_answer','referral_timeout')), 
	CONSTRAINT claim_rounds_check_0 CHECK (response_hours>0), 
	CONSTRAINT uq_claim_rounds_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_claim_rounds_run_id_office_id_submission_id_id UNIQUE (run_id, office_id, submission_id, id)
)

;

CREATE TABLE claim_responses (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	round_id UUID NOT NULL, 
	parent_response_id UUID, 
	actor_id UUID NOT NULL, 
	kind TEXT NOT NULL, 
	residence_attested BOOLEAN, 
	affected_attested BOOLEAN, 
	category_opinion_id UUID, 
	category_disputed BOOLEAN NOT NULL, 
	related_declared BOOLEAN NOT NULL, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_claim_responses PRIMARY KEY (id), 
	CONSTRAINT claim_responses_kind_enum CHECK (kind IN ('endorse','not_endorse','withdraw','reverse','referral_answer')), 
	CONSTRAINT uq_claim_responses_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_claim_responses_run_id_office_id_round_id_id UNIQUE (run_id, office_id, round_id, id)
)

;

CREATE TABLE check_runs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	submission_id UUID NOT NULL, 
	round_id UUID NOT NULL, 
	purpose TEXT NOT NULL, 
	algorithm_version TEXT NOT NULL, 
	compared_data_revision INTEGER NOT NULL, 
	risk_score INTEGER NOT NULL, 
	simulation_adapter TEXT NOT NULL, 
	simulation_result JSONB NOT NULL, 
	simulated BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_check_runs PRIMARY KEY (id), 
	CONSTRAINT check_runs_purpose_enum CHECK (purpose IN ('intake','review','recheck','duplicate_attempt')), 
	CONSTRAINT check_runs_check_0 CHECK (simulated), 
	CONSTRAINT check_runs_check_1 CHECK (risk_score>=0), 
	CONSTRAINT uq_check_runs_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE claim_decisions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	claim_id UUID NOT NULL, 
	submission_id UUID NOT NULL, 
	round_id UUID NOT NULL, 
	predecessor_id UUID, 
	check_run_id UUID NOT NULL, 
	action TEXT NOT NULL, 
	category_id UUID, 
	reason TEXT, 
	question TEXT, 
	confirmed_by UUID, 
	bulk_group_id UUID, 
	challenge_event_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_claim_decisions PRIMARY KEY (id), 
	CONSTRAINT claim_decisions_action_enum CHECK (action IN ('approve','decline','refer','category_change','reverse_approval')), 
	CONSTRAINT claim_decisions_check_0 CHECK (confirmed_by IS NULL), 
	CONSTRAINT uq_claim_decisions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_claim_decisions_run_id_office_id_claim_id_id UNIQUE (run_id, office_id, claim_id, id)
)

;

CREATE TABLE amount_input_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	predecessor_id UUID, 
	mode TEXT NOT NULL, 
	wage_centavos BIGINT, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_amount_input_versions PRIMARY KEY (id), 
	CONSTRAINT amount_input_versions_mode_enum CHECK (mode IN ('wage_formula','fixed_category')), 
	CONSTRAINT amount_input_versions_check_0 CHECK ((mode='wage_formula' AND wage_centavos>0) OR (mode='fixed_category' AND wage_centavos IS NULL)), 
	CONSTRAINT uq_amount_input_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_amount_input_versions_run_id_office_id_disaster_id_id UNIQUE (run_id, office_id, disaster_id, id), 
	CONSTRAINT amount_input_versions_required_pair CHECK (mode!='wage_formula' OR wage_centavos IS NOT NULL), 
	CONSTRAINT amount_input_versions_wage_centavos_range CHECK (wage_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE entitlements (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	claim_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	current_version_id UUID NOT NULL, 
	business_status TEXT NOT NULL, 
	hold_reasons TEXT[] NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_entitlements PRIMARY KEY (id), 
	CONSTRAINT entitlements_business_status_enum CHECK (business_status IN ('awaiting_amount','awaiting_publication','available','in_transaction','held','handed_over','cancelled')), 
	CONSTRAINT uq_entitlements_claim_id UNIQUE (claim_id), 
	CONSTRAINT uq_entitlements_household_id_disaster_id UNIQUE (household_id, disaster_id), 
	CONSTRAINT uq_entitlements_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE entitlement_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	entitlement_id UUID NOT NULL, 
	predecessor_id UUID, 
	decision_id UUID NOT NULL, 
	registry_version_id UUID NOT NULL, 
	registry_review_id UUID, 
	category_id UUID NOT NULL, 
	input_version_id UUID, 
	amount_centavos BIGINT, 
	calculation JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_entitlement_versions PRIMARY KEY (id), 
	CONSTRAINT entitlement_versions_check_0 CHECK ((amount_centavos IS NULL AND input_version_id IS NULL) OR (amount_centavos>0 AND input_version_id IS NOT NULL)), 
	CONSTRAINT uq_entitlement_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_entitlement_versions_run_id_office_id_entitlement_id_id UNIQUE (run_id, office_id, entitlement_id, id), 
	CONSTRAINT uq_entitlement_versions_run_id_office_id_entitlement_id_41a5 UNIQUE (run_id, office_id, entitlement_id, id, amount_centavos, input_version_id), 
	CONSTRAINT entitlement_versions_required_pair CHECK ((amount_centavos IS NULL)=(input_version_id IS NULL)), 
	CONSTRAINT entitlement_versions_amount_centavos_range CHECK (amount_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE list_heads (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	barangay_id UUID NOT NULL, 
	eligibility_revision INTEGER NOT NULL, 
	newest_requested_id UUID, 
	current_published_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_list_heads PRIMARY KEY (id), 
	CONSTRAINT uq_list_heads_disaster_id_barangay_id UNIQUE (disaster_id, barangay_id), 
	CONSTRAINT uq_list_heads_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE approved_list_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	list_head_id UUID NOT NULL, 
	predecessor_published_id UUID, 
	based_on_revision INTEGER NOT NULL, 
	basis_input_version_id UUID NOT NULL, 
	requested_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	business_status TEXT NOT NULL, 
	published_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_approved_list_versions PRIMARY KEY (id), 
	CONSTRAINT approved_list_versions_business_status_enum CHECK (business_status IN ('pending_publication','published','historical','stale')), 
	CONSTRAINT uq_approved_list_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_approved_list_versions_run_id_office_id_list_head_id_id UNIQUE (run_id, office_id, list_head_id, id)
)

;

CREATE TABLE approved_list_entries (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	list_version_id UUID NOT NULL, 
	entitlement_id UUID NOT NULL, 
	entitlement_version_id UUID NOT NULL, 
	submission_id UUID NOT NULL, 
	display_decision_id UUID NOT NULL, 
	registry_version_id UUID NOT NULL, 
	registry_review_id UUID, 
	frozen_name TEXT NOT NULL, 
	frozen_zone TEXT NOT NULL, 
	display_category_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_approved_list_entries PRIMARY KEY (id), 
	CONSTRAINT uq_approved_list_entries_list_version_id_entitlement_id UNIQUE (list_version_id, entitlement_id), 
	CONSTRAINT uq_approved_list_entries_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_approved_list_entries_run_id_office_id_id_entitlemen_1ca6 UNIQUE (run_id, office_id, id, entitlement_id, entitlement_version_id)
)

;

CREATE TABLE payout_sessions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	barangay_id UUID NOT NULL, 
	current_version_id UUID NOT NULL, 
	business_status TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_payout_sessions PRIMARY KEY (id), 
	CONSTRAINT payout_sessions_business_status_enum CHECK (business_status IN ('scheduled','open','closed','cancelled')), 
	CONSTRAINT uq_payout_sessions_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE session_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	session_id UUID NOT NULL, 
	predecessor_id UUID, 
	action TEXT NOT NULL, 
	date DATE NOT NULL, 
	site TEXT NOT NULL, 
	original_list_version_id UUID NOT NULL, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_session_versions PRIMARY KEY (id), 
	CONSTRAINT session_versions_action_enum CHECK (action IN ('schedule','open','close','cancel','amend','followup_assign')), 
	CONSTRAINT uq_session_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_session_versions_run_id_office_id_session_id_id UNIQUE (run_id, office_id, session_id, id)
)

;

CREATE TABLE payout_transactions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	entitlement_id UUID NOT NULL, 
	current_attempt_id UUID, 
	current_outcome_id UUID, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_payout_transactions PRIMARY KEY (id), 
	CONSTRAINT uq_payout_transactions_entitlement_id UNIQUE (entitlement_id), 
	CONSTRAINT uq_payout_transactions_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE payout_attempts (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	transaction_id UUID NOT NULL, 
	attempt_number INTEGER NOT NULL, 
	session_entry_id UUID NOT NULL, 
	entitlement_version_id UUID NOT NULL, 
	path TEXT NOT NULL, 
	recipient_actor_id UUID NOT NULL, 
	opened_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	business_status TEXT NOT NULL, 
	current_id_check_id UUID, 
	bad_code_count INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_payout_attempts PRIMARY KEY (id), 
	CONSTRAINT payout_attempts_path_enum CHECK (path IN ('own_device','assisted')), 
	CONSTRAINT payout_attempts_business_status_enum CHECK (business_status IN ('open','presented','stopped','expired','handed_over')), 
	CONSTRAINT payout_attempts_check_0 CHECK (bad_code_count>=0), 
	CONSTRAINT payout_attempts_check_1 CHECK (attempt_number>0), 
	CONSTRAINT uq_payout_attempts_transaction_id_attempt_number UNIQUE (transaction_id, attempt_number), 
	CONSTRAINT uq_payout_attempts_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_payout_attempts_run_id_office_id_transaction_id_id UNIQUE (run_id, office_id, transaction_id, id)
)

;

CREATE TABLE identity_checks (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	session_id UUID NOT NULL, 
	household_version_id UUID NOT NULL, 
	checked_by UUID NOT NULL, 
	result TEXT NOT NULL, 
	accepted_id_type TEXT, 
	person_photo_compared BOOLEAN NOT NULL, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_identity_checks PRIMARY KEY (id), 
	CONSTRAINT identity_checks_result_enum CHECK (result IN ('pass','fail')), 
	CONSTRAINT identity_checks_check_0 CHECK ((result='pass' AND person_photo_compared AND accepted_id_type IS NOT NULL) OR (result='fail' AND length(reason)>0)), 
	CONSTRAINT uq_identity_checks_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE assisted_pins (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	established_after_check_id UUID NOT NULL, 
	salt BYTEA NOT NULL, 
	digest BYTEA NOT NULL, 
	algorithm TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_assisted_pins PRIMARY KEY (id), 
	CONSTRAINT assisted_pins_check_0 CHECK (octet_length(salt)=32), 
	CONSTRAINT assisted_pins_check_1 CHECK (octet_length(digest)=32), 
	CONSTRAINT uq_assisted_pins_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_assisted_pins_run_id_office_id_household_id_id UNIQUE (run_id, office_id, household_id, id)
)

;

CREATE TABLE recorded_handovers (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	transaction_id UUID NOT NULL, 
	entitlement_id UUID NOT NULL, 
	attempt_id UUID NOT NULL, 
	entitlement_version_id UUID NOT NULL, 
	input_version_id UUID NOT NULL, 
	session_entry_id UUID NOT NULL, 
	current_session_entry_id UUID NOT NULL, 
	session_version_id UUID NOT NULL, 
	current_list_entry_id UUID NOT NULL, 
	identity_check_id UUID NOT NULL, 
	payer_id UUID NOT NULL, 
	recipient_actor_id UUID NOT NULL, 
	checker_assignment_id UUID, 
	path TEXT NOT NULL, 
	amount_centavos BIGINT NOT NULL, 
	handed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	authorization_result JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_recorded_handovers PRIMARY KEY (id), 
	CONSTRAINT recorded_handovers_path_enum CHECK (path IN ('own_device','assisted')), 
	CONSTRAINT recorded_handovers_check_0 CHECK (amount_centavos>0), 
	CONSTRAINT recorded_handovers_check_1 CHECK ((path='assisted' AND checker_assignment_id IS NOT NULL) OR (path='own_device' AND checker_assignment_id IS NULL)), 
	CONSTRAINT uq_recorded_handovers_transaction_id UNIQUE (transaction_id), 
	CONSTRAINT uq_recorded_handovers_entitlement_id UNIQUE (entitlement_id), 
	CONSTRAINT uq_recorded_handovers_attempt_id UNIQUE (attempt_id), 
	CONSTRAINT uq_recorded_handovers_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_recorded_handovers_run_id_office_id_transaction_id_id UNIQUE (run_id, office_id, transaction_id, id), 
	CONSTRAINT recorded_handovers_amount_centavos_range CHECK (amount_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE outcome_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	transaction_id UUID NOT NULL, 
	handover_id UUID NOT NULL, 
	predecessor_id UUID, 
	answer TEXT NOT NULL, 
	recorder_actor_id UUID NOT NULL, 
	supplied_by_household BOOLEAN NOT NULL, 
	effective_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	late BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_outcome_versions PRIMARY KEY (id), 
	CONSTRAINT outcome_versions_answer_enum CHECK (answer IN ('received_full','received_less','not_received','unconfirmed')), 
	CONSTRAINT uq_outcome_versions_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_outcome_versions_run_id_office_id_transaction_id_id UNIQUE (run_id, office_id, transaction_id, id)
)

;

CREATE TABLE list_challenges (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	list_entry_id UUID NOT NULL, 
	reporting_household_id UUID NOT NULL, 
	business_status TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_list_challenges PRIMARY KEY (id), 
	CONSTRAINT list_challenges_business_status_enum CHECK (business_status IN ('open','under_review','closed')), 
	CONSTRAINT uq_list_challenges_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE challenge_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	challenge_id UUID NOT NULL, 
	predecessor_id UUID, 
	action TEXT NOT NULL, 
	reason TEXT NOT NULL, 
	decision_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_challenge_events PRIMARY KEY (id), 
	CONSTRAINT challenge_events_action_enum CHECK (action IN ('report','review','substantiate','dismiss','note')), 
	CONSTRAINT uq_challenge_events_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_challenge_events_run_id_office_id_challenge_id_id UNIQUE (run_id, office_id, challenge_id, id)
)

;

CREATE TABLE fund_entries (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	kind TEXT NOT NULL, 
	delta_centavos BIGINT NOT NULL, 
	source_root_id UUID NOT NULL, 
	original_entry_id UUID, 
	correction_set_id UUID, 
	document_type TEXT NOT NULL, 
	reference_number TEXT NOT NULL, 
	issued_date DATE NOT NULL, 
	purpose TEXT NOT NULL, 
	covered_area TEXT NOT NULL, 
	extracted_fields JSONB, 
	confirmed_fields JSONB NOT NULL, 
	amount_review JSONB NOT NULL, 
	entered_by UUID NOT NULL, 
	approved_by UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_fund_entries PRIMARY KEY (id), 
	CONSTRAINT fund_entries_kind_enum CHECK (kind IN ('release','reversal','replacement')), 
	CONSTRAINT fund_entries_check_0 CHECK ((kind='release' AND delta_centavos>0 AND original_entry_id IS NULL AND correction_set_id IS NULL AND source_root_id=id) OR (kind='reversal' AND delta_centavos<0 AND original_entry_id IS NOT NULL AND correction_set_id IS NOT NULL) OR (kind='replacement' AND delta_centavos>0 AND original_entry_id IS NOT NULL AND correction_set_id IS NOT NULL)), 
	CONSTRAINT fund_entries_check_1 CHECK (approved_by IS NULL), 
	CONSTRAINT uq_fund_entries_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT fund_entries_delta_centavos_range CHECK (delta_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE fund_correction_sets (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	original_entry_id UUID NOT NULL, 
	reversal_entry_id UUID NOT NULL, 
	replacement_entry_id UUID NOT NULL, 
	correction_kind TEXT NOT NULL, 
	reason TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_fund_correction_sets PRIMARY KEY (id), 
	CONSTRAINT fund_correction_sets_correction_kind_enum CHECK (correction_kind IN ('transcription','source_amendment')), 
	CONSTRAINT uq_fund_correction_sets_original_entry_id UNIQUE (original_entry_id), 
	CONSTRAINT uq_fund_correction_sets_reversal_entry_id UNIQUE (reversal_entry_id), 
	CONSTRAINT uq_fund_correction_sets_replacement_entry_id UNIQUE (replacement_entry_id), 
	CONSTRAINT uq_fund_correction_sets_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE evidence_versions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	predecessor_id UUID, 
	uploaded_by UUID NOT NULL, 
	prepared_for_actor_id UUID, 
	purpose TEXT NOT NULL, 
	mime_type TEXT NOT NULL, 
	byte_length BIGINT NOT NULL, 
	byte_sha256 BYTEA NOT NULL, 
	storage_key TEXT NOT NULL, 
	storage_version TEXT, 
	uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	extraction_state TEXT NOT NULL, 
	extraction_version TEXT, 
	extracted_fields JSONB, 
	signature_state TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_evidence_versions PRIMARY KEY (id), 
	CONSTRAINT evidence_versions_purpose_enum CHECK (purpose IN ('nomination','operation_basis','identity_photo','identity_document','field_check','damage','council_resolution','wage','days','fixed_amount','release_source','supporting','amended_source','private_report','clearance')), 
	CONSTRAINT evidence_versions_mime_type_enum CHECK (mime_type IN ('application/pdf','image/png','image/jpeg')), 
	CONSTRAINT evidence_versions_extraction_state_enum CHECK (extraction_state IN ('extracted','manual_required','failed')), 
	CONSTRAINT evidence_versions_signature_state_enum CHECK (signature_state IN ('not_validated','validated')), 
	CONSTRAINT evidence_versions_check_0 CHECK (byte_length>0 AND byte_length<=10485760), 
	CONSTRAINT evidence_versions_check_1 CHECK (octet_length(byte_sha256)=32), 
	CONSTRAINT evidence_versions_check_2 CHECK (signature_state='not_validated'), 
	CONSTRAINT uq_evidence_versions_storage_key UNIQUE (storage_key), 
	CONSTRAINT uq_evidence_versions_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE evaluation_runs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	office_id UUID NOT NULL, 
	namespace BYTEA NOT NULL, 
	state TEXT NOT NULL, 
	clock_mode TEXT NOT NULL, 
	clock_offset INTERVAL NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	CONSTRAINT pk_evaluation_runs PRIMARY KEY (id), 
	CONSTRAINT fk_evaluation_runs_office_id_field_offices FOREIGN KEY(office_id) REFERENCES field_offices (id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT evaluation_runs_state_enum CHECK (state IN ('active','retired')), 
	CONSTRAINT evaluation_runs_clock_mode_enum CHECK (clock_mode IN ('wall_clock','simulated')), 
	CONSTRAINT evaluation_runs_check_0 CHECK (octet_length(namespace)=32), 
	CONSTRAINT uq_evaluation_runs_id_office_id UNIQUE (id, office_id)
)

;

CREATE TABLE damage_categories (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	code TEXT NOT NULL, 
	label TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_damage_categories PRIMARY KEY (id), 
	CONSTRAINT fk_damage_categories_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_damage_categories_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_damage_categories_run_id_code UNIQUE (run_id, code), 
	CONSTRAINT uq_damage_categories_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE member_versions (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_version_id UUID NOT NULL, 
	member_id UUID NOT NULL, 
	name TEXT NOT NULL, 
	birth_date DATE, 
	relationship TEXT NOT NULL, 
	is_head BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_member_versions PRIMARY KEY (household_version_id, member_id), 
	CONSTRAINT fk_member_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_member_versions_household_version_id FOREIGN KEY(run_id, office_id, household_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_member_versions_member_id FOREIGN KEY(run_id, office_id, member_id) REFERENCES household_members (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_member_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE household_links (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	link_version_id UUID NOT NULL, 
	beneficiary_actor_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_household_links PRIMARY KEY (household_id), 
	CONSTRAINT fk_household_links_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_household_links_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_household_links_link_version_id FOREIGN KEY(run_id, office_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_household_links_beneficiary_actor_id FOREIGN KEY(run_id, office_id, beneficiary_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_household_links_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT rel_household_links_household_id_link_version_id FOREIGN KEY(run_id, office_id, household_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, household_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT rel_household_links_household_id_link_version_id_benefi_8d89 FOREIGN KEY(run_id, office_id, household_id, link_version_id, beneficiary_actor_id) REFERENCES household_link_versions (run_id, office_id, household_id, id, beneficiary_actor_id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE operation_barangays (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	operation_version_id UUID NOT NULL, 
	barangay_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_operation_barangays PRIMARY KEY (operation_version_id, barangay_id), 
	CONSTRAINT fk_operation_barangays_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_operation_barangays_operation_version_id FOREIGN KEY(run_id, office_id, operation_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_operation_barangays_barangay_id FOREIGN KEY(run_id, office_id, barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_operation_barangays_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE check_flags (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	check_run_id UUID NOT NULL, 
	code TEXT NOT NULL, 
	weight INTEGER NOT NULL, 
	matched_household_id UUID, 
	matched_member_id UUID, 
	matched_link_version_id UUID, 
	scores JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_check_flags PRIMARY KEY (id), 
	CONSTRAINT fk_check_flags_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_check_flags_check_run_id FOREIGN KEY(run_id, office_id, check_run_id) REFERENCES check_runs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_check_flags_matched_household_id FOREIGN KEY(run_id, office_id, matched_household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_check_flags_matched_member_id FOREIGN KEY(run_id, office_id, matched_member_id) REFERENCES household_members (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_check_flags_matched_link_version_id FOREIGN KEY(run_id, office_id, matched_link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_check_flags_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT check_flags_check_0 CHECK (weight>=0), 
	CONSTRAINT uq_check_flags_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE submission_snapshots (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	disaster_id UUID NOT NULL, 
	barangay_id UUID NOT NULL, 
	kind TEXT NOT NULL, 
	sender_id UUID, 
	resolution_evidence_id UUID, 
	fallback_reason TEXT, 
	fallback_details JSONB NOT NULL, 
	submitted_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_submission_snapshots PRIMARY KEY (id), 
	CONSTRAINT fk_submission_snapshots_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_submission_snapshots_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_submission_snapshots_barangay_id FOREIGN KEY(run_id, office_id, barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT submission_snapshots_kind_enum CHECK (kind IN ('barangay_submission','system_fallback')), 
	CONSTRAINT fk_submission_snapshots_sender_id FOREIGN KEY(run_id, office_id, sender_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_submission_snapshots_resolution_evidence_id FOREIGN KEY(run_id, office_id, resolution_evidence_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT submission_snapshots_fallback_reason_enum CHECK (fallback_reason IN ('no_eligible_endorser','no_barangay_response','no_barangay_submission')), 
	CONSTRAINT fk_submission_snapshots_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT submission_snapshots_check_0 CHECK ((kind='barangay_submission' AND sender_id IS NOT NULL AND resolution_evidence_id IS NOT NULL AND fallback_reason IS NULL) OR (kind='system_fallback' AND sender_id IS NULL AND resolution_evidence_id IS NULL AND fallback_reason IS NOT NULL)), 
	CONSTRAINT uq_submission_snapshots_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE paid_difference_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	handover_id UUID NOT NULL, 
	new_input_version_id UUID, 
	new_decision_id UUID, 
	hypothetical_centavos BIGINT NOT NULL, 
	locked_centavos BIGINT NOT NULL, 
	delta_centavos BIGINT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_paid_difference_events PRIMARY KEY (id), 
	CONSTRAINT fk_paid_difference_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_paid_difference_events_handover_id FOREIGN KEY(run_id, office_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_paid_difference_events_new_input_version_id FOREIGN KEY(run_id, office_id, new_input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_paid_difference_events_new_decision_id FOREIGN KEY(run_id, office_id, new_decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_paid_difference_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT paid_difference_events_check_0 CHECK (num_nonnulls(new_input_version_id,new_decision_id)>0), 
	CONSTRAINT paid_difference_events_check_1 CHECK (delta_centavos=hypothetical_centavos-locked_centavos), 
	CONSTRAINT uq_paid_difference_events_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT paid_difference_events_hypothetical_centavos_range CHECK (hypothetical_centavos BETWEEN -9000000000000000000 AND 9000000000000000000), 
	CONSTRAINT paid_difference_events_locked_centavos_range CHECK (locked_centavos BETWEEN -9000000000000000000 AND 9000000000000000000), 
	CONSTRAINT paid_difference_events_delta_centavos_range CHECK (delta_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE session_assignments (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	session_version_id UUID NOT NULL, 
	actor_id UUID NOT NULL, 
	assignment_kind TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_session_assignments PRIMARY KEY (id), 
	CONSTRAINT fk_session_assignments_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_assignments_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_assignments_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT session_assignments_assignment_kind_enum CHECK (assignment_kind IN ('cash','followup')), 
	CONSTRAINT fk_session_assignments_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_session_assignments_session_version_id_actor_id_assi_d791 UNIQUE (session_version_id, actor_id, assignment_kind), 
	CONSTRAINT uq_session_assignments_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE session_entries (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	session_version_id UUID NOT NULL, 
	list_entry_id UUID NOT NULL, 
	entitlement_id UUID NOT NULL, 
	entitlement_version_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_session_entries PRIMARY KEY (id), 
	CONSTRAINT fk_session_entries_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_entries_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_entries_list_entry_id FOREIGN KEY(run_id, office_id, list_entry_id) REFERENCES approved_list_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_entries_entitlement_id FOREIGN KEY(run_id, office_id, entitlement_id) REFERENCES entitlements (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_entries_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_session_entries_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_session_entries_session_version_id_entitlement_id UNIQUE (session_version_id, entitlement_id), 
	CONSTRAINT uq_session_entries_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT rel_session_entries_list_entry_id_entitlement_id_entitl_06f2 FOREIGN KEY(run_id, office_id, list_entry_id, entitlement_id, entitlement_version_id) REFERENCES approved_list_entries (run_id, office_id, id, entitlement_id, entitlement_version_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_session_entries_run_id_office_id_id_entitlement_id_e_9ee9 UNIQUE (run_id, office_id, id, entitlement_id, entitlement_version_id), 
	CONSTRAINT uq_session_entries_run_id_office_id_id_entitlement_version_id UNIQUE (run_id, office_id, id, entitlement_version_id), 
	CONSTRAINT uq_session_entries_run_id_office_id_id_session_version__ebf1 UNIQUE (run_id, office_id, id, session_version_id, entitlement_id, entitlement_version_id)
)

;

CREATE TABLE attempt_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	attempt_id UUID NOT NULL, 
	action TEXT NOT NULL, 
	identity_check_id UUID, 
	reason TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_attempt_events PRIMARY KEY (id), 
	CONSTRAINT fk_attempt_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_attempt_events_attempt_id FOREIGN KEY(run_id, office_id, attempt_id) REFERENCES payout_attempts (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT attempt_events_action_enum CHECK (action IN ('open','present','stop','expire','handover')), 
	CONSTRAINT fk_attempt_events_identity_check_id FOREIGN KEY(run_id, office_id, identity_check_id) REFERENCES identity_checks (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_attempt_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT attempt_events_check_0 CHECK (action NOT IN ('stop','expire') OR length(reason)>0), 
	CONSTRAINT uq_attempt_events_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE payout_codes (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	attempt_id UUID NOT NULL, 
	salt BYTEA NOT NULL, 
	digest BYTEA NOT NULL, 
	algorithm TEXT NOT NULL, 
	expires_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	consumed_at TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_payout_codes PRIMARY KEY (attempt_id), 
	CONSTRAINT fk_payout_codes_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_payout_codes_attempt_id FOREIGN KEY(run_id, office_id, attempt_id) REFERENCES payout_attempts (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_payout_codes_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT payout_codes_check_0 CHECK (octet_length(salt)=32), 
	CONSTRAINT payout_codes_check_1 CHECK (octet_length(digest)=32)
)

;

CREATE TABLE credential_counters (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	pin_id UUID NOT NULL, 
	failed_count INTEGER NOT NULL, 
	window_start TIMESTAMP WITH TIME ZONE, 
	locked_until TIMESTAMP WITH TIME ZONE, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_credential_counters PRIMARY KEY (pin_id), 
	CONSTRAINT fk_credential_counters_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_credential_counters_pin_id FOREIGN KEY(run_id, office_id, pin_id) REFERENCES assisted_pins (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_credential_counters_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT credential_counters_check_0 CHECK (failed_count>=0)
)

;

CREATE TABLE transaction_clearances (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	transaction_id UUID NOT NULL, 
	stopped_attempt_id UUID NOT NULL, 
	reason TEXT NOT NULL, 
	cleared_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_transaction_clearances PRIMARY KEY (id), 
	CONSTRAINT fk_transaction_clearances_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_transaction_clearances_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_transaction_clearances_stopped_attempt_id FOREIGN KEY(run_id, office_id, stopped_attempt_id) REFERENCES payout_attempts (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_transaction_clearances_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_transaction_clearances_stopped_attempt_id UNIQUE (stopped_attempt_id), 
	CONSTRAINT uq_transaction_clearances_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE transaction_notes (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	transaction_id UUID NOT NULL, 
	actor_id UUID NOT NULL, 
	note TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_transaction_notes PRIMARY KEY (id), 
	CONSTRAINT fk_transaction_notes_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_transaction_notes_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_transaction_notes_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_transaction_notes_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_transaction_notes_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE grievances (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	transaction_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	business_status TEXT NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_grievances PRIMARY KEY (id), 
	CONSTRAINT fk_grievances_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_grievances_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_grievances_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT grievances_business_status_enum CHECK (business_status IN ('open','under_review','closed')), 
	CONSTRAINT fk_grievances_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_grievances_transaction_id UNIQUE (transaction_id), 
	CONSTRAINT uq_grievances_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE fund_heads (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	source_root_id UUID NOT NULL, 
	current_entry_id UUID NOT NULL, 
	revision INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_fund_heads PRIMARY KEY (source_root_id), 
	CONSTRAINT fk_fund_heads_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_heads_source_root_id FOREIGN KEY(run_id, office_id, source_root_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_heads_current_entry_id FOREIGN KEY(run_id, office_id, current_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_heads_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_fund_heads_current_entry_id UNIQUE (current_entry_id)
)

;

CREATE TABLE fund_signatories (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	entry_id UUID NOT NULL, 
	ordinal INTEGER NOT NULL, 
	printed_name TEXT NOT NULL, 
	printed_role TEXT NOT NULL, 
	signature_state TEXT NOT NULL, 
	validation_evidence_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_fund_signatories PRIMARY KEY (entry_id, ordinal), 
	CONSTRAINT fk_fund_signatories_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_signatories_entry_id FOREIGN KEY(run_id, office_id, entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fund_signatories_signature_state_enum CHECK (signature_state IN ('not_validated','validated')), 
	CONSTRAINT fk_fund_signatories_validation_evidence_id FOREIGN KEY(run_id, office_id, validation_evidence_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_signatories_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fund_signatories_check_0 CHECK (ordinal>=0), 
	CONSTRAINT fund_signatories_check_1 CHECK (signature_state='not_validated' OR validation_evidence_id IS NOT NULL)
)

;

CREATE TABLE fund_area_lines (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	entry_id UUID NOT NULL, 
	ordinal INTEGER NOT NULL, 
	area_code TEXT NOT NULL, 
	area_name TEXT NOT NULL, 
	amount_centavos BIGINT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_fund_area_lines PRIMARY KEY (entry_id, ordinal), 
	CONSTRAINT fk_fund_area_lines_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_area_lines_entry_id FOREIGN KEY(run_id, office_id, entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_fund_area_lines_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fund_area_lines_check_0 CHECK (ordinal>=0), 
	CONSTRAINT fund_area_lines_check_1 CHECK (amount_centavos>=0), 
	CONSTRAINT fund_area_lines_amount_centavos_range CHECK (amount_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE release_document_uses (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	byte_sha256 BYTEA NOT NULL, 
	source_root_id UUID NOT NULL, 
	evidence_version_id UUID NOT NULL, 
	role TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_release_document_uses PRIMARY KEY (run_id, byte_sha256), 
	CONSTRAINT fk_release_document_uses_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_release_document_uses_source_root_id FOREIGN KEY(run_id, office_id, source_root_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_release_document_uses_evidence_version_id FOREIGN KEY(run_id, office_id, evidence_version_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT release_document_uses_role_enum CHECK (role IN ('primary','supporting')), 
	CONSTRAINT fk_release_document_uses_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT release_document_uses_check_0 CHECK (octet_length(byte_sha256)=32)
)

;

CREATE TABLE deployments (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	protocol TEXT NOT NULL, 
	chain_id NUMERIC(78, 0) NOT NULL, 
	address BYTEA NOT NULL, 
	deployment_uid BYTEA, 
	genesis_hash BYTEA NOT NULL, 
	deploy_block_number BIGINT NOT NULL, 
	deploy_block_hash BYTEA NOT NULL, 
	runtime_code_hash BYTEA NOT NULL, 
	abi_reference TEXT NOT NULL, 
	confirmation_policy TEXT NOT NULL, 
	state TEXT NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_deployments PRIMARY KEY (id), 
	CONSTRAINT fk_deployments_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT deployments_protocol_enum CHECK (protocol IN ('ayudachain.evidence.v1','legacy.receipt.v1')), 
	CONSTRAINT deployments_state_enum CHECK (state IN ('active','retired','lost')), 
	CONSTRAINT fk_deployments_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT deployments_check_0 CHECK (octet_length(address)=20), 
	CONSTRAINT deployments_check_1 CHECK (octet_length(genesis_hash)=32), 
	CONSTRAINT deployments_check_2 CHECK (octet_length(deploy_block_hash)=32), 
	CONSTRAINT deployments_check_3 CHECK (octet_length(runtime_code_hash)=32), 
	CONSTRAINT uq_deployments_chain_id_address_deploy_block_hash UNIQUE (chain_id, address, deploy_block_hash), 
	CONSTRAINT uq_deployments_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE audit_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	sequence BIGINT NOT NULL, 
	actor_id UUID NOT NULL, 
	action TEXT NOT NULL, 
	request_id UUID NOT NULL, 
	reason TEXT, 
	effective_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	safe_details JSONB NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_audit_events PRIMARY KEY (id), 
	CONSTRAINT fk_audit_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_events_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_audit_events_sequence UNIQUE (sequence), 
	CONSTRAINT uq_audit_events_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE auditor_access_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	auditor_actor_id UUID NOT NULL, 
	action TEXT NOT NULL, 
	fields_opened TEXT[] NOT NULL, 
	success BOOLEAN NOT NULL, 
	checked_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	integrity_result TEXT, 
	safe_error TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_auditor_access_events PRIMARY KEY (id), 
	CONSTRAINT fk_auditor_access_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_events_auditor_actor_id FOREIGN KEY(run_id, office_id, auditor_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT auditor_access_events_action_enum CHECK (action IN ('browse','open','file','identity','integrity','material')), 
	CONSTRAINT fk_auditor_access_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_auditor_access_events_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE notifications (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	household_id UUID NOT NULL, 
	link_version_id UUID, 
	purpose TEXT NOT NULL, 
	channel TEXT NOT NULL, 
	content JSONB NOT NULL, 
	simulated BOOLEAN NOT NULL, 
	state TEXT NOT NULL, 
	session_version_id UUID, 
	entitlement_version_id UUID, 
	decision_id UUID, 
	operation_version_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_notifications PRIMARY KEY (id), 
	CONSTRAINT fk_notifications_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notifications_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notifications_link_version_id FOREIGN KEY(run_id, office_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT notifications_channel_enum CHECK (channel IN ('in_app','simulated_notice_sms')), 
	CONSTRAINT notifications_state_enum CHECK (state IN ('pending','delivered','failed','no_contact')), 
	CONSTRAINT fk_notifications_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notifications_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notifications_decision_id FOREIGN KEY(run_id, office_id, decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notifications_operation_version_id FOREIGN KEY(run_id, office_id, operation_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notifications_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT notifications_check_0 CHECK (num_nonnulls(session_version_id,entitlement_version_id,decision_id,operation_version_id)=1), 
	CONSTRAINT uq_notifications_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE command_results (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	actor_id UUID NOT NULL, 
	command_name TEXT NOT NULL, 
	idempotency_key TEXT NOT NULL, 
	request_digest BYTEA NOT NULL, 
	status_code INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_command_results PRIMARY KEY (actor_id, command_name, idempotency_key), 
	CONSTRAINT fk_command_results_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_results_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_results_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT command_results_check_0 CHECK (octet_length(request_digest)=32)
)

;

CREATE TABLE snapshot_items (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	snapshot_id UUID NOT NULL, 
	round_id UUID NOT NULL, 
	submission_id UUID NOT NULL, 
	registry_version_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_snapshot_items PRIMARY KEY (snapshot_id, round_id), 
	CONSTRAINT fk_snapshot_items_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_items_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_items_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_items_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_items_registry_version_id FOREIGN KEY(run_id, office_id, registry_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_items_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT rel_snapshot_items_submission_id_round_id FOREIGN KEY(run_id, office_id, submission_id, round_id) REFERENCES claim_rounds (run_id, office_id, submission_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT rel_snapshot_items_submission_id_registry_version_id FOREIGN KEY(run_id, office_id, submission_id, registry_version_id) REFERENCES claim_submissions (run_id, office_id, id, registry_version_id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE snapshot_response_refs (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	snapshot_id UUID NOT NULL, 
	response_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_snapshot_response_refs PRIMARY KEY (snapshot_id, response_id), 
	CONSTRAINT fk_snapshot_response_refs_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_response_refs_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_response_refs_response_id FOREIGN KEY(run_id, office_id, response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_snapshot_response_refs_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE amount_rules (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	input_version_id UUID NOT NULL, 
	category_id UUID NOT NULL, 
	day_count INTEGER, 
	fixed_centavos BIGINT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_amount_rules PRIMARY KEY (id), 
	CONSTRAINT fk_amount_rules_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_amount_rules_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_amount_rules_category_id FOREIGN KEY(run_id, office_id, category_id) REFERENCES damage_categories (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_amount_rules_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT amount_rules_check_0 CHECK ((day_count>0 AND fixed_centavos IS NULL) OR (day_count IS NULL AND fixed_centavos>0)), 
	CONSTRAINT uq_amount_rules_input_version_id_category_id UNIQUE (input_version_id, category_id), 
	CONSTRAINT uq_amount_rules_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT amount_rules_required_pair CHECK (num_nonnulls(day_count,fixed_centavos)=1), 
	CONSTRAINT amount_rules_fixed_centavos_range CHECK (fixed_centavos BETWEEN -9000000000000000000 AND 9000000000000000000)
)

;

CREATE TABLE active_session_memberships (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	entitlement_id UUID NOT NULL, 
	session_id UUID NOT NULL, 
	session_entry_id UUID NOT NULL, 
	entitlement_version_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_active_session_memberships PRIMARY KEY (entitlement_id), 
	CONSTRAINT fk_active_session_memberships_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_active_session_memberships_entitlement_id FOREIGN KEY(run_id, office_id, entitlement_id) REFERENCES entitlements (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_active_session_memberships_session_id FOREIGN KEY(run_id, office_id, session_id) REFERENCES payout_sessions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_active_session_memberships_session_entry_id FOREIGN KEY(run_id, office_id, session_entry_id) REFERENCES session_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_active_session_memberships_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_active_session_memberships_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT rel_active_session_memberships_session_entry_id_entitle_cbe1 FOREIGN KEY(run_id, office_id, session_entry_id, entitlement_id, entitlement_version_id) REFERENCES session_entries (run_id, office_id, id, entitlement_id, entitlement_version_id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE grievance_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	grievance_id UUID NOT NULL, 
	predecessor_id UUID, 
	kind TEXT NOT NULL, 
	outcome_version_id UUID, 
	report_text TEXT, 
	resolution TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_grievance_events PRIMARY KEY (id), 
	CONSTRAINT fk_grievance_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_grievance_events_grievance_id FOREIGN KEY(run_id, office_id, grievance_id) REFERENCES grievances (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_grievance_events_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES grievance_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT grievance_events_kind_enum CHECK (kind IN ('open','report','review','note','resolve','reopen')), 
	CONSTRAINT fk_grievance_events_outcome_version_id FOREIGN KEY(run_id, office_id, outcome_version_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_grievance_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT grievance_events_check_0 CHECK (kind!='resolve' OR length(resolution)>0), 
	CONSTRAINT uq_grievance_events_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT uq_grievance_events_run_id_office_id_grievance_id_id UNIQUE (run_id, office_id, grievance_id, id), 
	CONSTRAINT fk_grievance_events_predecessor_parent FOREIGN KEY(run_id, office_id, grievance_id, predecessor_id) REFERENCES grievance_events (run_id, office_id, grievance_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT rel_grievance_events_outcome_version_id FOREIGN KEY(run_id, office_id, outcome_version_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE commitments (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	public_id BYTEA NOT NULL, 
	protocol TEXT NOT NULL, 
	kind TEXT NOT NULL, 
	predecessor_commitment_id UUID, 
	public_context BYTEA NOT NULL, 
	public_related BYTEA, 
	canonical_bytes BYTEA NOT NULL, 
	content_hash BYTEA NOT NULL, 
	private_nonce BYTEA NOT NULL, 
	deployment_id UUID NOT NULL, 
	evidence_version_id UUID, 
	fund_entry_id UUID, 
	input_version_id UUID, 
	snapshot_id UUID, 
	list_version_id UUID, 
	handover_id UUID, 
	outcome_version_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_commitments PRIMARY KEY (id), 
	CONSTRAINT fk_commitments_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT commitments_kind_enum CHECK (kind IN ('document','amount_input','barangay_submission','system_fallback','approved_list','handover','outcome','fund_release','fund_reversal','fund_replacement')), 
	CONSTRAINT fk_commitments_predecessor_commitment_id FOREIGN KEY(run_id, office_id, predecessor_commitment_id) REFERENCES commitments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_deployment_id FOREIGN KEY(run_id, office_id, deployment_id) REFERENCES deployments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_evidence_version_id FOREIGN KEY(run_id, office_id, evidence_version_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_fund_entry_id FOREIGN KEY(run_id, office_id, fund_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_list_version_id FOREIGN KEY(run_id, office_id, list_version_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_handover_id FOREIGN KEY(run_id, office_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_outcome_version_id FOREIGN KEY(run_id, office_id, outcome_version_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_commitments_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT commitments_check_0 CHECK (octet_length(public_id)=32), 
	CONSTRAINT commitments_check_1 CHECK (octet_length(content_hash)=32), 
	CONSTRAINT commitments_check_2 CHECK (octet_length(private_nonce)=32), 
	CONSTRAINT commitments_check_3 CHECK (octet_length(public_context)=32), 
	CONSTRAINT commitments_check_4 CHECK (num_nonnulls(evidence_version_id,fund_entry_id,input_version_id,snapshot_id,list_version_id,handover_id,outcome_version_id)=1), 
	CONSTRAINT uq_commitments_public_id UNIQUE (public_id), 
	CONSTRAINT uq_commitments_evidence_version_id UNIQUE (evidence_version_id), 
	CONSTRAINT uq_commitments_fund_entry_id UNIQUE (fund_entry_id), 
	CONSTRAINT uq_commitments_input_version_id UNIQUE (input_version_id), 
	CONSTRAINT uq_commitments_snapshot_id UNIQUE (snapshot_id), 
	CONSTRAINT uq_commitments_list_version_id UNIQUE (list_version_id), 
	CONSTRAINT uq_commitments_handover_id UNIQUE (handover_id), 
	CONSTRAINT uq_commitments_outcome_version_id UNIQUE (outcome_version_id), 
	CONSTRAINT uq_commitments_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE anchor_jobs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	deployment_id UUID NOT NULL, 
	operation TEXT NOT NULL, 
	state TEXT NOT NULL, 
	next_attempt_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	lease_owner TEXT, 
	lease_until TIMESTAMP WITH TIME ZONE, 
	last_error_code TEXT, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_jobs PRIMARY KEY (id), 
	CONSTRAINT fk_anchor_jobs_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_jobs_deployment_id FOREIGN KEY(run_id, office_id, deployment_id) REFERENCES deployments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT anchor_jobs_operation_enum CHECK (operation IN ('anchor_record','fund_release','fund_correction')), 
	CONSTRAINT anchor_jobs_state_enum CHECK (state IN ('pending','prepared','submitted','uncertain','retry_wait','mined_unapplied','confirmed','conflict','deployment_lost')), 
	CONSTRAINT fk_anchor_jobs_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_anchor_jobs_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE notification_attempts (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	notification_id UUID NOT NULL, 
	attempt_number INTEGER NOT NULL, 
	adapter TEXT NOT NULL, 
	simulated BOOLEAN NOT NULL, 
	result TEXT NOT NULL, 
	safe_failure TEXT, 
	attempted_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_notification_attempts PRIMARY KEY (id), 
	CONSTRAINT fk_notification_attempts_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_notification_attempts_notification_id FOREIGN KEY(run_id, office_id, notification_id) REFERENCES notifications (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT notification_attempts_result_enum CHECK (result IN ('delivered','failed','no_contact')), 
	CONSTRAINT fk_notification_attempts_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_notification_attempts_notification_id_attempt_number UNIQUE (notification_id, attempt_number), 
	CONSTRAINT uq_notification_attempts_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE legacy_records (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	source_db_sha256 BYTEA NOT NULL, 
	source_table TEXT NOT NULL, 
	source_key TEXT NOT NULL, 
	original_fields JSONB NOT NULL, 
	original_receipt_hash BYTEA, 
	deployment_id UUID, 
	imported_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_legacy_records PRIMARY KEY (id), 
	CONSTRAINT fk_legacy_records_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT legacy_records_source_table_enum CHECK (source_table IN ('relief_batches','allocations','beneficiaries','distributions','audit_events')), 
	CONSTRAINT fk_legacy_records_deployment_id FOREIGN KEY(run_id, office_id, deployment_id) REFERENCES deployments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_legacy_records_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_legacy_records_source_db_sha256_source_table_source_key UNIQUE (source_db_sha256, source_table, source_key), 
	CONSTRAINT uq_legacy_records_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE evidence_links (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	evidence_version_id UUID NOT NULL, 
	attachment_role TEXT NOT NULL, 
	input_field TEXT, 
	nomination_id UUID, 
	operation_version_id UUID, 
	household_version_id UUID, 
	registry_review_id UUID, 
	submission_id UUID, 
	response_id UUID, 
	snapshot_id UUID, 
	input_version_id UUID, 
	amount_rule_id UUID, 
	fund_entry_id UUID, 
	clearance_id UUID, 
	grievance_event_id UUID, 
	challenge_event_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_evidence_links PRIMARY KEY (id), 
	CONSTRAINT fk_evidence_links_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_evidence_version_id FOREIGN KEY(run_id, office_id, evidence_version_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_nomination_id FOREIGN KEY(run_id, office_id, nomination_id) REFERENCES nominations (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_operation_version_id FOREIGN KEY(run_id, office_id, operation_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_household_version_id FOREIGN KEY(run_id, office_id, household_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_response_id FOREIGN KEY(run_id, office_id, response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_amount_rule_id FOREIGN KEY(run_id, office_id, amount_rule_id) REFERENCES amount_rules (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_fund_entry_id FOREIGN KEY(run_id, office_id, fund_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_clearance_id FOREIGN KEY(run_id, office_id, clearance_id) REFERENCES transaction_clearances (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_grievance_event_id FOREIGN KEY(run_id, office_id, grievance_event_id) REFERENCES grievance_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_challenge_event_id FOREIGN KEY(run_id, office_id, challenge_event_id) REFERENCES challenge_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_evidence_links_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT evidence_links_check_0 CHECK (num_nonnulls(nomination_id,operation_version_id,household_version_id,registry_review_id,submission_id,response_id,snapshot_id,input_version_id,amount_rule_id,fund_entry_id,clearance_id,grievance_event_id,challenge_event_id)=1), 
	CONSTRAINT uq_evidence_links_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT evidence_link_owner_role CHECK ((nomination_id IS NOT NULL AND attachment_role IN ('nomination')) OR (operation_version_id IS NOT NULL AND attachment_role IN ('operation_basis')) OR (household_version_id IS NOT NULL AND attachment_role IN ('identity_photo','identity_document')) OR (registry_review_id IS NOT NULL AND attachment_role IN ('field_check','identity_photo','identity_document')) OR (submission_id IS NOT NULL AND attachment_role IN ('damage')) OR (response_id IS NOT NULL AND attachment_role IN ('damage')) OR (snapshot_id IS NOT NULL AND attachment_role IN ('council_resolution')) OR (input_version_id IS NOT NULL AND attachment_role IN ('wage')) OR (amount_rule_id IS NOT NULL AND attachment_role IN ('days','fixed_amount')) OR (fund_entry_id IS NOT NULL AND attachment_role IN ('release_source','supporting','amended_source')) OR (clearance_id IS NOT NULL AND attachment_role IN ('clearance')) OR (grievance_event_id IS NOT NULL AND attachment_role IN ('private_report')) OR (challenge_event_id IS NOT NULL AND attachment_role IN ('private_report')))
)

;

CREATE TABLE anchor_job_items (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	commitment_id UUID NOT NULL, 
	job_id UUID NOT NULL, 
	ordinal INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_job_items PRIMARY KEY (commitment_id), 
	CONSTRAINT fk_anchor_job_items_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_job_items_commitment_id FOREIGN KEY(run_id, office_id, commitment_id) REFERENCES commitments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_job_items_job_id FOREIGN KEY(run_id, office_id, job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_job_items_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT anchor_job_items_check_0 CHECK (ordinal>=0), 
	CONSTRAINT uq_anchor_job_items_job_id_ordinal UNIQUE (job_id, ordinal)
)

;

CREATE TABLE anchor_dependencies (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	job_id UUID NOT NULL, 
	prerequisite_job_id UUID NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_dependencies PRIMARY KEY (job_id, prerequisite_job_id), 
	CONSTRAINT fk_anchor_dependencies_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_dependencies_job_id FOREIGN KEY(run_id, office_id, job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_dependencies_prerequisite_job_id FOREIGN KEY(run_id, office_id, prerequisite_job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_dependencies_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT anchor_dependencies_check_0 CHECK (job_id!=prerequisite_job_id)
)

;

CREATE TABLE anchor_submissions (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	job_id UUID NOT NULL, 
	attempt_number INTEGER NOT NULL, 
	signer_address BYTEA NOT NULL, 
	nonce NUMERIC(78, 0) NOT NULL, 
	raw_signed_tx BYTEA NOT NULL, 
	candidate_tx_hash BYTEA NOT NULL, 
	prepared_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_submissions PRIMARY KEY (id), 
	CONSTRAINT fk_anchor_submissions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_submissions_job_id FOREIGN KEY(run_id, office_id, job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_submissions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT anchor_submissions_check_0 CHECK (octet_length(signer_address)=20), 
	CONSTRAINT anchor_submissions_check_1 CHECK (octet_length(candidate_tx_hash)=32), 
	CONSTRAINT anchor_submissions_check_2 CHECK (nonce>=0), 
	CONSTRAINT anchor_submissions_check_3 CHECK (attempt_number>0), 
	CONSTRAINT uq_anchor_submissions_job_id_attempt_number UNIQUE (job_id, attempt_number), 
	CONSTRAINT uq_anchor_submissions_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE audit_targets (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	audit_event_id UUID NOT NULL, 
	actor_version_id UUID, 
	household_version_id UUID, 
	link_version_id UUID, 
	registry_review_id UUID, 
	operation_version_id UUID, 
	submission_id UUID, 
	round_id UUID, 
	response_id UUID, 
	check_run_id UUID, 
	decision_id UUID, 
	snapshot_id UUID, 
	input_version_id UUID, 
	entitlement_version_id UUID, 
	list_version_id UUID, 
	session_version_id UUID, 
	attempt_event_id UUID, 
	handover_id UUID, 
	outcome_version_id UUID, 
	grievance_event_id UUID, 
	challenge_event_id UUID, 
	fund_entry_id UUID, 
	correction_set_id UUID, 
	evidence_version_id UUID, 
	anchor_job_id UUID, 
	notification_id UUID, 
	evaluation_run_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_audit_targets PRIMARY KEY (id), 
	CONSTRAINT fk_audit_targets_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_audit_event_id FOREIGN KEY(run_id, office_id, audit_event_id) REFERENCES audit_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_actor_version_id FOREIGN KEY(run_id, office_id, actor_version_id) REFERENCES actor_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_household_version_id FOREIGN KEY(run_id, office_id, household_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_link_version_id FOREIGN KEY(run_id, office_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_operation_version_id FOREIGN KEY(run_id, office_id, operation_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_response_id FOREIGN KEY(run_id, office_id, response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_check_run_id FOREIGN KEY(run_id, office_id, check_run_id) REFERENCES check_runs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_decision_id FOREIGN KEY(run_id, office_id, decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_list_version_id FOREIGN KEY(run_id, office_id, list_version_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_attempt_event_id FOREIGN KEY(run_id, office_id, attempt_event_id) REFERENCES attempt_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_handover_id FOREIGN KEY(run_id, office_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_outcome_version_id FOREIGN KEY(run_id, office_id, outcome_version_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_grievance_event_id FOREIGN KEY(run_id, office_id, grievance_event_id) REFERENCES grievance_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_challenge_event_id FOREIGN KEY(run_id, office_id, challenge_event_id) REFERENCES challenge_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_fund_entry_id FOREIGN KEY(run_id, office_id, fund_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_correction_set_id FOREIGN KEY(run_id, office_id, correction_set_id) REFERENCES fund_correction_sets (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_evidence_version_id FOREIGN KEY(run_id, office_id, evidence_version_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_anchor_job_id FOREIGN KEY(run_id, office_id, anchor_job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_notification_id FOREIGN KEY(run_id, office_id, notification_id) REFERENCES notifications (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_evaluation_run_id_evaluation_runs FOREIGN KEY(evaluation_run_id) REFERENCES evaluation_runs (id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_audit_targets_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT audit_targets_check_0 CHECK (num_nonnulls(actor_version_id,household_version_id,link_version_id,registry_review_id,operation_version_id,submission_id,round_id,response_id,check_run_id,decision_id,snapshot_id,input_version_id,entitlement_version_id,list_version_id,session_version_id,attempt_event_id,handover_id,outcome_version_id,grievance_event_id,challenge_event_id,fund_entry_id,correction_set_id,evidence_version_id,anchor_job_id,notification_id,evaluation_run_id)=1), 
	CONSTRAINT uq_audit_targets_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE auditor_access_targets (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	access_event_id UUID NOT NULL, 
	actor_version_id UUID, 
	household_version_id UUID, 
	link_version_id UUID, 
	registry_review_id UUID, 
	operation_version_id UUID, 
	submission_id UUID, 
	round_id UUID, 
	response_id UUID, 
	check_run_id UUID, 
	decision_id UUID, 
	snapshot_id UUID, 
	input_version_id UUID, 
	entitlement_version_id UUID, 
	list_version_id UUID, 
	session_version_id UUID, 
	attempt_event_id UUID, 
	handover_id UUID, 
	outcome_version_id UUID, 
	grievance_event_id UUID, 
	challenge_event_id UUID, 
	fund_entry_id UUID, 
	correction_set_id UUID, 
	evidence_version_id UUID, 
	anchor_job_id UUID, 
	notification_id UUID, 
	evaluation_run_id UUID, 
	household_id UUID, 
	claim_id UUID, 
	transaction_id UUID, 
	commitment_id UUID, 
	disaster_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_auditor_access_targets PRIMARY KEY (id), 
	CONSTRAINT fk_auditor_access_targets_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_access_event_id FOREIGN KEY(run_id, office_id, access_event_id) REFERENCES auditor_access_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_actor_version_id FOREIGN KEY(run_id, office_id, actor_version_id) REFERENCES actor_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_household_version_id FOREIGN KEY(run_id, office_id, household_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_link_version_id FOREIGN KEY(run_id, office_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_operation_version_id FOREIGN KEY(run_id, office_id, operation_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_response_id FOREIGN KEY(run_id, office_id, response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_check_run_id FOREIGN KEY(run_id, office_id, check_run_id) REFERENCES check_runs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_decision_id FOREIGN KEY(run_id, office_id, decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_list_version_id FOREIGN KEY(run_id, office_id, list_version_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_attempt_event_id FOREIGN KEY(run_id, office_id, attempt_event_id) REFERENCES attempt_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_handover_id FOREIGN KEY(run_id, office_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_outcome_version_id FOREIGN KEY(run_id, office_id, outcome_version_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_grievance_event_id FOREIGN KEY(run_id, office_id, grievance_event_id) REFERENCES grievance_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_challenge_event_id FOREIGN KEY(run_id, office_id, challenge_event_id) REFERENCES challenge_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_fund_entry_id FOREIGN KEY(run_id, office_id, fund_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_correction_set_id FOREIGN KEY(run_id, office_id, correction_set_id) REFERENCES fund_correction_sets (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_evidence_version_id FOREIGN KEY(run_id, office_id, evidence_version_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_anchor_job_id FOREIGN KEY(run_id, office_id, anchor_job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_notification_id FOREIGN KEY(run_id, office_id, notification_id) REFERENCES notifications (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_evaluation_run_id_evaluation_runs FOREIGN KEY(evaluation_run_id) REFERENCES evaluation_runs (id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_claim_id FOREIGN KEY(run_id, office_id, claim_id) REFERENCES claims (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_commitment_id FOREIGN KEY(run_id, office_id, commitment_id) REFERENCES commitments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_auditor_access_targets_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT auditor_access_targets_check_0 CHECK (num_nonnulls(actor_version_id,household_version_id,link_version_id,registry_review_id,operation_version_id,submission_id,round_id,response_id,check_run_id,decision_id,snapshot_id,input_version_id,entitlement_version_id,list_version_id,session_version_id,attempt_event_id,handover_id,outcome_version_id,grievance_event_id,challenge_event_id,fund_entry_id,correction_set_id,evidence_version_id,anchor_job_id,notification_id,evaluation_run_id,household_id,claim_id,transaction_id,commitment_id,disaster_id)=1), 
	CONSTRAINT uq_auditor_access_targets_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE command_result_refs (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	actor_id UUID NOT NULL, 
	command_name TEXT NOT NULL, 
	idempotency_key TEXT NOT NULL, 
	actor_version_id UUID, 
	household_version_id UUID, 
	link_version_id UUID, 
	registry_review_id UUID, 
	operation_version_id UUID, 
	submission_id UUID, 
	round_id UUID, 
	response_id UUID, 
	check_run_id UUID, 
	decision_id UUID, 
	snapshot_id UUID, 
	input_version_id UUID, 
	entitlement_version_id UUID, 
	list_version_id UUID, 
	session_version_id UUID, 
	attempt_event_id UUID, 
	handover_id UUID, 
	outcome_version_id UUID, 
	grievance_event_id UUID, 
	challenge_event_id UUID, 
	fund_entry_id UUID, 
	correction_set_id UUID, 
	evidence_version_id UUID, 
	anchor_job_id UUID, 
	notification_id UUID, 
	evaluation_run_id UUID, 
	household_id UUID, 
	claim_id UUID, 
	transaction_id UUID, 
	commitment_id UUID, 
	disaster_id UUID, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_command_result_refs PRIMARY KEY (id), 
	CONSTRAINT fk_command_result_refs_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_actor_version_id FOREIGN KEY(run_id, office_id, actor_version_id) REFERENCES actor_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_household_version_id FOREIGN KEY(run_id, office_id, household_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_link_version_id FOREIGN KEY(run_id, office_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_operation_version_id FOREIGN KEY(run_id, office_id, operation_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_response_id FOREIGN KEY(run_id, office_id, response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_check_run_id FOREIGN KEY(run_id, office_id, check_run_id) REFERENCES check_runs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_decision_id FOREIGN KEY(run_id, office_id, decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_snapshot_id FOREIGN KEY(run_id, office_id, snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_list_version_id FOREIGN KEY(run_id, office_id, list_version_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_attempt_event_id FOREIGN KEY(run_id, office_id, attempt_event_id) REFERENCES attempt_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_handover_id FOREIGN KEY(run_id, office_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_outcome_version_id FOREIGN KEY(run_id, office_id, outcome_version_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_grievance_event_id FOREIGN KEY(run_id, office_id, grievance_event_id) REFERENCES grievance_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_challenge_event_id FOREIGN KEY(run_id, office_id, challenge_event_id) REFERENCES challenge_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_fund_entry_id FOREIGN KEY(run_id, office_id, fund_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_correction_set_id FOREIGN KEY(run_id, office_id, correction_set_id) REFERENCES fund_correction_sets (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_evidence_version_id FOREIGN KEY(run_id, office_id, evidence_version_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_anchor_job_id FOREIGN KEY(run_id, office_id, anchor_job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_notification_id FOREIGN KEY(run_id, office_id, notification_id) REFERENCES notifications (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_evaluation_run_id_evaluation_runs FOREIGN KEY(evaluation_run_id) REFERENCES evaluation_runs (id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_claim_id FOREIGN KEY(run_id, office_id, claim_id) REFERENCES claims (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_commitment_id FOREIGN KEY(run_id, office_id, commitment_id) REFERENCES commitments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_command_result_refs_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT command_result_refs_check_0 CHECK (num_nonnulls(actor_version_id,household_version_id,link_version_id,registry_review_id,operation_version_id,submission_id,round_id,response_id,check_run_id,decision_id,snapshot_id,input_version_id,entitlement_version_id,list_version_id,session_version_id,attempt_event_id,handover_id,outcome_version_id,grievance_event_id,challenge_event_id,fund_entry_id,correction_set_id,evidence_version_id,anchor_job_id,notification_id,evaluation_run_id,household_id,claim_id,transaction_id,commitment_id,disaster_id)=1), 
	CONSTRAINT uq_command_result_refs_run_id_office_id_id UNIQUE (run_id, office_id, id), 
	CONSTRAINT fk_command_result_refs_actor_id_command_results FOREIGN KEY(actor_id, command_name, idempotency_key) REFERENCES command_results (actor_id, command_name, idempotency_key) DEFERRABLE INITIALLY DEFERRED
)

;

CREATE TABLE anchor_submission_events (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	job_id UUID NOT NULL, 
	submission_id UUID, 
	action TEXT NOT NULL, 
	observed_tx_hash BYTEA, 
	receipt_status INTEGER, 
	block_number BIGINT, 
	block_hash BYTEA, 
	gas_used NUMERIC(78, 0), 
	gas_price NUMERIC(78, 0), 
	log_index INTEGER, 
	error_code TEXT, 
	safe_details JSONB NOT NULL, 
	observed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_submission_events PRIMARY KEY (id), 
	CONSTRAINT fk_anchor_submission_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_submission_events_job_id FOREIGN KEY(run_id, office_id, job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_submission_events_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES anchor_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_submission_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_anchor_submission_events_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE anchor_observations (
	id UUID DEFAULT gen_random_uuid() NOT NULL, 
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	job_id UUID NOT NULL, 
	submission_id UUID, 
	verdict TEXT NOT NULL, 
	observed_tx_hash BYTEA, 
	receipt_json JSONB, 
	chain_record_json JSONB, 
	checked_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_observations PRIMARY KEY (id), 
	CONSTRAINT fk_anchor_observations_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_observations_job_id FOREIGN KEY(run_id, office_id, job_id) REFERENCES anchor_jobs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_observations_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES anchor_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT anchor_observations_verdict_enum CHECK (verdict IN ('mined_match','transport_failure','reverted','conflict','deployment_lost')), 
	CONSTRAINT fk_anchor_observations_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT uq_anchor_observations_run_id_office_id_id UNIQUE (run_id, office_id, id)
)

;

CREATE TABLE anchor_applications (
	run_id UUID NOT NULL, 
	office_id UUID NOT NULL, 
	observation_id UUID NOT NULL, 
	audit_event_id UUID NOT NULL, 
	applied_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL, 
	created_by UUID NOT NULL, 
	identity_assurance TEXT DEFAULT 'claimed_unverified' NOT NULL, 
	CONSTRAINT pk_anchor_applications PRIMARY KEY (observation_id), 
	CONSTRAINT fk_anchor_applications_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_applications_observation_id FOREIGN KEY(run_id, office_id, observation_id) REFERENCES anchor_observations (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_applications_audit_event_id FOREIGN KEY(run_id, office_id, audit_event_id) REFERENCES audit_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED, 
	CONSTRAINT fk_anchor_applications_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED
)

;
CREATE INDEX ix_active_session_memberships_entitlement_id ON active_session_memberships (entitlement_id);
CREATE INDEX ix_active_session_memberships_entitlement_version_id ON active_session_memberships (entitlement_version_id);
CREATE INDEX ix_active_session_memberships_session_entry_id ON active_session_memberships (session_entry_id);
CREATE INDEX ix_active_session_memberships_session_id ON active_session_memberships (session_id);
CREATE INDEX ix_actor_member_links_actor_id ON actor_member_links (actor_id);
CREATE INDEX ix_actor_member_links_basis_review_id ON actor_member_links (basis_review_id);
CREATE INDEX ix_actor_member_links_member_id ON actor_member_links (member_id);
CREATE INDEX ix_actor_member_links_predecessor_id ON actor_member_links (predecessor_id);
CREATE INDEX ix_actor_versions_actor_id ON actor_versions (actor_id);
CREATE INDEX ix_actor_versions_barangay_id ON actor_versions (barangay_id);
CREATE INDEX ix_actor_versions_nomination_id ON actor_versions (nomination_id);
CREATE INDEX ix_actor_versions_predecessor_id ON actor_versions (predecessor_id);
CREATE INDEX ix_actors_current_member_link_id ON actors (current_member_link_id);
CREATE INDEX ix_actors_current_version_id ON actors (current_version_id);
CREATE INDEX ix_amount_input_versions_disaster_id ON amount_input_versions (disaster_id);
CREATE INDEX ix_amount_input_versions_predecessor_id ON amount_input_versions (predecessor_id);
CREATE INDEX ix_amount_rules_category_id ON amount_rules (category_id);
CREATE INDEX ix_amount_rules_input_version_id ON amount_rules (input_version_id);
CREATE INDEX ix_anchor_applications_audit_event_id ON anchor_applications (audit_event_id);
CREATE INDEX ix_anchor_applications_observation_id ON anchor_applications (observation_id);
CREATE INDEX ix_anchor_dependencies_job_id ON anchor_dependencies (job_id);
CREATE INDEX ix_anchor_dependencies_prerequisite_job_id ON anchor_dependencies (prerequisite_job_id);
CREATE INDEX ix_anchor_job_items_commitment_id ON anchor_job_items (commitment_id);
CREATE INDEX ix_anchor_job_items_job_id ON anchor_job_items (job_id);
CREATE INDEX ix_anchor_jobs_deployment_id ON anchor_jobs (deployment_id);
CREATE INDEX ix_anchor_observations_job_id ON anchor_observations (job_id);
CREATE INDEX ix_anchor_observations_submission_id ON anchor_observations (submission_id);
CREATE INDEX ix_anchor_submission_events_job_id ON anchor_submission_events (job_id);
CREATE INDEX ix_anchor_submission_events_submission_id ON anchor_submission_events (submission_id);
CREATE INDEX ix_anchor_submissions_job_id ON anchor_submissions (job_id);
CREATE INDEX ix_approved_list_entries_display_category_id ON approved_list_entries (display_category_id);
CREATE INDEX ix_approved_list_entries_display_decision_id ON approved_list_entries (display_decision_id);
CREATE INDEX ix_approved_list_entries_entitlement_id ON approved_list_entries (entitlement_id);
CREATE INDEX ix_approved_list_entries_entitlement_version_id ON approved_list_entries (entitlement_version_id);
CREATE INDEX ix_approved_list_entries_list_version_id ON approved_list_entries (list_version_id);
CREATE INDEX ix_approved_list_entries_registry_review_id ON approved_list_entries (registry_review_id);
CREATE INDEX ix_approved_list_entries_registry_version_id ON approved_list_entries (registry_version_id);
CREATE INDEX ix_approved_list_entries_submission_id ON approved_list_entries (submission_id);
CREATE INDEX ix_approved_list_versions_basis_input_version_id ON approved_list_versions (basis_input_version_id);
CREATE INDEX ix_approved_list_versions_list_head_id ON approved_list_versions (list_head_id);
CREATE INDEX ix_approved_list_versions_predecessor_published_id ON approved_list_versions (predecessor_published_id);
CREATE INDEX ix_assisted_pins_established_after_check_id ON assisted_pins (established_after_check_id);
CREATE INDEX ix_assisted_pins_household_id ON assisted_pins (household_id);
CREATE INDEX ix_attempt_events_attempt_id ON attempt_events (attempt_id);
CREATE INDEX ix_attempt_events_identity_check_id ON attempt_events (identity_check_id);
CREATE INDEX ix_audit_events_actor_id ON audit_events (actor_id);
CREATE INDEX ix_audit_events_request_id ON audit_events (request_id);
CREATE INDEX ix_audit_targets_actor_version_id ON audit_targets (actor_version_id);
CREATE INDEX ix_audit_targets_anchor_job_id ON audit_targets (anchor_job_id);
CREATE INDEX ix_audit_targets_attempt_event_id ON audit_targets (attempt_event_id);
CREATE INDEX ix_audit_targets_audit_event_id ON audit_targets (audit_event_id);
CREATE INDEX ix_audit_targets_challenge_event_id ON audit_targets (challenge_event_id);
CREATE INDEX ix_audit_targets_check_run_id ON audit_targets (check_run_id);
CREATE INDEX ix_audit_targets_correction_set_id ON audit_targets (correction_set_id);
CREATE INDEX ix_audit_targets_decision_id ON audit_targets (decision_id);
CREATE INDEX ix_audit_targets_entitlement_version_id ON audit_targets (entitlement_version_id);
CREATE INDEX ix_audit_targets_evaluation_run_id ON audit_targets (evaluation_run_id);
CREATE INDEX ix_audit_targets_evidence_version_id ON audit_targets (evidence_version_id);
CREATE INDEX ix_audit_targets_fund_entry_id ON audit_targets (fund_entry_id);
CREATE INDEX ix_audit_targets_grievance_event_id ON audit_targets (grievance_event_id);
CREATE INDEX ix_audit_targets_handover_id ON audit_targets (handover_id);
CREATE INDEX ix_audit_targets_household_version_id ON audit_targets (household_version_id);
CREATE INDEX ix_audit_targets_input_version_id ON audit_targets (input_version_id);
CREATE INDEX ix_audit_targets_link_version_id ON audit_targets (link_version_id);
CREATE INDEX ix_audit_targets_list_version_id ON audit_targets (list_version_id);
CREATE INDEX ix_audit_targets_notification_id ON audit_targets (notification_id);
CREATE INDEX ix_audit_targets_operation_version_id ON audit_targets (operation_version_id);
CREATE INDEX ix_audit_targets_outcome_version_id ON audit_targets (outcome_version_id);
CREATE INDEX ix_audit_targets_registry_review_id ON audit_targets (registry_review_id);
CREATE INDEX ix_audit_targets_response_id ON audit_targets (response_id);
CREATE INDEX ix_audit_targets_round_id ON audit_targets (round_id);
CREATE INDEX ix_audit_targets_session_version_id ON audit_targets (session_version_id);
CREATE INDEX ix_audit_targets_snapshot_id ON audit_targets (snapshot_id);
CREATE INDEX ix_audit_targets_submission_id ON audit_targets (submission_id);
CREATE INDEX ix_auditor_access_events_auditor_actor_id ON auditor_access_events (auditor_actor_id);
CREATE INDEX ix_auditor_access_targets_access_event_id ON auditor_access_targets (access_event_id);
CREATE INDEX ix_auditor_access_targets_actor_version_id ON auditor_access_targets (actor_version_id);
CREATE INDEX ix_auditor_access_targets_anchor_job_id ON auditor_access_targets (anchor_job_id);
CREATE INDEX ix_auditor_access_targets_attempt_event_id ON auditor_access_targets (attempt_event_id);
CREATE INDEX ix_auditor_access_targets_challenge_event_id ON auditor_access_targets (challenge_event_id);
CREATE INDEX ix_auditor_access_targets_check_run_id ON auditor_access_targets (check_run_id);
CREATE INDEX ix_auditor_access_targets_claim_id ON auditor_access_targets (claim_id);
CREATE INDEX ix_auditor_access_targets_commitment_id ON auditor_access_targets (commitment_id);
CREATE INDEX ix_auditor_access_targets_correction_set_id ON auditor_access_targets (correction_set_id);
CREATE INDEX ix_auditor_access_targets_decision_id ON auditor_access_targets (decision_id);
CREATE INDEX ix_auditor_access_targets_disaster_id ON auditor_access_targets (disaster_id);
CREATE INDEX ix_auditor_access_targets_entitlement_version_id ON auditor_access_targets (entitlement_version_id);
CREATE INDEX ix_auditor_access_targets_evaluation_run_id ON auditor_access_targets (evaluation_run_id);
CREATE INDEX ix_auditor_access_targets_evidence_version_id ON auditor_access_targets (evidence_version_id);
CREATE INDEX ix_auditor_access_targets_fund_entry_id ON auditor_access_targets (fund_entry_id);
CREATE INDEX ix_auditor_access_targets_grievance_event_id ON auditor_access_targets (grievance_event_id);
CREATE INDEX ix_auditor_access_targets_handover_id ON auditor_access_targets (handover_id);
CREATE INDEX ix_auditor_access_targets_household_id ON auditor_access_targets (household_id);
CREATE INDEX ix_auditor_access_targets_household_version_id ON auditor_access_targets (household_version_id);
CREATE INDEX ix_auditor_access_targets_input_version_id ON auditor_access_targets (input_version_id);
CREATE INDEX ix_auditor_access_targets_link_version_id ON auditor_access_targets (link_version_id);
CREATE INDEX ix_auditor_access_targets_list_version_id ON auditor_access_targets (list_version_id);
CREATE INDEX ix_auditor_access_targets_notification_id ON auditor_access_targets (notification_id);
CREATE INDEX ix_auditor_access_targets_operation_version_id ON auditor_access_targets (operation_version_id);
CREATE INDEX ix_auditor_access_targets_outcome_version_id ON auditor_access_targets (outcome_version_id);
CREATE INDEX ix_auditor_access_targets_registry_review_id ON auditor_access_targets (registry_review_id);
CREATE INDEX ix_auditor_access_targets_response_id ON auditor_access_targets (response_id);
CREATE INDEX ix_auditor_access_targets_round_id ON auditor_access_targets (round_id);
CREATE INDEX ix_auditor_access_targets_session_version_id ON auditor_access_targets (session_version_id);
CREATE INDEX ix_auditor_access_targets_snapshot_id ON auditor_access_targets (snapshot_id);
CREATE INDEX ix_auditor_access_targets_submission_id ON auditor_access_targets (submission_id);
CREATE INDEX ix_auditor_access_targets_transaction_id ON auditor_access_targets (transaction_id);
CREATE INDEX ix_challenge_events_challenge_id ON challenge_events (challenge_id);
CREATE INDEX ix_challenge_events_decision_id ON challenge_events (decision_id);
CREATE INDEX ix_challenge_events_predecessor_id ON challenge_events (predecessor_id);
CREATE INDEX ix_check_flags_check_run_id ON check_flags (check_run_id);
CREATE INDEX ix_check_flags_matched_household_id ON check_flags (matched_household_id);
CREATE INDEX ix_check_flags_matched_link_version_id ON check_flags (matched_link_version_id);
CREATE INDEX ix_check_flags_matched_member_id ON check_flags (matched_member_id);
CREATE INDEX ix_check_runs_round_id ON check_runs (round_id);
CREATE INDEX ix_check_runs_submission_id ON check_runs (submission_id);
CREATE INDEX ix_claim_decisions_bulk_group_id ON claim_decisions (bulk_group_id);
CREATE INDEX ix_claim_decisions_category_id ON claim_decisions (category_id);
CREATE INDEX ix_claim_decisions_challenge_event_id ON claim_decisions (challenge_event_id);
CREATE INDEX ix_claim_decisions_check_run_id ON claim_decisions (check_run_id);
CREATE INDEX ix_claim_decisions_claim_id ON claim_decisions (claim_id);
CREATE INDEX ix_claim_decisions_predecessor_id ON claim_decisions (predecessor_id);
CREATE INDEX ix_claim_decisions_round_id ON claim_decisions (round_id);
CREATE INDEX ix_claim_decisions_submission_id ON claim_decisions (submission_id);
CREATE INDEX ix_claim_operations_current_version_id ON claim_operations (current_version_id);
CREATE INDEX ix_claim_operations_disaster_id ON claim_operations (disaster_id);
CREATE INDEX ix_claim_responses_actor_id ON claim_responses (actor_id);
CREATE INDEX ix_claim_responses_category_opinion_id ON claim_responses (category_opinion_id);
CREATE INDEX ix_claim_responses_parent_response_id ON claim_responses (parent_response_id);
CREATE INDEX ix_claim_responses_round_id ON claim_responses (round_id);
CREATE INDEX ix_claim_rounds_primary_snapshot_id ON claim_rounds (primary_snapshot_id);
CREATE INDEX ix_claim_rounds_referral_decision_id ON claim_rounds (referral_decision_id);
CREATE INDEX ix_claim_rounds_routed_response_id ON claim_rounds (routed_response_id);
CREATE INDEX ix_claim_rounds_submission_id ON claim_rounds (submission_id);
CREATE INDEX ix_claim_submissions_claim_id ON claim_submissions (claim_id);
CREATE INDEX ix_claim_submissions_link_version_id ON claim_submissions (link_version_id);
CREATE INDEX ix_claim_submissions_predecessor_id ON claim_submissions (predecessor_id);
CREATE INDEX ix_claim_submissions_registry_version_id ON claim_submissions (registry_version_id);
CREATE INDEX ix_claim_submissions_stated_category_id ON claim_submissions (stated_category_id);
CREATE INDEX ix_claims_current_decision_id ON claims (current_decision_id);
CREATE INDEX ix_claims_current_submission_id ON claims (current_submission_id);
CREATE INDEX ix_claims_disaster_id ON claims (disaster_id);
CREATE INDEX ix_claims_household_id ON claims (household_id);
CREATE INDEX ix_claims_operation_id ON claims (operation_id);
CREATE INDEX ix_command_result_refs_actor_id ON command_result_refs (actor_id);
CREATE INDEX ix_command_result_refs_actor_version_id ON command_result_refs (actor_version_id);
CREATE INDEX ix_command_result_refs_anchor_job_id ON command_result_refs (anchor_job_id);
CREATE INDEX ix_command_result_refs_attempt_event_id ON command_result_refs (attempt_event_id);
CREATE INDEX ix_command_result_refs_challenge_event_id ON command_result_refs (challenge_event_id);
CREATE INDEX ix_command_result_refs_check_run_id ON command_result_refs (check_run_id);
CREATE INDEX ix_command_result_refs_claim_id ON command_result_refs (claim_id);
CREATE INDEX ix_command_result_refs_commitment_id ON command_result_refs (commitment_id);
CREATE INDEX ix_command_result_refs_correction_set_id ON command_result_refs (correction_set_id);
CREATE INDEX ix_command_result_refs_decision_id ON command_result_refs (decision_id);
CREATE INDEX ix_command_result_refs_disaster_id ON command_result_refs (disaster_id);
CREATE INDEX ix_command_result_refs_entitlement_version_id ON command_result_refs (entitlement_version_id);
CREATE INDEX ix_command_result_refs_evaluation_run_id ON command_result_refs (evaluation_run_id);
CREATE INDEX ix_command_result_refs_evidence_version_id ON command_result_refs (evidence_version_id);
CREATE INDEX ix_command_result_refs_fund_entry_id ON command_result_refs (fund_entry_id);
CREATE INDEX ix_command_result_refs_grievance_event_id ON command_result_refs (grievance_event_id);
CREATE INDEX ix_command_result_refs_handover_id ON command_result_refs (handover_id);
CREATE INDEX ix_command_result_refs_household_id ON command_result_refs (household_id);
CREATE INDEX ix_command_result_refs_household_version_id ON command_result_refs (household_version_id);
CREATE INDEX ix_command_result_refs_input_version_id ON command_result_refs (input_version_id);
CREATE INDEX ix_command_result_refs_link_version_id ON command_result_refs (link_version_id);
CREATE INDEX ix_command_result_refs_list_version_id ON command_result_refs (list_version_id);
CREATE INDEX ix_command_result_refs_notification_id ON command_result_refs (notification_id);
CREATE INDEX ix_command_result_refs_operation_version_id ON command_result_refs (operation_version_id);
CREATE INDEX ix_command_result_refs_outcome_version_id ON command_result_refs (outcome_version_id);
CREATE INDEX ix_command_result_refs_registry_review_id ON command_result_refs (registry_review_id);
CREATE INDEX ix_command_result_refs_response_id ON command_result_refs (response_id);
CREATE INDEX ix_command_result_refs_round_id ON command_result_refs (round_id);
CREATE INDEX ix_command_result_refs_session_version_id ON command_result_refs (session_version_id);
CREATE INDEX ix_command_result_refs_snapshot_id ON command_result_refs (snapshot_id);
CREATE INDEX ix_command_result_refs_submission_id ON command_result_refs (submission_id);
CREATE INDEX ix_command_result_refs_transaction_id ON command_result_refs (transaction_id);
CREATE INDEX ix_command_results_actor_id ON command_results (actor_id);
CREATE INDEX ix_commitments_deployment_id ON commitments (deployment_id);
CREATE INDEX ix_commitments_evidence_version_id ON commitments (evidence_version_id);
CREATE INDEX ix_commitments_fund_entry_id ON commitments (fund_entry_id);
CREATE INDEX ix_commitments_handover_id ON commitments (handover_id);
CREATE INDEX ix_commitments_input_version_id ON commitments (input_version_id);
CREATE INDEX ix_commitments_list_version_id ON commitments (list_version_id);
CREATE INDEX ix_commitments_outcome_version_id ON commitments (outcome_version_id);
CREATE INDEX ix_commitments_predecessor_commitment_id ON commitments (predecessor_commitment_id);
CREATE INDEX ix_commitments_public_id ON commitments (public_id);
CREATE INDEX ix_commitments_snapshot_id ON commitments (snapshot_id);
CREATE INDEX ix_credential_counters_pin_id ON credential_counters (pin_id);
CREATE INDEX ix_deployments_chain_id ON deployments (chain_id);
CREATE INDEX ix_disasters_current_input_version_id ON disasters (current_input_version_id);
CREATE INDEX ix_entitlement_versions_category_id ON entitlement_versions (category_id);
CREATE INDEX ix_entitlement_versions_decision_id ON entitlement_versions (decision_id);
CREATE INDEX ix_entitlement_versions_entitlement_id ON entitlement_versions (entitlement_id);
CREATE INDEX ix_entitlement_versions_input_version_id ON entitlement_versions (input_version_id);
CREATE INDEX ix_entitlement_versions_predecessor_id ON entitlement_versions (predecessor_id);
CREATE INDEX ix_entitlement_versions_registry_review_id ON entitlement_versions (registry_review_id);
CREATE INDEX ix_entitlement_versions_registry_version_id ON entitlement_versions (registry_version_id);
CREATE INDEX ix_entitlements_claim_id ON entitlements (claim_id);
CREATE INDEX ix_entitlements_current_version_id ON entitlements (current_version_id);
CREATE INDEX ix_entitlements_disaster_id ON entitlements (disaster_id);
CREATE INDEX ix_entitlements_household_id ON entitlements (household_id);
CREATE INDEX ix_evidence_links_amount_rule_id ON evidence_links (amount_rule_id);
CREATE INDEX ix_evidence_links_challenge_event_id ON evidence_links (challenge_event_id);
CREATE INDEX ix_evidence_links_clearance_id ON evidence_links (clearance_id);
CREATE INDEX ix_evidence_links_evidence_version_id ON evidence_links (evidence_version_id);
CREATE INDEX ix_evidence_links_fund_entry_id ON evidence_links (fund_entry_id);
CREATE INDEX ix_evidence_links_grievance_event_id ON evidence_links (grievance_event_id);
CREATE INDEX ix_evidence_links_household_version_id ON evidence_links (household_version_id);
CREATE INDEX ix_evidence_links_input_version_id ON evidence_links (input_version_id);
CREATE INDEX ix_evidence_links_nomination_id ON evidence_links (nomination_id);
CREATE INDEX ix_evidence_links_operation_version_id ON evidence_links (operation_version_id);
CREATE INDEX ix_evidence_links_registry_review_id ON evidence_links (registry_review_id);
CREATE INDEX ix_evidence_links_response_id ON evidence_links (response_id);
CREATE INDEX ix_evidence_links_snapshot_id ON evidence_links (snapshot_id);
CREATE INDEX ix_evidence_links_submission_id ON evidence_links (submission_id);
CREATE INDEX ix_evidence_versions_predecessor_id ON evidence_versions (predecessor_id);
CREATE INDEX ix_evidence_versions_prepared_for_actor_id ON evidence_versions (prepared_for_actor_id);
CREATE INDEX ix_fund_area_lines_entry_id ON fund_area_lines (entry_id);
CREATE INDEX ix_fund_correction_sets_original_entry_id ON fund_correction_sets (original_entry_id);
CREATE INDEX ix_fund_correction_sets_replacement_entry_id ON fund_correction_sets (replacement_entry_id);
CREATE INDEX ix_fund_correction_sets_reversal_entry_id ON fund_correction_sets (reversal_entry_id);
CREATE INDEX ix_fund_entries_correction_set_id ON fund_entries (correction_set_id);
CREATE INDEX ix_fund_entries_disaster_id ON fund_entries (disaster_id);
CREATE INDEX ix_fund_entries_original_entry_id ON fund_entries (original_entry_id);
CREATE INDEX ix_fund_entries_source_root_id ON fund_entries (source_root_id);
CREATE INDEX ix_fund_heads_current_entry_id ON fund_heads (current_entry_id);
CREATE INDEX ix_fund_heads_source_root_id ON fund_heads (source_root_id);
CREATE INDEX ix_fund_signatories_entry_id ON fund_signatories (entry_id);
CREATE INDEX ix_fund_signatories_validation_evidence_id ON fund_signatories (validation_evidence_id);
CREATE INDEX ix_grievance_events_grievance_id ON grievance_events (grievance_id);
CREATE INDEX ix_grievance_events_outcome_version_id ON grievance_events (outcome_version_id);
CREATE INDEX ix_grievance_events_predecessor_id ON grievance_events (predecessor_id);
CREATE INDEX ix_grievances_household_id ON grievances (household_id);
CREATE INDEX ix_grievances_transaction_id ON grievances (transaction_id);
CREATE INDEX ix_household_link_versions_basis_review_id ON household_link_versions (basis_review_id);
CREATE INDEX ix_household_link_versions_beneficiary_actor_id ON household_link_versions (beneficiary_actor_id);
CREATE INDEX ix_household_link_versions_household_id ON household_link_versions (household_id);
CREATE INDEX ix_household_link_versions_predecessor_id ON household_link_versions (predecessor_id);
CREATE INDEX ix_household_links_beneficiary_actor_id ON household_links (beneficiary_actor_id);
CREATE INDEX ix_household_links_household_id ON household_links (household_id);
CREATE INDEX ix_household_links_link_version_id ON household_links (link_version_id);
CREATE INDEX ix_household_members_household_id ON household_members (household_id);
CREATE INDEX ix_household_versions_assister_id ON household_versions (assister_id);
CREATE INDEX ix_household_versions_declared_barangay_id ON household_versions (declared_barangay_id);
CREATE INDEX ix_household_versions_head_photo_evidence_id ON household_versions (head_photo_evidence_id);
CREATE INDEX ix_household_versions_household_id ON household_versions (household_id);
CREATE INDEX ix_household_versions_id_evidence_id ON household_versions (id_evidence_id);
CREATE INDEX ix_household_versions_predecessor_id ON household_versions (predecessor_id);
CREATE INDEX ix_household_versions_registry_review_id ON household_versions (registry_review_id);
CREATE INDEX ix_households_current_pin_id ON households (current_pin_id);
CREATE INDEX ix_households_current_version_id ON households (current_version_id);
CREATE INDEX ix_households_display_id ON households (display_id);
CREATE INDEX ix_households_registered_without_id ON households (registered_without_id);
CREATE INDEX ix_identity_checks_household_version_id ON identity_checks (household_version_id);
CREATE INDEX ix_identity_checks_session_id ON identity_checks (session_id);
CREATE INDEX ix_legacy_records_deployment_id ON legacy_records (deployment_id);
CREATE INDEX ix_list_challenges_list_entry_id ON list_challenges (list_entry_id);
CREATE INDEX ix_list_challenges_reporting_household_id ON list_challenges (reporting_household_id);
CREATE INDEX ix_list_heads_barangay_id ON list_heads (barangay_id);
CREATE INDEX ix_list_heads_current_published_id ON list_heads (current_published_id);
CREATE INDEX ix_list_heads_disaster_id ON list_heads (disaster_id);
CREATE INDEX ix_list_heads_newest_requested_id ON list_heads (newest_requested_id);
CREATE INDEX ix_member_versions_household_version_id ON member_versions (household_version_id);
CREATE INDEX ix_member_versions_member_id ON member_versions (member_id);
CREATE INDEX ix_nominations_barangay_id ON nominations (barangay_id);
CREATE INDEX ix_nominations_candidate_actor_id ON nominations (candidate_actor_id);
CREATE INDEX ix_notification_attempts_notification_id ON notification_attempts (notification_id);
CREATE INDEX ix_notifications_decision_id ON notifications (decision_id);
CREATE INDEX ix_notifications_entitlement_version_id ON notifications (entitlement_version_id);
CREATE INDEX ix_notifications_household_id ON notifications (household_id);
CREATE INDEX ix_notifications_link_version_id ON notifications (link_version_id);
CREATE INDEX ix_notifications_operation_version_id ON notifications (operation_version_id);
CREATE INDEX ix_notifications_session_version_id ON notifications (session_version_id);
CREATE INDEX ix_operation_barangays_barangay_id ON operation_barangays (barangay_id);
CREATE INDEX ix_operation_barangays_operation_version_id ON operation_barangays (operation_version_id);
CREATE INDEX ix_operation_versions_operation_id ON operation_versions (operation_id);
CREATE INDEX ix_operation_versions_predecessor_id ON operation_versions (predecessor_id);
CREATE INDEX ix_outcome_versions_handover_id ON outcome_versions (handover_id);
CREATE INDEX ix_outcome_versions_predecessor_id ON outcome_versions (predecessor_id);
CREATE INDEX ix_outcome_versions_recorder_actor_id ON outcome_versions (recorder_actor_id);
CREATE INDEX ix_outcome_versions_transaction_id ON outcome_versions (transaction_id);
CREATE INDEX ix_paid_difference_events_handover_id ON paid_difference_events (handover_id);
CREATE INDEX ix_paid_difference_events_new_decision_id ON paid_difference_events (new_decision_id);
CREATE INDEX ix_paid_difference_events_new_input_version_id ON paid_difference_events (new_input_version_id);
CREATE INDEX ix_payout_attempts_current_id_check_id ON payout_attempts (current_id_check_id);
CREATE INDEX ix_payout_attempts_entitlement_version_id ON payout_attempts (entitlement_version_id);
CREATE INDEX ix_payout_attempts_recipient_actor_id ON payout_attempts (recipient_actor_id);
CREATE INDEX ix_payout_attempts_session_entry_id ON payout_attempts (session_entry_id);
CREATE INDEX ix_payout_attempts_transaction_id ON payout_attempts (transaction_id);
CREATE INDEX ix_payout_codes_attempt_id ON payout_codes (attempt_id);
CREATE INDEX ix_payout_sessions_barangay_id ON payout_sessions (barangay_id);
CREATE INDEX ix_payout_sessions_current_version_id ON payout_sessions (current_version_id);
CREATE INDEX ix_payout_sessions_disaster_id ON payout_sessions (disaster_id);
CREATE INDEX ix_payout_transactions_current_attempt_id ON payout_transactions (current_attempt_id);
CREATE INDEX ix_payout_transactions_current_outcome_id ON payout_transactions (current_outcome_id);
CREATE INDEX ix_payout_transactions_entitlement_id ON payout_transactions (entitlement_id);
CREATE INDEX ix_recorded_handovers_attempt_id ON recorded_handovers (attempt_id);
CREATE INDEX ix_recorded_handovers_checker_assignment_id ON recorded_handovers (checker_assignment_id);
CREATE INDEX ix_recorded_handovers_current_list_entry_id ON recorded_handovers (current_list_entry_id);
CREATE INDEX ix_recorded_handovers_current_session_entry_id ON recorded_handovers (current_session_entry_id);
CREATE INDEX ix_recorded_handovers_entitlement_id ON recorded_handovers (entitlement_id);
CREATE INDEX ix_recorded_handovers_entitlement_version_id ON recorded_handovers (entitlement_version_id);
CREATE INDEX ix_recorded_handovers_identity_check_id ON recorded_handovers (identity_check_id);
CREATE INDEX ix_recorded_handovers_input_version_id ON recorded_handovers (input_version_id);
CREATE INDEX ix_recorded_handovers_payer_id ON recorded_handovers (payer_id);
CREATE INDEX ix_recorded_handovers_recipient_actor_id ON recorded_handovers (recipient_actor_id);
CREATE INDEX ix_recorded_handovers_session_entry_id ON recorded_handovers (session_entry_id);
CREATE INDEX ix_recorded_handovers_session_version_id ON recorded_handovers (session_version_id);
CREATE INDEX ix_recorded_handovers_transaction_id ON recorded_handovers (transaction_id);
CREATE INDEX ix_registry_reviews_household_id ON registry_reviews (household_id);
CREATE INDEX ix_registry_reviews_prior_link_id ON registry_reviews (prior_link_id);
CREATE INDEX ix_registry_reviews_prior_version_id ON registry_reviews (prior_version_id);
CREATE INDEX ix_registry_reviews_result_link_id ON registry_reviews (result_link_id);
CREATE INDEX ix_registry_reviews_result_version_id ON registry_reviews (result_version_id);
CREATE INDEX ix_release_document_uses_evidence_version_id ON release_document_uses (evidence_version_id);
CREATE INDEX ix_release_document_uses_source_root_id ON release_document_uses (source_root_id);
CREATE INDEX ix_session_assignments_actor_id ON session_assignments (actor_id);
CREATE INDEX ix_session_assignments_session_version_id ON session_assignments (session_version_id);
CREATE INDEX ix_session_entries_entitlement_id ON session_entries (entitlement_id);
CREATE INDEX ix_session_entries_entitlement_version_id ON session_entries (entitlement_version_id);
CREATE INDEX ix_session_entries_list_entry_id ON session_entries (list_entry_id);
CREATE INDEX ix_session_entries_session_version_id ON session_entries (session_version_id);
CREATE INDEX ix_session_versions_original_list_version_id ON session_versions (original_list_version_id);
CREATE INDEX ix_session_versions_predecessor_id ON session_versions (predecessor_id);
CREATE INDEX ix_session_versions_session_id ON session_versions (session_id);
CREATE INDEX ix_snapshot_items_registry_version_id ON snapshot_items (registry_version_id);
CREATE INDEX ix_snapshot_items_round_id ON snapshot_items (round_id);
CREATE INDEX ix_snapshot_items_snapshot_id ON snapshot_items (snapshot_id);
CREATE INDEX ix_snapshot_items_submission_id ON snapshot_items (submission_id);
CREATE INDEX ix_snapshot_response_refs_response_id ON snapshot_response_refs (response_id);
CREATE INDEX ix_snapshot_response_refs_snapshot_id ON snapshot_response_refs (snapshot_id);
CREATE INDEX ix_submission_snapshots_barangay_id ON submission_snapshots (barangay_id);
CREATE INDEX ix_submission_snapshots_disaster_id ON submission_snapshots (disaster_id);
CREATE INDEX ix_submission_snapshots_resolution_evidence_id ON submission_snapshots (resolution_evidence_id);
CREATE INDEX ix_submission_snapshots_sender_id ON submission_snapshots (sender_id);
CREATE INDEX ix_transaction_clearances_stopped_attempt_id ON transaction_clearances (stopped_attempt_id);
CREATE INDEX ix_transaction_clearances_transaction_id ON transaction_clearances (transaction_id);
CREATE INDEX ix_transaction_notes_actor_id ON transaction_notes (actor_id);
CREATE INDEX ix_transaction_notes_transaction_id ON transaction_notes (transaction_id);
CREATE UNIQUE INDEX uq_active_attempt ON payout_attempts (transaction_id) WHERE business_status IN ('open','presented');
CREATE UNIQUE INDEX uq_active_run ON evaluation_runs (office_id) WHERE state='active';
CREATE UNIQUE INDEX uq_actor_member_links_initial ON actor_member_links (actor_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_actor_member_links_predecessor ON actor_member_links (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_actor_versions_initial ON actor_versions (actor_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_actor_versions_predecessor ON actor_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_amount_input_versions_initial ON amount_input_versions (disaster_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_amount_input_versions_predecessor ON amount_input_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_actor_version_id ON audit_targets (audit_event_id, actor_version_id) NULLS NOT DISTINCT WHERE actor_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_anchor_job_id ON audit_targets (audit_event_id, anchor_job_id) NULLS NOT DISTINCT WHERE anchor_job_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_attempt_event_id ON audit_targets (audit_event_id, attempt_event_id) NULLS NOT DISTINCT WHERE attempt_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_challenge_event_id ON audit_targets (audit_event_id, challenge_event_id) NULLS NOT DISTINCT WHERE challenge_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_check_run_id ON audit_targets (audit_event_id, check_run_id) NULLS NOT DISTINCT WHERE check_run_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_correction_set_id ON audit_targets (audit_event_id, correction_set_id) NULLS NOT DISTINCT WHERE correction_set_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_decision_id ON audit_targets (audit_event_id, decision_id) NULLS NOT DISTINCT WHERE decision_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_entitlement_version_id ON audit_targets (audit_event_id, entitlement_version_id) NULLS NOT DISTINCT WHERE entitlement_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_evaluation_run_id ON audit_targets (audit_event_id, evaluation_run_id) NULLS NOT DISTINCT WHERE evaluation_run_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_evidence_version_id ON audit_targets (audit_event_id, evidence_version_id) NULLS NOT DISTINCT WHERE evidence_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_fund_entry_id ON audit_targets (audit_event_id, fund_entry_id) NULLS NOT DISTINCT WHERE fund_entry_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_grievance_event_id ON audit_targets (audit_event_id, grievance_event_id) NULLS NOT DISTINCT WHERE grievance_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_handover_id ON audit_targets (audit_event_id, handover_id) NULLS NOT DISTINCT WHERE handover_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_household_version_id ON audit_targets (audit_event_id, household_version_id) NULLS NOT DISTINCT WHERE household_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_input_version_id ON audit_targets (audit_event_id, input_version_id) NULLS NOT DISTINCT WHERE input_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_link_version_id ON audit_targets (audit_event_id, link_version_id) NULLS NOT DISTINCT WHERE link_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_list_version_id ON audit_targets (audit_event_id, list_version_id) NULLS NOT DISTINCT WHERE list_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_notification_id ON audit_targets (audit_event_id, notification_id) NULLS NOT DISTINCT WHERE notification_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_operation_version_id ON audit_targets (audit_event_id, operation_version_id) NULLS NOT DISTINCT WHERE operation_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_outcome_version_id ON audit_targets (audit_event_id, outcome_version_id) NULLS NOT DISTINCT WHERE outcome_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_registry_review_id ON audit_targets (audit_event_id, registry_review_id) NULLS NOT DISTINCT WHERE registry_review_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_response_id ON audit_targets (audit_event_id, response_id) NULLS NOT DISTINCT WHERE response_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_round_id ON audit_targets (audit_event_id, round_id) NULLS NOT DISTINCT WHERE round_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_session_version_id ON audit_targets (audit_event_id, session_version_id) NULLS NOT DISTINCT WHERE session_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_snapshot_id ON audit_targets (audit_event_id, snapshot_id) NULLS NOT DISTINCT WHERE snapshot_id IS NOT NULL;
CREATE UNIQUE INDEX uq_audit_targets_submission_id ON audit_targets (audit_event_id, submission_id) NULLS NOT DISTINCT WHERE submission_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_actor_version_id ON auditor_access_targets (access_event_id, actor_version_id) NULLS NOT DISTINCT WHERE actor_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_anchor_job_id ON auditor_access_targets (access_event_id, anchor_job_id) NULLS NOT DISTINCT WHERE anchor_job_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_attempt_event_id ON auditor_access_targets (access_event_id, attempt_event_id) NULLS NOT DISTINCT WHERE attempt_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_challenge_event_id ON auditor_access_targets (access_event_id, challenge_event_id) NULLS NOT DISTINCT WHERE challenge_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_check_run_id ON auditor_access_targets (access_event_id, check_run_id) NULLS NOT DISTINCT WHERE check_run_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_claim_id ON auditor_access_targets (access_event_id, claim_id) NULLS NOT DISTINCT WHERE claim_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_commitment_id ON auditor_access_targets (access_event_id, commitment_id) NULLS NOT DISTINCT WHERE commitment_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_correction_set_id ON auditor_access_targets (access_event_id, correction_set_id) NULLS NOT DISTINCT WHERE correction_set_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_decision_id ON auditor_access_targets (access_event_id, decision_id) NULLS NOT DISTINCT WHERE decision_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_disaster_id ON auditor_access_targets (access_event_id, disaster_id) NULLS NOT DISTINCT WHERE disaster_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_entitlement_version_id ON auditor_access_targets (access_event_id, entitlement_version_id) NULLS NOT DISTINCT WHERE entitlement_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_evaluation_run_id ON auditor_access_targets (access_event_id, evaluation_run_id) NULLS NOT DISTINCT WHERE evaluation_run_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_evidence_version_id ON auditor_access_targets (access_event_id, evidence_version_id) NULLS NOT DISTINCT WHERE evidence_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_fund_entry_id ON auditor_access_targets (access_event_id, fund_entry_id) NULLS NOT DISTINCT WHERE fund_entry_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_grievance_event_id ON auditor_access_targets (access_event_id, grievance_event_id) NULLS NOT DISTINCT WHERE grievance_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_handover_id ON auditor_access_targets (access_event_id, handover_id) NULLS NOT DISTINCT WHERE handover_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_household_id ON auditor_access_targets (access_event_id, household_id) NULLS NOT DISTINCT WHERE household_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_household_version_id ON auditor_access_targets (access_event_id, household_version_id) NULLS NOT DISTINCT WHERE household_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_input_version_id ON auditor_access_targets (access_event_id, input_version_id) NULLS NOT DISTINCT WHERE input_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_link_version_id ON auditor_access_targets (access_event_id, link_version_id) NULLS NOT DISTINCT WHERE link_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_list_version_id ON auditor_access_targets (access_event_id, list_version_id) NULLS NOT DISTINCT WHERE list_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_notification_id ON auditor_access_targets (access_event_id, notification_id) NULLS NOT DISTINCT WHERE notification_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_operation_version_id ON auditor_access_targets (access_event_id, operation_version_id) NULLS NOT DISTINCT WHERE operation_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_outcome_version_id ON auditor_access_targets (access_event_id, outcome_version_id) NULLS NOT DISTINCT WHERE outcome_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_registry_review_id ON auditor_access_targets (access_event_id, registry_review_id) NULLS NOT DISTINCT WHERE registry_review_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_response_id ON auditor_access_targets (access_event_id, response_id) NULLS NOT DISTINCT WHERE response_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_round_id ON auditor_access_targets (access_event_id, round_id) NULLS NOT DISTINCT WHERE round_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_session_version_id ON auditor_access_targets (access_event_id, session_version_id) NULLS NOT DISTINCT WHERE session_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_snapshot_id ON auditor_access_targets (access_event_id, snapshot_id) NULLS NOT DISTINCT WHERE snapshot_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_submission_id ON auditor_access_targets (access_event_id, submission_id) NULLS NOT DISTINCT WHERE submission_id IS NOT NULL;
CREATE UNIQUE INDEX uq_auditor_access_targets_transaction_id ON auditor_access_targets (access_event_id, transaction_id) NULLS NOT DISTINCT WHERE transaction_id IS NOT NULL;
CREATE UNIQUE INDEX uq_challenge_events_initial ON challenge_events (challenge_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_challenge_events_predecessor ON challenge_events (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_claim_decisions_initial ON claim_decisions (claim_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_claim_decisions_predecessor ON claim_decisions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_claim_submissions_initial ON claim_submissions (claim_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_claim_submissions_predecessor ON claim_submissions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_actor_version_id ON command_result_refs (actor_id, command_name, idempotency_key, actor_version_id) NULLS NOT DISTINCT WHERE actor_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_anchor_job_id ON command_result_refs (actor_id, command_name, idempotency_key, anchor_job_id) NULLS NOT DISTINCT WHERE anchor_job_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_attempt_event_id ON command_result_refs (actor_id, command_name, idempotency_key, attempt_event_id) NULLS NOT DISTINCT WHERE attempt_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_challenge_event_id ON command_result_refs (actor_id, command_name, idempotency_key, challenge_event_id) NULLS NOT DISTINCT WHERE challenge_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_check_run_id ON command_result_refs (actor_id, command_name, idempotency_key, check_run_id) NULLS NOT DISTINCT WHERE check_run_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_claim_id ON command_result_refs (actor_id, command_name, idempotency_key, claim_id) NULLS NOT DISTINCT WHERE claim_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_commitment_id ON command_result_refs (actor_id, command_name, idempotency_key, commitment_id) NULLS NOT DISTINCT WHERE commitment_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_correction_set_id ON command_result_refs (actor_id, command_name, idempotency_key, correction_set_id) NULLS NOT DISTINCT WHERE correction_set_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_decision_id ON command_result_refs (actor_id, command_name, idempotency_key, decision_id) NULLS NOT DISTINCT WHERE decision_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_disaster_id ON command_result_refs (actor_id, command_name, idempotency_key, disaster_id) NULLS NOT DISTINCT WHERE disaster_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_entitlement_version_id ON command_result_refs (actor_id, command_name, idempotency_key, entitlement_version_id) NULLS NOT DISTINCT WHERE entitlement_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_evaluation_run_id ON command_result_refs (actor_id, command_name, idempotency_key, evaluation_run_id) NULLS NOT DISTINCT WHERE evaluation_run_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_evidence_version_id ON command_result_refs (actor_id, command_name, idempotency_key, evidence_version_id) NULLS NOT DISTINCT WHERE evidence_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_fund_entry_id ON command_result_refs (actor_id, command_name, idempotency_key, fund_entry_id) NULLS NOT DISTINCT WHERE fund_entry_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_grievance_event_id ON command_result_refs (actor_id, command_name, idempotency_key, grievance_event_id) NULLS NOT DISTINCT WHERE grievance_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_handover_id ON command_result_refs (actor_id, command_name, idempotency_key, handover_id) NULLS NOT DISTINCT WHERE handover_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_household_id ON command_result_refs (actor_id, command_name, idempotency_key, household_id) NULLS NOT DISTINCT WHERE household_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_household_version_id ON command_result_refs (actor_id, command_name, idempotency_key, household_version_id) NULLS NOT DISTINCT WHERE household_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_input_version_id ON command_result_refs (actor_id, command_name, idempotency_key, input_version_id) NULLS NOT DISTINCT WHERE input_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_link_version_id ON command_result_refs (actor_id, command_name, idempotency_key, link_version_id) NULLS NOT DISTINCT WHERE link_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_list_version_id ON command_result_refs (actor_id, command_name, idempotency_key, list_version_id) NULLS NOT DISTINCT WHERE list_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_notification_id ON command_result_refs (actor_id, command_name, idempotency_key, notification_id) NULLS NOT DISTINCT WHERE notification_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_operation_version_id ON command_result_refs (actor_id, command_name, idempotency_key, operation_version_id) NULLS NOT DISTINCT WHERE operation_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_outcome_version_id ON command_result_refs (actor_id, command_name, idempotency_key, outcome_version_id) NULLS NOT DISTINCT WHERE outcome_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_registry_review_id ON command_result_refs (actor_id, command_name, idempotency_key, registry_review_id) NULLS NOT DISTINCT WHERE registry_review_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_response_id ON command_result_refs (actor_id, command_name, idempotency_key, response_id) NULLS NOT DISTINCT WHERE response_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_round_id ON command_result_refs (actor_id, command_name, idempotency_key, round_id) NULLS NOT DISTINCT WHERE round_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_session_version_id ON command_result_refs (actor_id, command_name, idempotency_key, session_version_id) NULLS NOT DISTINCT WHERE session_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_snapshot_id ON command_result_refs (actor_id, command_name, idempotency_key, snapshot_id) NULLS NOT DISTINCT WHERE snapshot_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_submission_id ON command_result_refs (actor_id, command_name, idempotency_key, submission_id) NULLS NOT DISTINCT WHERE submission_id IS NOT NULL;
CREATE UNIQUE INDEX uq_command_result_refs_transaction_id ON command_result_refs (actor_id, command_name, idempotency_key, transaction_id) NULLS NOT DISTINCT WHERE transaction_id IS NOT NULL;
CREATE UNIQUE INDEX uq_current_beneficiary_link ON household_links (beneficiary_actor_id) WHERE beneficiary_actor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_entitlement_versions_initial ON entitlement_versions (entitlement_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_entitlement_versions_predecessor ON entitlement_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_amount_rule_id ON evidence_links (evidence_version_id, attachment_role, input_field, amount_rule_id) NULLS NOT DISTINCT WHERE amount_rule_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_challenge_event_id ON evidence_links (evidence_version_id, attachment_role, input_field, challenge_event_id) NULLS NOT DISTINCT WHERE challenge_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_clearance_id ON evidence_links (evidence_version_id, attachment_role, input_field, clearance_id) NULLS NOT DISTINCT WHERE clearance_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_fund_entry_id ON evidence_links (evidence_version_id, attachment_role, input_field, fund_entry_id) NULLS NOT DISTINCT WHERE fund_entry_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_grievance_event_id ON evidence_links (evidence_version_id, attachment_role, input_field, grievance_event_id) NULLS NOT DISTINCT WHERE grievance_event_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_household_version_id ON evidence_links (evidence_version_id, attachment_role, input_field, household_version_id) NULLS NOT DISTINCT WHERE household_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_input_version_id ON evidence_links (evidence_version_id, attachment_role, input_field, input_version_id) NULLS NOT DISTINCT WHERE input_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_nomination_id ON evidence_links (evidence_version_id, attachment_role, input_field, nomination_id) NULLS NOT DISTINCT WHERE nomination_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_operation_version_id ON evidence_links (evidence_version_id, attachment_role, input_field, operation_version_id) NULLS NOT DISTINCT WHERE operation_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_registry_review_id ON evidence_links (evidence_version_id, attachment_role, input_field, registry_review_id) NULLS NOT DISTINCT WHERE registry_review_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_response_id ON evidence_links (evidence_version_id, attachment_role, input_field, response_id) NULLS NOT DISTINCT WHERE response_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_snapshot_id ON evidence_links (evidence_version_id, attachment_role, input_field, snapshot_id) NULLS NOT DISTINCT WHERE snapshot_id IS NOT NULL;
CREATE UNIQUE INDEX uq_evidence_links_submission_id ON evidence_links (evidence_version_id, attachment_role, input_field, submission_id) NULLS NOT DISTINCT WHERE submission_id IS NOT NULL;
CREATE UNIQUE INDEX uq_grievance_events_initial ON grievance_events (grievance_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_grievance_events_predecessor ON grievance_events (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_household_link_versions_initial ON household_link_versions (household_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_household_link_versions_predecessor ON household_link_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_household_versions_initial ON household_versions (household_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_household_versions_predecessor ON household_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_initial_round ON claim_rounds (submission_id) WHERE referral_decision_id IS NULL;
CREATE UNIQUE INDEX uq_notifications_decision_id ON notifications (household_id, purpose, channel, decision_id) NULLS NOT DISTINCT WHERE decision_id IS NOT NULL;
CREATE UNIQUE INDEX uq_notifications_entitlement_version_id ON notifications (household_id, purpose, channel, entitlement_version_id) NULLS NOT DISTINCT WHERE entitlement_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_notifications_operation_version_id ON notifications (household_id, purpose, channel, operation_version_id) NULLS NOT DISTINCT WHERE operation_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_notifications_session_version_id ON notifications (household_id, purpose, channel, session_version_id) NULLS NOT DISTINCT WHERE session_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_one_head ON member_versions (household_version_id) WHERE is_head;
CREATE UNIQUE INDEX uq_one_timeout ON outcome_versions (transaction_id) WHERE answer='unconfirmed';
CREATE UNIQUE INDEX uq_operation_versions_initial ON operation_versions (operation_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_operation_versions_predecessor ON operation_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_outcome_versions_initial ON outcome_versions (transaction_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_outcome_versions_predecessor ON outcome_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
CREATE UNIQUE INDEX uq_paid_difference_basis ON paid_difference_events (handover_id, new_input_version_id, new_decision_id) NULLS NOT DISTINCT;
CREATE UNIQUE INDEX uq_referral_round ON claim_rounds (referral_decision_id) WHERE referral_decision_id IS NOT NULL;
CREATE UNIQUE INDEX uq_session_versions_initial ON session_versions (session_id) WHERE predecessor_id IS NULL;
CREATE UNIQUE INDEX uq_session_versions_predecessor ON session_versions (predecessor_id) WHERE predecessor_id IS NOT NULL;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_basis_review_id FOREIGN KEY(run_id, office_id, basis_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_member_id FOREIGN KEY(run_id, office_id, member_id) REFERENCES household_members (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES actor_member_links (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_predecessor_parent FOREIGN KEY(run_id, office_id, actor_id, predecessor_id) REFERENCES actor_member_links (run_id, office_id, actor_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_member_links ADD CONSTRAINT fk_actor_member_links_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_approved_by FOREIGN KEY(run_id, office_id, approved_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_barangay_id FOREIGN KEY(run_id, office_id, barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_nomination_id FOREIGN KEY(run_id, office_id, nomination_id) REFERENCES nominations (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES actor_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_predecessor_parent FOREIGN KEY(run_id, office_id, actor_id, predecessor_id) REFERENCES actor_versions (run_id, office_id, actor_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT fk_actor_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actor_versions ADD CONSTRAINT rel_actor_versions_actor_id_nomination_id FOREIGN KEY(run_id, office_id, actor_id, nomination_id) REFERENCES nominations (run_id, office_id, candidate_actor_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actors ADD CONSTRAINT fk_actors_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actors ADD CONSTRAINT fk_actors_current_member_link_id FOREIGN KEY(run_id, office_id, current_member_link_id) REFERENCES actor_member_links (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actors ADD CONSTRAINT fk_actors_current_version_id FOREIGN KEY(run_id, office_id, current_version_id) REFERENCES actor_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actors ADD CONSTRAINT fk_actors_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actors ADD CONSTRAINT rel_actors_id_current_member_link_id FOREIGN KEY(run_id, office_id, id, current_member_link_id) REFERENCES actor_member_links (run_id, office_id, actor_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE actors ADD CONSTRAINT rel_actors_id_current_version_id FOREIGN KEY(run_id, office_id, id, current_version_id) REFERENCES actor_versions (run_id, office_id, actor_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE amount_input_versions ADD CONSTRAINT fk_amount_input_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE amount_input_versions ADD CONSTRAINT fk_amount_input_versions_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE amount_input_versions ADD CONSTRAINT fk_amount_input_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE amount_input_versions ADD CONSTRAINT fk_amount_input_versions_predecessor_parent FOREIGN KEY(run_id, office_id, disaster_id, predecessor_id) REFERENCES amount_input_versions (run_id, office_id, disaster_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE amount_input_versions ADD CONSTRAINT fk_amount_input_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_display_category_id FOREIGN KEY(run_id, office_id, display_category_id) REFERENCES damage_categories (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_display_decision_id FOREIGN KEY(run_id, office_id, display_decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_entitlement_id FOREIGN KEY(run_id, office_id, entitlement_id) REFERENCES entitlements (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_list_version_id FOREIGN KEY(run_id, office_id, list_version_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_registry_version_id FOREIGN KEY(run_id, office_id, registry_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT fk_approved_list_entries_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_entries ADD CONSTRAINT rel_approved_list_entries_entitlement_id_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, entitlement_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_versions ADD CONSTRAINT fk_approved_list_versions_basis_input_version_id FOREIGN KEY(run_id, office_id, basis_input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_versions ADD CONSTRAINT fk_approved_list_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_versions ADD CONSTRAINT fk_approved_list_versions_list_head_id FOREIGN KEY(run_id, office_id, list_head_id) REFERENCES list_heads (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_versions ADD CONSTRAINT fk_approved_list_versions_predecessor_published_id FOREIGN KEY(run_id, office_id, predecessor_published_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE approved_list_versions ADD CONSTRAINT fk_approved_list_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE assisted_pins ADD CONSTRAINT fk_assisted_pins_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE assisted_pins ADD CONSTRAINT fk_assisted_pins_established_after_check_id FOREIGN KEY(run_id, office_id, established_after_check_id) REFERENCES identity_checks (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE assisted_pins ADD CONSTRAINT fk_assisted_pins_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE assisted_pins ADD CONSTRAINT fk_assisted_pins_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE barangays ADD CONSTRAINT fk_barangays_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE barangays ADD CONSTRAINT fk_barangays_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE challenge_events ADD CONSTRAINT fk_challenge_events_challenge_id FOREIGN KEY(run_id, office_id, challenge_id) REFERENCES list_challenges (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE challenge_events ADD CONSTRAINT fk_challenge_events_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE challenge_events ADD CONSTRAINT fk_challenge_events_decision_id FOREIGN KEY(run_id, office_id, decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE challenge_events ADD CONSTRAINT fk_challenge_events_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES challenge_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE challenge_events ADD CONSTRAINT fk_challenge_events_predecessor_parent FOREIGN KEY(run_id, office_id, challenge_id, predecessor_id) REFERENCES challenge_events (run_id, office_id, challenge_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE challenge_events ADD CONSTRAINT fk_challenge_events_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE check_runs ADD CONSTRAINT fk_check_runs_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE check_runs ADD CONSTRAINT fk_check_runs_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE check_runs ADD CONSTRAINT fk_check_runs_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE check_runs ADD CONSTRAINT fk_check_runs_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_category_id FOREIGN KEY(run_id, office_id, category_id) REFERENCES damage_categories (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_challenge_event_id FOREIGN KEY(run_id, office_id, challenge_event_id) REFERENCES challenge_events (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_check_run_id FOREIGN KEY(run_id, office_id, check_run_id) REFERENCES check_runs (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_claim_id FOREIGN KEY(run_id, office_id, claim_id) REFERENCES claims (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_confirmed_by FOREIGN KEY(run_id, office_id, confirmed_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_predecessor_parent FOREIGN KEY(run_id, office_id, claim_id, predecessor_id) REFERENCES claim_decisions (run_id, office_id, claim_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_decisions ADD CONSTRAINT fk_claim_decisions_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_operations ADD CONSTRAINT fk_claim_operations_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_operations ADD CONSTRAINT fk_claim_operations_current_version_id FOREIGN KEY(run_id, office_id, current_version_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_operations ADD CONSTRAINT fk_claim_operations_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_operations ADD CONSTRAINT fk_claim_operations_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_operations ADD CONSTRAINT rel_claim_operations_id_current_version_id FOREIGN KEY(run_id, office_id, id, current_version_id) REFERENCES operation_versions (run_id, office_id, operation_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT fk_claim_responses_actor_id FOREIGN KEY(run_id, office_id, actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT fk_claim_responses_category_opinion_id FOREIGN KEY(run_id, office_id, category_opinion_id) REFERENCES damage_categories (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT fk_claim_responses_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT fk_claim_responses_parent_response_id FOREIGN KEY(run_id, office_id, parent_response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT fk_claim_responses_round_id FOREIGN KEY(run_id, office_id, round_id) REFERENCES claim_rounds (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT fk_claim_responses_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_responses ADD CONSTRAINT rel_claim_responses_round_id_parent_response_id FOREIGN KEY(run_id, office_id, round_id, parent_response_id) REFERENCES claim_responses (run_id, office_id, round_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_rounds ADD CONSTRAINT fk_claim_rounds_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_rounds ADD CONSTRAINT fk_claim_rounds_primary_snapshot_id FOREIGN KEY(run_id, office_id, primary_snapshot_id) REFERENCES submission_snapshots (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_rounds ADD CONSTRAINT fk_claim_rounds_referral_decision_id FOREIGN KEY(run_id, office_id, referral_decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_rounds ADD CONSTRAINT fk_claim_rounds_routed_response_id FOREIGN KEY(run_id, office_id, routed_response_id) REFERENCES claim_responses (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_rounds ADD CONSTRAINT fk_claim_rounds_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_rounds ADD CONSTRAINT fk_claim_rounds_submission_id FOREIGN KEY(run_id, office_id, submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_claim_id FOREIGN KEY(run_id, office_id, claim_id) REFERENCES claims (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_link_version_id FOREIGN KEY(run_id, office_id, link_version_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_predecessor_parent FOREIGN KEY(run_id, office_id, claim_id, predecessor_id) REFERENCES claim_submissions (run_id, office_id, claim_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_registry_version_id FOREIGN KEY(run_id, office_id, registry_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claim_submissions ADD CONSTRAINT fk_claim_submissions_stated_category_id FOREIGN KEY(run_id, office_id, stated_category_id) REFERENCES damage_categories (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_current_decision_id FOREIGN KEY(run_id, office_id, current_decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_current_submission_id FOREIGN KEY(run_id, office_id, current_submission_id) REFERENCES claim_submissions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_operation_id FOREIGN KEY(run_id, office_id, operation_id) REFERENCES claim_operations (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT fk_claims_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT rel_claims_id_current_decision_id FOREIGN KEY(run_id, office_id, id, current_decision_id) REFERENCES claim_decisions (run_id, office_id, claim_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE claims ADD CONSTRAINT rel_claims_id_current_submission_id FOREIGN KEY(run_id, office_id, id, current_submission_id) REFERENCES claim_submissions (run_id, office_id, claim_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE disasters ADD CONSTRAINT fk_disasters_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE disasters ADD CONSTRAINT fk_disasters_current_input_version_id FOREIGN KEY(run_id, office_id, current_input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE disasters ADD CONSTRAINT fk_disasters_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE disasters ADD CONSTRAINT rel_disasters_id_current_input_version_id FOREIGN KEY(run_id, office_id, id, current_input_version_id) REFERENCES amount_input_versions (run_id, office_id, disaster_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_category_id FOREIGN KEY(run_id, office_id, category_id) REFERENCES damage_categories (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_decision_id FOREIGN KEY(run_id, office_id, decision_id) REFERENCES claim_decisions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_entitlement_id FOREIGN KEY(run_id, office_id, entitlement_id) REFERENCES entitlements (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_predecessor_parent FOREIGN KEY(run_id, office_id, entitlement_id, predecessor_id) REFERENCES entitlement_versions (run_id, office_id, entitlement_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_registry_version_id FOREIGN KEY(run_id, office_id, registry_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlement_versions ADD CONSTRAINT fk_entitlement_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT fk_entitlements_claim_id FOREIGN KEY(run_id, office_id, claim_id) REFERENCES claims (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT fk_entitlements_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT fk_entitlements_current_version_id FOREIGN KEY(run_id, office_id, current_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT fk_entitlements_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT fk_entitlements_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT fk_entitlements_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE entitlements ADD CONSTRAINT rel_entitlements_id_current_version_id FOREIGN KEY(run_id, office_id, id, current_version_id) REFERENCES entitlement_versions (run_id, office_id, entitlement_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE evidence_versions ADD CONSTRAINT fk_evidence_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE evidence_versions ADD CONSTRAINT fk_evidence_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE evidence_versions ADD CONSTRAINT fk_evidence_versions_prepared_for_actor_id FOREIGN KEY(run_id, office_id, prepared_for_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE evidence_versions ADD CONSTRAINT fk_evidence_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE evidence_versions ADD CONSTRAINT fk_evidence_versions_uploaded_by FOREIGN KEY(run_id, office_id, uploaded_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_correction_sets ADD CONSTRAINT fk_fund_correction_sets_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_correction_sets ADD CONSTRAINT fk_fund_correction_sets_original_entry_id FOREIGN KEY(run_id, office_id, original_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_correction_sets ADD CONSTRAINT fk_fund_correction_sets_replacement_entry_id FOREIGN KEY(run_id, office_id, replacement_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_correction_sets ADD CONSTRAINT fk_fund_correction_sets_reversal_entry_id FOREIGN KEY(run_id, office_id, reversal_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_correction_sets ADD CONSTRAINT fk_fund_correction_sets_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_approved_by FOREIGN KEY(run_id, office_id, approved_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_correction_set_id FOREIGN KEY(run_id, office_id, correction_set_id) REFERENCES fund_correction_sets (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_entered_by FOREIGN KEY(run_id, office_id, entered_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_original_entry_id FOREIGN KEY(run_id, office_id, original_entry_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE fund_entries ADD CONSTRAINT fk_fund_entries_source_root_id FOREIGN KEY(run_id, office_id, source_root_id) REFERENCES fund_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_basis_review_id FOREIGN KEY(run_id, office_id, basis_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_beneficiary_actor_id FOREIGN KEY(run_id, office_id, beneficiary_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_predecessor_parent FOREIGN KEY(run_id, office_id, household_id, predecessor_id) REFERENCES household_link_versions (run_id, office_id, household_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_link_versions ADD CONSTRAINT fk_household_link_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_members ADD CONSTRAINT fk_household_members_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_members ADD CONSTRAINT fk_household_members_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_members ADD CONSTRAINT fk_household_members_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_assister_id FOREIGN KEY(run_id, office_id, assister_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_declared_barangay_id FOREIGN KEY(run_id, office_id, declared_barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_head_photo_evidence_id FOREIGN KEY(run_id, office_id, head_photo_evidence_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_id_evidence_id FOREIGN KEY(run_id, office_id, id_evidence_id) REFERENCES evidence_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_predecessor_parent FOREIGN KEY(run_id, office_id, household_id, predecessor_id) REFERENCES household_versions (run_id, office_id, household_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_registry_review_id FOREIGN KEY(run_id, office_id, registry_review_id) REFERENCES registry_reviews (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE household_versions ADD CONSTRAINT fk_household_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE households ADD CONSTRAINT fk_households_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE households ADD CONSTRAINT fk_households_current_pin_id FOREIGN KEY(run_id, office_id, current_pin_id) REFERENCES assisted_pins (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE households ADD CONSTRAINT fk_households_current_version_id FOREIGN KEY(run_id, office_id, current_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE households ADD CONSTRAINT fk_households_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE households ADD CONSTRAINT rel_households_id_current_pin_id FOREIGN KEY(run_id, office_id, id, current_pin_id) REFERENCES assisted_pins (run_id, office_id, household_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE households ADD CONSTRAINT rel_households_id_current_version_id FOREIGN KEY(run_id, office_id, id, current_version_id) REFERENCES household_versions (run_id, office_id, household_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE identity_checks ADD CONSTRAINT fk_identity_checks_checked_by FOREIGN KEY(run_id, office_id, checked_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE identity_checks ADD CONSTRAINT fk_identity_checks_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE identity_checks ADD CONSTRAINT fk_identity_checks_household_version_id FOREIGN KEY(run_id, office_id, household_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE identity_checks ADD CONSTRAINT fk_identity_checks_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE identity_checks ADD CONSTRAINT fk_identity_checks_session_id FOREIGN KEY(run_id, office_id, session_id) REFERENCES payout_sessions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_challenges ADD CONSTRAINT fk_list_challenges_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_challenges ADD CONSTRAINT fk_list_challenges_list_entry_id FOREIGN KEY(run_id, office_id, list_entry_id) REFERENCES approved_list_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_challenges ADD CONSTRAINT fk_list_challenges_reporting_household_id FOREIGN KEY(run_id, office_id, reporting_household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_challenges ADD CONSTRAINT fk_list_challenges_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT fk_list_heads_barangay_id FOREIGN KEY(run_id, office_id, barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT fk_list_heads_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT fk_list_heads_current_published_id FOREIGN KEY(run_id, office_id, current_published_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT fk_list_heads_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT fk_list_heads_newest_requested_id FOREIGN KEY(run_id, office_id, newest_requested_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT fk_list_heads_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT rel_list_heads_id_current_published_id FOREIGN KEY(run_id, office_id, id, current_published_id) REFERENCES approved_list_versions (run_id, office_id, list_head_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE list_heads ADD CONSTRAINT rel_list_heads_id_newest_requested_id FOREIGN KEY(run_id, office_id, id, newest_requested_id) REFERENCES approved_list_versions (run_id, office_id, list_head_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE nominations ADD CONSTRAINT fk_nominations_barangay_id FOREIGN KEY(run_id, office_id, barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE nominations ADD CONSTRAINT fk_nominations_candidate_actor_id FOREIGN KEY(run_id, office_id, candidate_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE nominations ADD CONSTRAINT fk_nominations_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE nominations ADD CONSTRAINT fk_nominations_entered_by FOREIGN KEY(run_id, office_id, entered_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE nominations ADD CONSTRAINT fk_nominations_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE operation_versions ADD CONSTRAINT fk_operation_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE operation_versions ADD CONSTRAINT fk_operation_versions_operation_id FOREIGN KEY(run_id, office_id, operation_id) REFERENCES claim_operations (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE operation_versions ADD CONSTRAINT fk_operation_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES operation_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE operation_versions ADD CONSTRAINT fk_operation_versions_predecessor_parent FOREIGN KEY(run_id, office_id, operation_id, predecessor_id) REFERENCES operation_versions (run_id, office_id, operation_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE operation_versions ADD CONSTRAINT fk_operation_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_handover_id FOREIGN KEY(run_id, office_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_predecessor_parent FOREIGN KEY(run_id, office_id, transaction_id, predecessor_id) REFERENCES outcome_versions (run_id, office_id, transaction_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_recorder_actor_id FOREIGN KEY(run_id, office_id, recorder_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT fk_outcome_versions_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE outcome_versions ADD CONSTRAINT rel_outcome_versions_transaction_id_handover_id FOREIGN KEY(run_id, office_id, transaction_id, handover_id) REFERENCES recorded_handovers (run_id, office_id, transaction_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_current_id_check_id FOREIGN KEY(run_id, office_id, current_id_check_id) REFERENCES identity_checks (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_recipient_actor_id FOREIGN KEY(run_id, office_id, recipient_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_session_entry_id FOREIGN KEY(run_id, office_id, session_entry_id) REFERENCES session_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT fk_payout_attempts_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_attempts ADD CONSTRAINT rel_payout_attempts_session_entry_id_entitlement_version_id FOREIGN KEY(run_id, office_id, session_entry_id, entitlement_version_id) REFERENCES session_entries (run_id, office_id, id, entitlement_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_sessions ADD CONSTRAINT fk_payout_sessions_barangay_id FOREIGN KEY(run_id, office_id, barangay_id) REFERENCES barangays (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_sessions ADD CONSTRAINT fk_payout_sessions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_sessions ADD CONSTRAINT fk_payout_sessions_current_version_id FOREIGN KEY(run_id, office_id, current_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_sessions ADD CONSTRAINT fk_payout_sessions_disaster_id FOREIGN KEY(run_id, office_id, disaster_id) REFERENCES disasters (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_sessions ADD CONSTRAINT fk_payout_sessions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_sessions ADD CONSTRAINT rel_payout_sessions_id_current_version_id FOREIGN KEY(run_id, office_id, id, current_version_id) REFERENCES session_versions (run_id, office_id, session_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT fk_payout_transactions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT fk_payout_transactions_current_attempt_id FOREIGN KEY(run_id, office_id, current_attempt_id) REFERENCES payout_attempts (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT fk_payout_transactions_current_outcome_id FOREIGN KEY(run_id, office_id, current_outcome_id) REFERENCES outcome_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT fk_payout_transactions_entitlement_id FOREIGN KEY(run_id, office_id, entitlement_id) REFERENCES entitlements (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT fk_payout_transactions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT rel_payout_transactions_id_current_attempt_id FOREIGN KEY(run_id, office_id, id, current_attempt_id) REFERENCES payout_attempts (run_id, office_id, transaction_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE payout_transactions ADD CONSTRAINT rel_payout_transactions_id_current_outcome_id FOREIGN KEY(run_id, office_id, id, current_outcome_id) REFERENCES outcome_versions (run_id, office_id, transaction_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_attempt_id FOREIGN KEY(run_id, office_id, attempt_id) REFERENCES payout_attempts (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_checker_assignment_id FOREIGN KEY(run_id, office_id, checker_assignment_id) REFERENCES session_assignments (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_current_list_entry_id FOREIGN KEY(run_id, office_id, current_list_entry_id) REFERENCES approved_list_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_current_session_entry_id FOREIGN KEY(run_id, office_id, current_session_entry_id) REFERENCES session_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_entitlement_id FOREIGN KEY(run_id, office_id, entitlement_id) REFERENCES entitlements (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_entitlement_version_id FOREIGN KEY(run_id, office_id, entitlement_version_id) REFERENCES entitlement_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_identity_check_id FOREIGN KEY(run_id, office_id, identity_check_id) REFERENCES identity_checks (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_input_version_id FOREIGN KEY(run_id, office_id, input_version_id) REFERENCES amount_input_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_payer_id FOREIGN KEY(run_id, office_id, payer_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_recipient_actor_id FOREIGN KEY(run_id, office_id, recipient_actor_id) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_session_entry_id FOREIGN KEY(run_id, office_id, session_entry_id) REFERENCES session_entries (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_session_version_id FOREIGN KEY(run_id, office_id, session_version_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT fk_recorded_handovers_transaction_id FOREIGN KEY(run_id, office_id, transaction_id) REFERENCES payout_transactions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT rel_recorded_handovers_current_list_entry_id_entitlemen_68bd FOREIGN KEY(run_id, office_id, current_list_entry_id, entitlement_id, entitlement_version_id) REFERENCES approved_list_entries (run_id, office_id, id, entitlement_id, entitlement_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT rel_recorded_handovers_current_session_entry_id_session_bde5 FOREIGN KEY(run_id, office_id, current_session_entry_id, session_version_id, entitlement_id, entitlement_version_id) REFERENCES session_entries (run_id, office_id, id, session_version_id, entitlement_id, entitlement_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT rel_recorded_handovers_entitlement_id_entitlement_versi_7b43 FOREIGN KEY(run_id, office_id, entitlement_id, entitlement_version_id, amount_centavos, input_version_id) REFERENCES entitlement_versions (run_id, office_id, entitlement_id, id, amount_centavos, input_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT rel_recorded_handovers_session_entry_id_entitlement_id__f29c FOREIGN KEY(run_id, office_id, session_entry_id, entitlement_id, entitlement_version_id) REFERENCES session_entries (run_id, office_id, id, entitlement_id, entitlement_version_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE recorded_handovers ADD CONSTRAINT rel_recorded_handovers_transaction_id_attempt_id FOREIGN KEY(run_id, office_id, transaction_id, attempt_id) REFERENCES payout_attempts (run_id, office_id, transaction_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_household_id FOREIGN KEY(run_id, office_id, household_id) REFERENCES households (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_prior_link_id FOREIGN KEY(run_id, office_id, prior_link_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_prior_version_id FOREIGN KEY(run_id, office_id, prior_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_result_link_id FOREIGN KEY(run_id, office_id, result_link_id) REFERENCES household_link_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_result_version_id FOREIGN KEY(run_id, office_id, result_version_id) REFERENCES household_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE registry_reviews ADD CONSTRAINT fk_registry_reviews_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE session_versions ADD CONSTRAINT fk_session_versions_created_by FOREIGN KEY(run_id, office_id, created_by) REFERENCES actors (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE session_versions ADD CONSTRAINT fk_session_versions_original_list_version_id FOREIGN KEY(run_id, office_id, original_list_version_id) REFERENCES approved_list_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE session_versions ADD CONSTRAINT fk_session_versions_predecessor_id FOREIGN KEY(run_id, office_id, predecessor_id) REFERENCES session_versions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE session_versions ADD CONSTRAINT fk_session_versions_predecessor_parent FOREIGN KEY(run_id, office_id, session_id, predecessor_id) REFERENCES session_versions (run_id, office_id, session_id, id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE session_versions ADD CONSTRAINT fk_session_versions_run_id_evaluation_runs FOREIGN KEY(run_id, office_id) REFERENCES evaluation_runs (id, office_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE session_versions ADD CONSTRAINT fk_session_versions_session_id FOREIGN KEY(run_id, office_id, session_id) REFERENCES payout_sessions (run_id, office_id, id) DEFERRABLE INITIALLY DEFERRED;
CREATE SEQUENCE audit_sequence;
CREATE FUNCTION immutable_fact() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'append-only history' USING ERRCODE='55000'; END $$;
CREATE TRIGGER immutable_actor_member_links BEFORE UPDATE OR DELETE ON actor_member_links FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_actor_versions BEFORE UPDATE OR DELETE ON actor_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_amount_input_versions BEFORE UPDATE OR DELETE ON amount_input_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_amount_rules BEFORE UPDATE OR DELETE ON amount_rules FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_anchor_applications BEFORE UPDATE OR DELETE ON anchor_applications FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_anchor_dependencies BEFORE UPDATE OR DELETE ON anchor_dependencies FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_anchor_job_items BEFORE UPDATE OR DELETE ON anchor_job_items FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_anchor_observations BEFORE UPDATE OR DELETE ON anchor_observations FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_anchor_submission_events BEFORE UPDATE OR DELETE ON anchor_submission_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_anchor_submissions BEFORE UPDATE OR DELETE ON anchor_submissions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_approved_list_entries BEFORE UPDATE OR DELETE ON approved_list_entries FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_assisted_pins BEFORE UPDATE OR DELETE ON assisted_pins FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_attempt_events BEFORE UPDATE OR DELETE ON attempt_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_audit_events BEFORE UPDATE OR DELETE ON audit_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_audit_targets BEFORE UPDATE OR DELETE ON audit_targets FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_auditor_access_events BEFORE UPDATE OR DELETE ON auditor_access_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_auditor_access_targets BEFORE UPDATE OR DELETE ON auditor_access_targets FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_challenge_events BEFORE UPDATE OR DELETE ON challenge_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_check_flags BEFORE UPDATE OR DELETE ON check_flags FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_check_runs BEFORE UPDATE OR DELETE ON check_runs FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_claim_decisions BEFORE UPDATE OR DELETE ON claim_decisions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_claim_responses BEFORE UPDATE OR DELETE ON claim_responses FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_claim_submissions BEFORE UPDATE OR DELETE ON claim_submissions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_command_result_refs BEFORE UPDATE OR DELETE ON command_result_refs FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_command_results BEFORE UPDATE OR DELETE ON command_results FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_commitments BEFORE UPDATE OR DELETE ON commitments FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_damage_categories BEFORE UPDATE OR DELETE ON damage_categories FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_entitlement_versions BEFORE UPDATE OR DELETE ON entitlement_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_evidence_links BEFORE UPDATE OR DELETE ON evidence_links FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_evidence_versions BEFORE UPDATE OR DELETE ON evidence_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_fund_area_lines BEFORE UPDATE OR DELETE ON fund_area_lines FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_fund_correction_sets BEFORE UPDATE OR DELETE ON fund_correction_sets FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_fund_entries BEFORE UPDATE OR DELETE ON fund_entries FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_fund_signatories BEFORE UPDATE OR DELETE ON fund_signatories FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_grievance_events BEFORE UPDATE OR DELETE ON grievance_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_household_link_versions BEFORE UPDATE OR DELETE ON household_link_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_household_members BEFORE UPDATE OR DELETE ON household_members FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_household_versions BEFORE UPDATE OR DELETE ON household_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_identity_checks BEFORE UPDATE OR DELETE ON identity_checks FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_legacy_records BEFORE UPDATE OR DELETE ON legacy_records FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_member_versions BEFORE UPDATE OR DELETE ON member_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_nominations BEFORE UPDATE OR DELETE ON nominations FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_notification_attempts BEFORE UPDATE OR DELETE ON notification_attempts FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_operation_barangays BEFORE UPDATE OR DELETE ON operation_barangays FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_operation_versions BEFORE UPDATE OR DELETE ON operation_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_outcome_versions BEFORE UPDATE OR DELETE ON outcome_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_paid_difference_events BEFORE UPDATE OR DELETE ON paid_difference_events FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_recorded_handovers BEFORE UPDATE OR DELETE ON recorded_handovers FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_registry_reviews BEFORE UPDATE OR DELETE ON registry_reviews FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_release_document_uses BEFORE UPDATE OR DELETE ON release_document_uses FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_session_assignments BEFORE UPDATE OR DELETE ON session_assignments FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_session_entries BEFORE UPDATE OR DELETE ON session_entries FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_session_versions BEFORE UPDATE OR DELETE ON session_versions FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_snapshot_items BEFORE UPDATE OR DELETE ON snapshot_items FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_snapshot_response_refs BEFORE UPDATE OR DELETE ON snapshot_response_refs FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_submission_snapshots BEFORE UPDATE OR DELETE ON submission_snapshots FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_transaction_clearances BEFORE UPDATE OR DELETE ON transaction_clearances FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE TRIGGER immutable_transaction_notes BEFORE UPDATE OR DELETE ON transaction_notes FOR EACH ROW EXECUTE FUNCTION immutable_fact();
CREATE FUNCTION frozen_content() RETURNS trigger LANGUAGE plpgsql AS $$
       DECLARE allowed text[]:=string_to_array(TG_ARGV[0],',');
       BEGIN
         IF TG_OP='DELETE' OR (to_jsonb(NEW)-allowed) IS DISTINCT FROM (to_jsonb(OLD)-allowed)
         THEN RAISE EXCEPTION 'immutable content' USING ERRCODE='55000'; END IF;
         RETURN NEW;
       END $$;
CREATE TRIGGER frozen_approved_list_versions BEFORE UPDATE OR DELETE ON approved_list_versions FOR EACH ROW EXECUTE FUNCTION frozen_content('business_status,published_at');
CREATE TRIGGER frozen_claim_rounds BEFORE UPDATE OR DELETE ON claim_rounds FOR EACH ROW EXECUTE FUNCTION frozen_content('primary_snapshot_id,revision,route_kind,routed_response_id,state');
CREATE TRIGGER frozen_deployments BEFORE UPDATE OR DELETE ON deployments FOR EACH ROW EXECUTE FUNCTION frozen_content('state');
CREATE TRIGGER frozen_notifications BEFORE UPDATE OR DELETE ON notifications FOR EACH ROW EXECUTE FUNCTION frozen_content('state');
CREATE TRIGGER frozen_payout_attempts BEFORE UPDATE OR DELETE ON payout_attempts FOR EACH ROW EXECUTE FUNCTION frozen_content('bad_code_count,business_status,current_id_check_id');
CREATE TRIGGER frozen_payout_codes BEFORE UPDATE OR DELETE ON payout_codes FOR EACH ROW EXECUTE FUNCTION frozen_content('consumed_at');
CREATE FUNCTION require_audit_target() RETURNS trigger LANGUAGE plpgsql AS $$
       DECLARE found boolean;
       BEGIN
         EXECUTE format('SELECT EXISTS(SELECT 1 FROM audit_targets WHERE %I=$1)',TG_ARGV[0]) INTO found USING NEW.id;
         IF NOT found THEN RAISE EXCEPTION 'business change requires typed audit' USING ERRCODE='23514'; END IF;
         RETURN NEW;
       END $$;
CREATE CONSTRAINT TRIGGER audit_actor_versions AFTER INSERT ON actor_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('actor_version_id');
CREATE CONSTRAINT TRIGGER audit_amount_input_versions AFTER INSERT ON amount_input_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('input_version_id');
CREATE CONSTRAINT TRIGGER audit_approved_list_versions AFTER INSERT ON approved_list_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('list_version_id');
CREATE CONSTRAINT TRIGGER audit_attempt_events AFTER INSERT ON attempt_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('attempt_event_id');
CREATE CONSTRAINT TRIGGER audit_challenge_events AFTER INSERT ON challenge_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('challenge_event_id');
CREATE CONSTRAINT TRIGGER audit_check_runs AFTER INSERT ON check_runs DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('check_run_id');
CREATE CONSTRAINT TRIGGER audit_claim_decisions AFTER INSERT ON claim_decisions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('decision_id');
CREATE CONSTRAINT TRIGGER audit_claim_responses AFTER INSERT ON claim_responses DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('response_id');
CREATE CONSTRAINT TRIGGER audit_claim_rounds AFTER INSERT ON claim_rounds DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('round_id');
CREATE CONSTRAINT TRIGGER audit_claim_submissions AFTER INSERT ON claim_submissions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('submission_id');
CREATE CONSTRAINT TRIGGER audit_entitlement_versions AFTER INSERT ON entitlement_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('entitlement_version_id');
CREATE CONSTRAINT TRIGGER audit_evidence_versions AFTER INSERT ON evidence_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('evidence_version_id');
CREATE CONSTRAINT TRIGGER audit_fund_correction_sets AFTER INSERT ON fund_correction_sets DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('correction_set_id');
CREATE CONSTRAINT TRIGGER audit_fund_entries AFTER INSERT ON fund_entries DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('fund_entry_id');
CREATE CONSTRAINT TRIGGER audit_grievance_events AFTER INSERT ON grievance_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('grievance_event_id');
CREATE CONSTRAINT TRIGGER audit_household_link_versions AFTER INSERT ON household_link_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('link_version_id');
CREATE CONSTRAINT TRIGGER audit_household_versions AFTER INSERT ON household_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('household_version_id');
CREATE CONSTRAINT TRIGGER audit_operation_versions AFTER INSERT ON operation_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('operation_version_id');
CREATE CONSTRAINT TRIGGER audit_outcome_versions AFTER INSERT ON outcome_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('outcome_version_id');
CREATE CONSTRAINT TRIGGER audit_recorded_handovers AFTER INSERT ON recorded_handovers DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('handover_id');
CREATE CONSTRAINT TRIGGER audit_registry_reviews AFTER INSERT ON registry_reviews DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('registry_review_id');
CREATE CONSTRAINT TRIGGER audit_session_versions AFTER INSERT ON session_versions DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('session_version_id');
CREATE CONSTRAINT TRIGGER audit_submission_snapshots AFTER INSERT ON submission_snapshots DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION require_audit_target('snapshot_id');
CREATE FUNCTION audit_not_empty() RETURNS trigger LANGUAGE plpgsql AS $$
       BEGIN
         IF NOT EXISTS(SELECT 1 FROM audit_targets WHERE audit_event_id=NEW.id)
         THEN RAISE EXCEPTION 'empty audit event' USING ERRCODE='23514'; END IF;
         RETURN NEW;
       END $$;
       CREATE CONSTRAINT TRIGGER audit_not_empty AFTER INSERT ON audit_events DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION audit_not_empty();
CREATE FUNCTION validate_correction() RETURNS trigger LANGUAGE plpgsql AS $$
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
       CREATE CONSTRAINT TRIGGER complete_correction AFTER INSERT ON fund_correction_sets DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION validate_correction();
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