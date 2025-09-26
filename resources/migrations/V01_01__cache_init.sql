CREATE TABLE IF NOT EXISTS cache_translate (
    key          TEXT    NOT NULL,
    created      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    from_lang    TEXT    NOT NULL,
    to_lang      TEXT    NOT NULL,
    plugin       TEXT    NOT NULL,
    model        TEXT    NOT NULL,
    context_hash INTEGER NOT NULL,
    value        TEXT    NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_translate_cols
    ON cache_translate (key, from_lang, to_lang, plugin, model, context_hash);

CREATE INDEX IF NOT EXISTS idx_created
    ON cache_translate (created);