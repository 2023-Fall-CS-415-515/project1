-- Add up migration script here
-- we want to ensure that all posts are unique;
-- i.e., we don't insert the same post twice
CREATE UNIQUE INDEX ON posts (subreddit, post_id);
CREATE UNIQUE INDEX ON comments (subreddit, post_id, comment_id);
