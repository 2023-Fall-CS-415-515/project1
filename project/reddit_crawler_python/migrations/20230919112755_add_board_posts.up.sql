-- Add up migration script here
ALTER TABLE posts ADD COLUMN subreddit TEXT;
ALTER TABLE comments ADD COLUMN subreddit TEXT;
