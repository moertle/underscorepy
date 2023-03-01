-- for storing configuration parameters
CREATE TABLE IF NOT EXISTS config (
    "key"       TEXT      UNIQUE NOT NULL,
    "value"     TEXT
    );

CREATE TABLE IF NOT EXISTS users (
    "username"  TEXT      UNIQUE NOT NULL,
    "password"  TEXT      NOT NULL
    )