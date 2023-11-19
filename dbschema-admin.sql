
DROP TABLE IF EXISTS users;
CREATE TABLE users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER NULL,
    creator_ip TEXT NULL
);
CREATE INDEX users_i1 ON users (email);


DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions(
    txnid TEXT NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    otp INTEGER NOT NULL,
    token TEXT NULL,
    ipadrr TEXT NULL,
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (email) VALUES ('nikhil.js@gmail.com');
