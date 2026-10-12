# V4 backend contracts — not a running server

These source files prepare Pixelhub's V4 account and progress-sync backend.
**No API is running, no identity provider is configured, and no database
migration has been executed.** Android/Web continue using local progress.

- openapi/v4-progress.yaml: provisional, versioned, authenticated API contract.
- migrations/0001_v4_accounts_progress.up.sql: initial PostgreSQL tables,
  constraints, cascade deletion and user-scoped progress/operation RLS.
- packages/game_domain/lib/progress_sync.dart: deterministic Dart reference
  reconciliation logic, not a network adapter or trusted API service.

The API service must first select an OIDC/Auth provider, host/region and
secrets strategy with a reviewed ADR. A server-side verified user ID must
be established before any progress query or write. A transaction should
SET LOCAL pixelhub.auth_user_id to the verified UUID; never accept it
from a request body or browser-controlled headers.

For every sync request, validate the level identity and bitset, compute a
canonical request digest, and look up the (user_id, operation_id) record.
Replay the stored response only if the digest matches. Otherwise reject
operation ID reuse. Hold a row lock during reset/merge and commit both
the updated user_progress row and operation ledger together.

A new progress key needs an explicit bootstrap or guest-adoption endpoint
before /progress/sync can safely process it. This is intentionally not
defined as an implicit overwrite of someone else's existing history.
Guests keep local progress on sign-in failure or unresolved conflicts.

Before deployment: pick the Auth/Hosting providers, add migration runner,
implement the service with strict authorization and user-level tests,
transactional idempotency, monitoring/redaction, rate limits, HTTPS, account
deletion, backup/restore and a complete Android/Web offline outbox.
The database migration is additive; rollback is not a destructive DROP
script. Back up and review any later down migration.

Do not commit provider credentials, tokens, originals of private photos,
or real user data.
