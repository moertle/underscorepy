-- for storing configuration parameters
CREATE TABLE IF NOT EXISTS config (
    "key"        TEXT      UNIQUE NOT NULL,
    "value"      TEXT
    );

CREATE TABLE IF NOT EXISTS users (
    "username"   TEXT      UNIQUE NOT NULL,
    "password"   TEXT      NOT NULL,
    "disabled"   BOOLEAN   NOT NULL,
    "isadmin"    BOOLEAN   NOT NULL
    );

CREATE TABLE IF NOT EXISTS sessions (
    "session_id" TEXT      UNIQUE NOT NULL,
    "username"   TEXT      NOT NULL,
    "agent"      TEXT      NOT NULL,
    "ip"         TEXT      NOT NULL,
    "time"       INTEGER   NOT NULL
    );
