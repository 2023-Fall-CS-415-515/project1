-- Add up migration script here
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    post_id VARCHAR(16) NOT NULL,
    title varchar(300) NOT NULL,
    created TIMESTAMP NOT NULL,
    data JSONB DEFAULT '{}'::jsonb NOT NULL,
    html TEXT
);

CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id VARCHAR(16) NOT NULL,
    comment_id VARCHAR(16) NOT NULL,
    created TIMESTAMP NOT NULL,
    data JSONB DEFAULT '{}'::jsonb NOT NULL,
    html TEXT
)