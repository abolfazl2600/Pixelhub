-- V4 contract only: not deployed and no authentication service exists yet.
-- Apply through a reviewed PostgreSQL migration runner after staging backup.
-- All API operations must derive the user UUID from a verified identity.

BEGIN;

CREATE TABLE app_users (
  id UUID PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'suspended', 'deleting')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE user_identities (
  user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
  provider TEXT NOT NULL CHECK (length(provider) BETWEEN 1 AND 80),
  provider_subject TEXT NOT NULL
    CHECK (length(provider_subject) BETWEEN 1 AND 255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (provider, provider_subject),
  UNIQUE (user_id, provider)
);

CREATE TABLE user_profiles (
  user_id UUID PRIMARY KEY REFERENCES app_users(id) ON DELETE CASCADE,
  nickname TEXT CHECK (char_length(nickname) BETWEEN 1 AND 80),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_devices (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  revoked_at TIMESTAMPTZ
);
CREATE INDEX user_devices_by_owner ON user_devices (user_id);

CREATE TABLE user_progress (
  user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
  level_id TEXT NOT NULL CHECK (length(level_id) BETWEEN 1 AND 128),
  level_version INTEGER NOT NULL CHECK (level_version > 0),
  level_checksum TEXT NOT NULL
    CHECK (level_checksum ~ '^[0-9a-f]{64}$'),
  cell_count INTEGER NOT NULL CHECK (cell_count BETWEEN 1 AND 65536),
  generation BIGINT NOT NULL DEFAULT 0 CHECK (generation >= 0),
  local_revision BIGINT NOT NULL DEFAULT 0 CHECK (local_revision >= 0),
  server_revision BIGINT NOT NULL DEFAULT 0 CHECK (server_revision >= 0),
  completed_cells BYTEA NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, level_id, level_version),
  CHECK (octet_length(completed_cells) = (cell_count + 7) / 8),
  CHECK (
    cell_count % 8 = 0 OR
    get_byte(completed_cells, (cell_count - 1) / 8) >> (cell_count % 8) = 0
  )
);
CREATE INDEX user_progress_updated ON user_progress (user_id, updated_at DESC);

-- Store canonical request SHA-256 and complete response in the SAME
-- transaction as user_progress. Reusing an operationId with a different
-- digest is rejected. Retrying a Reset must replay this result, never reset
-- again. Records are retained until a reviewed retention policy exists.
CREATE TABLE sync_operations (
  user_id UUID NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
  operation_id TEXT NOT NULL
    CHECK (operation_id ~ '^[A-Za-z0-9_-]{8,128}$'),
  request_digest BYTEA NOT NULL CHECK (octet_length(request_digest) = 32),
  response_status SMALLINT NOT NULL
    CHECK (response_status IN (200, 409, 422)),
  response_body JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, operation_id)
);
CREATE INDEX sync_operations_by_age ON sync_operations (created_at);

-- Progress and idempotency tables enforce per-user row access. The API's
-- verified-session middleware must use SET LOCAL pixelhub.auth_user_id =
-- '<verified UUID>' inside every transaction. A missing context sees no rows.
-- This setting MUST NOT be set from client-supplied user IDs.
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress FORCE ROW LEVEL SECURITY;
CREATE POLICY progress_user_scope ON user_progress
  USING (
    user_id = nullif(current_setting('pixelhub.auth_user_id', true), '')::uuid
  )
  WITH CHECK (
    user_id = nullif(current_setting('pixelhub.auth_user_id', true), '')::uuid
  );

ALTER TABLE sync_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_operations FORCE ROW LEVEL SECURITY;
CREATE POLICY operations_user_scope ON sync_operations
  USING (
    user_id = nullif(current_setting('pixelhub.auth_user_id', true), '')::uuid
  )
  WITH CHECK (
    user_id = nullif(current_setting('pixelhub.auth_user_id', true), '')::uuid
  );

COMMIT;
