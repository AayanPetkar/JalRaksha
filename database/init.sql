-- Enable PostGIS spatial extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'mr',
    fcm_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Admin Users Table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'DISASTER_OFFICIAL',
    jurisdiction_district VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Emergency Contacts Table
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    contact_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Villages Table
CREATE TABLE IF NOT EXISTS villages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    village_code VARCHAR(50) UNIQUE NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    name_mr VARCHAR(100),
    name_hi VARCHAR(100),
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    population INT DEFAULT 0,
    boundary GEOMETRY(POLYGON, 4326) NOT NULL,
    centroid GEOGRAPHY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_villages_boundary ON villages USING GIST(boundary);

-- 5. Safe Zones Table
CREATE TABLE IF NOT EXISTS safe_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50) DEFAULT 'SHELTER',
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    capacity INT DEFAULT 100,
    current_occupancy INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT TRUE,
    contact_phone VARCHAR(20),
    district VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_safe_zones_location ON safe_zones USING GIST(location);
