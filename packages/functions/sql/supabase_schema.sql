-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE listing_status AS ENUM ('available', 'rented', 'pending_review', 'rejected');
CREATE TYPE attribute_type AS ENUM ('boolean', 'string', 'integer', 'enum');

-- Create listings table
CREATE TABLE IF NOT EXISTS listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status listing_status DEFAULT 'pending_review',
    source_url TEXT UNIQUE,
    title TEXT,
    description TEXT,
    price_monthly_vnd BIGINT,
    area_m2 NUMERIC,
    address_street TEXT,
    address_ward TEXT,
    address_district TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    contact_phone TEXT,
    image_urls TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create attributes table
CREATE TABLE IF NOT EXISTS attributes (
    id SERIAL PRIMARY KEY,
    type attribute_type NOT NULL,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    possible_values TEXT[]
);

-- Create listing_attributes table
CREATE TABLE IF NOT EXISTS listing_attributes (
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    attribute_id INTEGER REFERENCES attributes(id) ON DELETE CASCADE,
    value_string TEXT,
    value_integer INTEGER,
    value_boolean BOOLEAN,
    PRIMARY KEY (listing_id, attribute_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_district ON listings(address_district);
CREATE INDEX IF NOT EXISTS idx_listings_price ON listings(price_monthly_vnd);
