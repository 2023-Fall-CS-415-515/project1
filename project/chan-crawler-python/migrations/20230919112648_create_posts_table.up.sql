-- Add up migration script here
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    board TEXT NOT NULL,
    thread_number BIGINT NOT NULL,
    post_number BIGINT NOT NULL,
    created TIMESTAMP NOT NULL,
    data TEXT,
    html TEXT
)