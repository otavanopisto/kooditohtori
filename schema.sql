CREATE TABLE bug_instance (
    id                   INTEGER,
    project              TEXT           NOT NULL,
    travis_build_number  INTEGER        NOT NULL,
    short_message        TEXT           NOT NULL,
    long_message         TEXT           NOT NULL,
    PRIMARY KEY (id ASC)
);