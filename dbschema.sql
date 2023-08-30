CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id TEXT,
    subject_name TEXT,
    topic_id TEXT,
    topic_name TEXT,
    subtopic_id TEXT,
    subtopic_name TEXT
);


CREATE TABLE IF NOT EXISTS questionbank (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subtopic_id TEXT,
    title TEXT,
    content TEXT,
    embeds TEXT,
    created TIMESTAMP DEFAULT (datetime('now', 'utc')),
    updated TIMESTAMP DEFAULT (datetime('now', 'utc'))
);


INSERT OR IGNORE INTO topics (id, subject_id, subject_name, topic_id, topic_name, subtopic_id, subtopic_name) VALUES
(1, 'biology', 'Biology', 'cell', 'Cell', 'cellorganelles', 'Cell organelles');



