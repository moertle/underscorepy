
-- _.py users
CREATE TABLE IF NOT EXISTS users (
    "username"      TEXT        UNIQUE NOT NULL,
    "password"      TEXT        NOT NULL,
    "disabled"      BOOLEAN,
    "created"       INTEGER,
    "last"          INTEGER
    );
