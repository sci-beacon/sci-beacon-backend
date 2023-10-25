
DROP TABLE IF EXISTS users;
CREATE TABLE users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    created_on TIMESTAMP DEFAULT (datetime('now', 'utc')),
    created_by INTEGER NULL,
    creator_ip VARCHAR(100) NULL
);
CREATE INDEX users_i1 ON users (email);


DROP TABLE IF EXISTS otps;
CREATE TABLE otps(
    txnid TEXT NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    otp INTEGER NOT NULL,
    created_on TIMESTAMP DEFAULT (datetime('now', 'utc')),
    ip VARCHAR(100) NULL,
    matched_on TIMESTAMP(0) NULL,
    validity INTEGER NULL
);


DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions(
    token VARCHAR(36) NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    ip VARCHAR(100) NULL,
    created_on TIMESTAMP DEFAULT (datetime('now', 'utc')),
    expired boolean DEFAULT FALSE NOT NULL
);
