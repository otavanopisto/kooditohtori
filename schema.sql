CREATE TABLE bug_instance (
    id                   INTEGER,
    timestamp            LONG           NOT NULL,
    project              TEXT           NOT NULL,
    short_message        TEXT           NOT NULL,
    long_message         TEXT           NOT NULL,
    PRIMARY KEY (id ASC)
);