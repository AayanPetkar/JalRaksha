# Database Schema & Spatial Architecture — JalRaksha

## 1. Overview

JalRaksha uses **PostgreSQL 15+** with the **PostGIS 3+** spatial extension. This database schema is designed to manage spatial geometries (village boundaries, road networks, river lines, safe zone points, citizen report locations), time-series environmental observations, user emergency circles, and risk score outputs.

---

## 2. Spatial Reference System (SRS)

- **EPSG:4326 (WGS 84)**: Standard coordinate reference system (Latitude, Longitude) used for point locations, user coordinates, citizen reports, and safe zones (`GEOGRAPHY` / `GEOMETRY`).
- **EPSG:3857 (Web Mercator)**: Used internally for buffer calculations and dynamic routing spatial queries where planar metric distance is required.

---

## 3. Entity Relationship & Schema Details

### 3.1 `users`
Stores registered citizens and app users.
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    preferred_language VARCHAR(10) DEFAULT 'mr', -- 'mr' (Marathi), 'hi' (Hindi), 'en' (English)
    fcm_token TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 `admin_users`
Stores disaster management officials and system administrators.
```sql
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'OFFICIAL', -- 'SUPER_ADMIN', 'DISASTER_OFFICIAL', 'RELIEF_WORKER'
    jurisdiction_district VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 `locations`
Stores user location history and current registered coordinates.
```sql
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    geom GEOGRAPHY(POINT, 4326) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy_meters FLOAT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_locations_geom ON locations USING GIST(geom);
CREATE INDEX idx_locations_user_time ON locations(user_id, recorded_at DESC);
```

### 3.4 `emergency_contacts`
Trusted contacts added by users for emergency notifications.
```sql
CREATE TABLE emergency_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    contact_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.5 `emergency_circle_preferences`
Notification thresholds per emergency contact.
```sql
CREATE TABLE emergency_circle_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES emergency_contacts(id) ON DELETE CASCADE,
    notify_on_prepare BOOLEAN DEFAULT FALSE,  -- 🟠 Prepare Alerts
    notify_on_critical BOOLEAN DEFAULT TRUE,  -- 🔴 Critical Alerts
    notify_on_distress BOOLEAN DEFAULT TRUE,  -- 🆘 "Need Help" Signal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.6 `villages`
Geospatial boundaries and metadata for monitored villages.
```sql
CREATE TABLE villages (
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
CREATE INDEX idx_villages_boundary ON villages USING GIST(boundary);
CREATE INDEX idx_villages_centroid ON villages USING GIST(centroid);
```

### 3.7 `infrastructure`
Physical assets within village territories (houses, schools, hospitals, power grids, farmlands).
```sql
CREATE TABLE infrastructure (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id UUID REFERENCES villages(id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'HOUSE', 'SCHOOL', 'HOSPITAL', 'FARM', 'BRIDGE', 'POWER_STATION'
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    elevation_meters FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_infrastructure_location ON infrastructure USING GIST(location);
```

### 3.8 `roads` & `road_conditions`
Road network segments and dynamic flood hazard conditions.
```sql
CREATE TABLE roads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    road_name VARCHAR(150),
    road_type VARCHAR(50), -- 'HIGHWAY', 'VILLAGE_ROAD', 'BRIDGE'
    path GEOMETRY(LINESTRING, 4326) NOT NULL,
    base_cost_meters FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_roads_path ON roads USING GIST(path);

CREATE TABLE road_conditions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    road_id UUID REFERENCES roads(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL, -- 'OPEN', 'WATCH', 'HIGH_RISK', 'BLOCKED', 'SUBMERGED'
    hazard_penalty_multiplier FLOAT DEFAULT 1.0, -- Multiplier applied to routing cost
    water_depth_cm FLOAT DEFAULT 0.0,
    source VARCHAR(30) DEFAULT 'AI_ESTIMATE', -- 'OFFICIAL', 'AI_ESTIMATE', 'CITIZEN_REPORT'
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3.9 `safe_zones`
Designated shelters, community halls, and relief centers.
```sql
CREATE TABLE safe_zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(150) NOT NULL,
    type VARCHAR(50) DEFAULT 'SHELTER', -- 'SHELTER', 'RELIEF_CENTER', 'COMMUNITY_HALL'
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    capacity INT DEFAULT 100,
    current_occupancy INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT TRUE, -- Officially verified safe zone
    contact_phone VARCHAR(20),
    district VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_safe_zones_location ON safe_zones USING GIST(location);
```

### 3.10 `environmental_observations`
Real-time and forecasted telemetry data.
```sql
CREATE TABLE environmental_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    station_id VARCHAR(50) NOT NULL,
    village_id UUID REFERENCES villages(id) ON DELETE CASCADE,
    rainfall_mm FLOAT DEFAULT 0.0,
    river_water_level_m FLOAT DEFAULT 0.0,
    soil_moisture_percentage FLOAT DEFAULT 0.0,
    temperature_celsius FLOAT,
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    source_tag VARCHAR(30) DEFAULT 'OFFICIAL_DATA' -- 'OFFICIAL_DATA', 'SIMULATED_DEMO_DATA'
);
CREATE INDEX idx_env_obs_village_time ON environmental_observations(village_id, observed_at DESC);
```

### 3.11 `flood_events` & `flood_risks` & `risk_factors`
Active flood occurrences and AI-generated risk evaluations.
```sql
CREATE TABLE flood_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_title VARCHAR(150) NOT NULL,
    affected_district VARCHAR(100) NOT NULL,
    severity VARCHAR(30) DEFAULT 'WATCH', -- 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE flood_risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id UUID REFERENCES villages(id) ON DELETE CASCADE,
    flood_event_id UUID REFERENCES flood_events(id) ON DELETE SET NULL,
    risk_score FLOAT NOT NULL, -- 0.0 to 100.0
    risk_level VARCHAR(20) NOT NULL, -- 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    confidence_score FLOAT DEFAULT 0.85, -- Model confidence score (0.0 - 1.0)
    data_freshness_minutes INT DEFAULT 5,
    affected_houses_count INT DEFAULT 0,
    affected_farmland_acres FLOAT DEFAULT 0.0,
    affected_schools_count INT DEFAULT 0,
    affected_hospitals_count INT DEFAULT 0,
    source_tag VARCHAR(30) DEFAULT 'AI_PREDICTION', -- 'AI_PREDICTION', 'OFFICIAL_DATA', 'SIMULATED_DEMO_DATA'
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_flood_risks_village ON flood_risks(village_id, evaluated_at DESC);

CREATE TABLE risk_factors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flood_risk_id UUID REFERENCES flood_risks(id) ON DELETE CASCADE,
    factor_key VARCHAR(50) NOT NULL, -- 'HEAVY_RAINFALL', 'RIVER_LEVEL', 'SOIL_SATURATION', 'LOW_ELEVATION'
    contribution_percentage FLOAT NOT NULL, -- Weight contribution (e.g. 45.0 for 45%)
    description_en TEXT NOT NULL,
    description_mr TEXT,
    description_hi TEXT
);
```

### 3.12 `citizen_reports`
Geotagged ground-truth submissions.
```sql
CREATE TABLE citizen_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    photo_url TEXT,
    voice_note_url TEXT,
    description TEXT,
    disaster_category VARCHAR(50) DEFAULT 'WATER_LOGGING', -- 'WATER_LOGGING', 'ROAD_BLOCKED', 'BRIDGE_SUBMERGED', 'TRAPPED_PERSON'
    verification_status VARCHAR(30) DEFAULT 'UNVERIFIED', -- 'UNVERIFIED', 'VERIFIED', 'REJECTED'
    source_tag VARCHAR(30) DEFAULT 'CITIZEN_REPORT',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_citizen_reports_location ON citizen_reports USING GIST(location);
```

### 3.13 `alerts` & `notification_history`
Alert history and delivery logs across push and SMS channels.
```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id UUID REFERENCES villages(id) ON DELETE CASCADE,
    alert_level VARCHAR(20) NOT NULL, -- 'LOW', 'WATCH', 'PREPARE', 'CRITICAL'
    title VARCHAR(150) NOT NULL,
    message_en TEXT NOT NULL,
    message_mr TEXT,
    message_hi TEXT,
    issued_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_id UUID REFERENCES alerts(id) ON DELETE CASCADE,
    recipient_phone VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL, -- 'APP_PUSH', 'USER_SMS', 'EMERGENCY_CONTACT_SMS'
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'SENT', 'DELIVERED', 'FAILED'
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
