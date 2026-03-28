-- MapSearch.app database schema

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    credits_remaining INTEGER DEFAULT 99,
    locale VARCHAR(5) DEFAULT 'en',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE scrape_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    zoom_level INTEGER DEFAULT 13,
    near_me BOOLEAN DEFAULT FALSE,
    country VARCHAR(10),
    raw_result_count INTEGER,
    cache_key VARCHAR(500) GENERATED ALWAYS AS (
        lower(trim(keyword)) || '|' || lower(trim(location)) || '|' || zoom_level || '|' || near_me || '|' || lower(coalesce(country, ''))
    ) STORED,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_cache_key ON scrape_cache(cache_key, created_at DESC);

CREATE TABLE searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    scrape_cache_id UUID REFERENCES scrape_cache(id),
    filters_applied JSONB NOT NULL DEFAULT '{}',
    filtered_result_count INTEGER,
    credits_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_searches_user ON searches(user_id, created_at DESC);

CREATE TABLE search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scrape_cache_id UUID REFERENCES scrape_cache(id) ON DELETE CASCADE,
    business_name VARCHAR(500),
    domain VARCHAR(500),
    url TEXT,
    phone VARCHAR(100),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(100),
    zip VARCHAR(50),
    country VARCHAR(10),
    rating NUMERIC(2,1),
    reviews_count INTEGER,
    place_id VARCHAR(255),
    cid VARCHAR(255),
    google_maps_url TEXT,
    category VARCHAR(255),
    additional_categories JSONB,
    category_ids JSONB,
    is_claimed BOOLEAN,
    verified BOOLEAN,
    photos_count INTEGER,
    main_image TEXT,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    price_level VARCHAR(10),
    work_hours JSONB,
    business_status VARCHAR(50),
    rating_distribution JSONB,
    has_website BOOLEAN GENERATED ALWAYS AS (domain IS NOT NULL AND domain != '') STORED,
    has_email BOOLEAN GENERATED ALWAYS AS (email IS NOT NULL AND email != '') STORED,
    has_phone BOOLEAN GENERATED ALWAYS AS (phone IS NOT NULL AND phone != '') STORED
);
CREATE INDEX idx_results_cache ON search_results(scrape_cache_id);
CREATE INDEX idx_results_filters ON search_results(has_website, has_email, rating, reviews_count);

CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    reference_id UUID,
    stripe_payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_credits_user ON credit_transactions(user_id, created_at DESC);

CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    search_id UUID REFERENCES searches(id),
    row_count INTEGER,
    filters_applied JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_reset_tokens_hash ON password_reset_tokens(token_hash);
CREATE INDEX idx_reset_tokens_user ON password_reset_tokens(user_id);

CREATE TABLE search_result_ids (
    search_id UUID REFERENCES searches(id) ON DELETE CASCADE,
    search_result_id UUID REFERENCES search_results(id) ON DELETE CASCADE,
    PRIMARY KEY (search_id, search_result_id)
);
