# Aling branch at PR ang gagamitin?

[Complete branch/39-PR matrix at exact source references](../GITHUB_TRIAGE.md). Hindi binago ang PR states, branches o main. Local uncommitted changes lang sa `design-proposal` ang finals work.

## Recommendation para sa presentation

Gamitin ang current candidate kung ang story ay funding → request → human review → amount → assigned payout → recipient report → integrity check. Mas complete ang implemented evidence workflow nito. Inadapt ang useful visual patterns ng PR39: compact navigation, searchable one-household detail, grouped payout desk at clearer phone shortcuts. Hindi imported ang ibang backend/auth/contracts stack.

## Honest comparison

| Area | Current candidate | PR39 |
|---|---|---|
| Funding entry UI | Original upload, extracted fields, manual confirmation, corrections | Write APIs exist; narrower frontend omits authoring forms per inspected docs |
| Claims/amounts/sessions | Implemented fuller documentary workflow | Different, narrower review/list/payout product; not same screens/protocol |
| Authentication | Wala; active selected actors can be impersonated | Password-authenticated synthetic accounts, sessions/request protections in inspected source |
| UI | New compact redesign; all five roles and fuller process retained | Strong compact visual reference |
| Data/contracts | Approved FastAPI/PostgreSQL MVP, versioned evidence registry | Separate SQLite/auth/accounting/contracts assumptions |
| Evidence | Current local tests/captures/rehearsal | Source/author evidence reviewed; not independently run here |

PR39 is not “fake,” “no blockchain” o merely cosmetic. May real strengths, lalo na sa authentication. Hindi lang safe drop-in ang whole branch. [Detailed PR39 review](../PR39_REVIEW.md).

## Main branches

- **main:** preserved baseline. Huwag baguhin o merge-an during this task.
- **design-proposal:** current finals worktree, existing approved MVP plus local UI/demo/docs work.
- **feat/five-role-mvp:** useful overlapping MVP implementation; role/error-recovery changes were inspected/selectively reused where compatible.
- **BinkzBooze stacked PRs:** sequential dependencies, cumulative changes. Hindi 39 independent features na puwedeng i-merge in any order.

Complete dependencies, duplicates/obsolete earlier steps at conflicts are in the linked matrix. Later stacked PR can contain earlier changes; huwag i-cherry-pick blindly at madoble ang implementation.

## Safe future consolidation

1. Preserve current work and both working stacks.
2. Decide product/data/contract/auth baseline with maintainers.
3. Move compatible presentation patterns separately from business/API changes.
4. Review auth, schema, hash and contract compatibility explicitly. Changes there need approved decisions/migrations/tests.
5. Validate one complete fresh synthetic journey plus fail-closed recovery before claiming combined capability.

No push, merge, PR closure, force-push, branch deletion o public deploy ang ginawa. Authentication from PR39 is **not** included here.
