CREATE TABLE IF NOT EXISTS raw_scraped_data (
    id UUID PRIMARY KEY,
    source TEXT NOT NULL,
    source_post_id TEXT,
    source_url TEXT,
    raw_json JSONB NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- deprecated: intentionally left blank. raw_scraped_data is removed in favor of inserting directly into listings.
