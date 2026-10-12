# ADR 0004 — V4 offline-first progress sync conflict policy

Status: **Accepted for the pure domain contract; backend and account integration are not implemented.**
Date: 2026-10-12
Scope: Android and Web, per immutable (levelId, levelVersion, levelChecksum).
Previous decisions: ADR 0002 (versioned bitset/local reset), ADR 0003 (private photos stay local).

## Context

V3 saves a ProgressSnapshot locally, with an immutable level identity, compact completion bitset, local generation (reset counter), and local revision. In V4, two signed-in devices can paint concurrently while disconnected. A naive last-write-wins upload drops painted cells; a naive bitwise union resurrects cells intentionally cleared by Reset.

Local ProgressSnapshot.revision is **not** a global ordering signal. V4 requires an independent server revision and an authoritative server reset epoch.

## Decision

The shared pure merge function is implemented in packages/game_domain/lib/progress_sync.dart, exposed via game_domain.dart. Each server-side progress record contains ProgressSnapshot plus serverRevision. Each queued client mutation contains a stable operationId, last acknowledged baseServerRevision and baseGeneration, local progress and an explicit isReset intent.

| Condition | Result |
| --- | --- |
| Different level ID/version/checksum/cell count | Reject malformed/incompatible mutation; never silently merge |
| Client baseServerRevision exceeds serverRevision | Reject invalid future reference |
| Client baseGeneration differs from current server generation | Reject as stale-generation conflict; retain client data for user resolution |
| Same generation, ordinary paint | Bitwise OR completed cells; increment server revision only if new bits appeared |
| Same generation, explicit Reset | Replace bitset with post-reset bits and increment authoritative generation and server revision |
| Retried same (user, operationId) | Return stored result from transactional backend idempotency ledger; **do not call pure merge twice** |

A client may do several local resets before reconnecting. Such a pending Reset represents the final post-reset bitset, but advances the server generation by exactly one epoch. Local generations must never be assumed equal to server generations after login: an adapter first adopts the last acknowledged server baseline.

Reset is intentionally dominant over concurrent painting from the prior generation. The rejected old-generation client must not discard its local snapshot or silently replay its old bits in the new generation. UI should offer an explicit resolution (keep server state, or start new work); designing that UX remains V4 work.

The backend must commit progress and the operationId/result ledger in a **single transaction** with a unique (authenticated user ID, operationId) key. Duplicates with a different request body must fail, not reuse another request's result. Lock the per-user/per-level progress row during reconciliation. User ID is taken from the verified session, not a client parameter. Authorization, request size limits, rate limiting and account deletion are mandatory before enabling the network adapter.

## Guest-to-account migration

Keep every guest progress record until the server has acknowledged a reconciled copy. Do not automatically union a guest snapshot into an existing registered record with a different reset history. Initial upload of a previously absent record can import its bits under server generation 0; any existing remote record with an unproven baseline requires a dedicated migration choice. V3 artwork/photo originals must never be included in progress sync; private converted grids remain local unless a separate explicit consent flow is developed.

## Local FIFO outbox (source implementation)

`ProgressSyncOutbox` stores only immutable, validated progress bitsets under an
authenticated account scope. Android/Web preferences use distinct keys by
account. Reads reject damaged or wrong-account documents rather than clearing
or silently overwriting them. The queue caps at 128 operations and 512 KiB.

The storage adapter serializes all mutations with local writes and propagates
write failures. A future coordinator must durably enqueue *before* sending,
retransmit the exact operation ID and body on an uncertain response, and
acknowledge only the queue head on a validated `applied` or `unchanged`
response. Never acknowledge on a timeout or stale-generation conflict.

The current outbox deliberately does not coalesce resets that might already
have reached the server. Before activation, implement generation rebasing for
multiple pending offline resets, a bounded-queue recovery path, verified
account switching, transactional server deduplication and conflict UX.
Clearing all Pixelhub data intentionally clears stored queues.

## Verification and rollout

The pure merge implementation and regression test source cover concurrent painting, replayed paint, Reset, late stale writes, competing resets, repeated offline resets, invalid level identity and future revisions. They were added **without running tests or a build** per the repository owner's development workflow. The database has an unexecuted migration draft and the account-scoped offline outbox has Android/Web source adapters and regression test source. The backend transaction handler, authenticated network coordinator, auth provider, app sync UI and cross-device validation remain unimplemented.

Do not advertise V4 cloud sync as available until authorization, transactional idempotency and the full Android-to-Web acceptance gate pass.
