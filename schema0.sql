*.loghema.sql
.envostgreSQL schema for NYC Taxi Trips (Task 2 deliverable)
.DS_Store: (Your name) — replace before submission
node_modules/ormalized schema, indexes, and logging for cleaned & enriched trip-level data

-- NOTE: This file targets PostgreSQL. Adjust minor datatypes if using SQLite/MySQL.

-- -----------------------------
-- Optional: create database (run outside this file)
-- createdb nyc_taxi
-- psql -d nyc_taxi -f schema.sql
-- -----------------------------

-- Enable useful extensions if available (uncomment if allowed in your environment)
-- CREATE EXTENSION IF NOT EXISTS pgcrypto; -- for gen_random_uuid()

-- -----------------------------
-- Table: vendors
-- stores taxi vendor/provider metadata
-- -----------------------------
CREATE TABLE IF NOT EXISTS vendors (
    vendor_id    INTEGER PRIMARY KEY,
    vendor_name  VARCHAR(128)
);

-- -----------------------------
-- Table: payment_types
-- canonical list of payment types
-- -----------------------------
CREATE TABLE IF NOT EXISTS payment_types (
    payment_id   SERIAL PRIMARY KEY,
    payment_code INTEGER UNIQUE, -- original code from raw dataset (if available)
    payment_desc VARCHAR(64) NOT NULL
);

-- -----------------------------
-- Table: locations
-- canonicalized pickup/dropoff coordinates to avoid duplication
-- using a simple lat/lon pair. If you deploy PostGIS, replace with geography/geometry
-- -----------------------------
CREATE TABLE IF NOT EXISTS locations (
    location_id  BIGSERIAL PRIMARY KEY,
    latitude     NUMERIC(9,6) NOT NULL,
    longitude    NUMERIC(9,6) NOT NULL,
    lat_long_hash TEXT GENERATED ALWAYS AS (concat(latitude::text, ',', longitude::text)) STORED
);
-- Prevent exact duplicates at insertion time (up to 6-decimal precision)
CREATE UNIQUE INDEX IF NOT EXISTS ux_locations_latlon ON locations(latitude, longitude);

-- -----------------------------
-- Table: trips
-- central table containing cleaned and derived fields
-- -----------------------------
CREATE TABLE IF NOT EXISTS trips (
    trip_id            BIGINT PRIMARY KEY, -- original trip id if available; otherwise generate outside
    vendor_id          INTEGER REFERENCES vendors(vendor_id),
    pickup_id          BIGINT REFERENCES locations(location_id),
    dropoff_id         BIGINT REFERENCES locations(location_id),
    pickup_datetime    TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    dropoff_datetime   TIMESTAMP WITHOUT TIME ZONE NOT NULL,

    passenger_count    SMALLINT,

    trip_distance_miles NUMERIC(8,3) CHECK (trip_distance_miles >= 0),
    trip_duration_sec   INTEGER CHECK (trip_duration_sec >= 0), -- derived: seconds between pickup/dropoff

    -- Derived features (must be computed during your ETL step)
    trip_duration_min   NUMERIC(8,3) GENERATED ALWAYS AS (trip_duration_sec::numeric / 60) STORED,
    trip_speed_mph      NUMERIC(8,3) GENERATED ALWAYS AS (
                            CASE WHEN trip_duration_sec > 0 THEN (trip_distance_miles / (trip_duration_sec::numeric/3600)) ELSE NULL END
                        ) STORED,

    fare_amount         NUMERIC(10,2) CHECK (fare_amount >= 0),
    tip_amount          NUMERIC(10,2) CHECK (tip_amount >= 0),
    total_amount        NUMERIC(12,2) GENERATED ALWAYS AS ((COALESCE(fare_amount,0) + COALESCE(tip_amount,0))) STORED,

    fare_per_mile       NUMERIC(10,4) GENERATED ALWAYS AS (
                            CASE WHEN trip_distance_miles > 0 THEN fare_amount / trip_distance_miles ELSE NULL END
                         ) STORED,

    payment_id          INTEGER REFERENCES payment_types(payment_id),

    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- -----------------------------
-- Table: excluded_records
-- log raw rows that were excluded or flagged during cleaning, for transparency
-- -----------------------------
CREATE TABLE IF NOT EXISTS excluded_records (
    excluded_id       BIGSERIAL PRIMARY KEY,
    raw_trip_id       TEXT, -- original id if available
    raw_row_json      JSONB, -- original row as JSON
    reason            TEXT NOT NULL, -- short reason why excluded/flagged
    flagged_at        TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- -----------------------------
-- Indexes: optimize common queries
-- -----------------------------
-- time-based filtering
CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_datetime ON trips(dropoff_datetime);

-- spatial grouping by pickup/dropoff
CREATE INDEX IF NOT EXISTS idx_trips_pickup_id ON trips(pickup_id);
CREATE INDEX IF NOT EXISTS idx_trips_dropoff_id ON trips(dropoff_id);

-- analytic columns
CREATE INDEX IF NOT EXISTS idx_trips_fare_amount ON trips(fare_amount);
CREATE INDEX IF NOT EXISTS idx_trips_trip_distance ON trips(trip_distance_miles);
CREATE INDEX IF NOT EXISTS idx_trips_speed ON trips(trip_speed_mph);

-- vendor and payment
CREATE INDEX IF NOT EXISTS idx_trips_vendor ON trips(vendor_id);
CREATE INDEX IF NOT EXISTS idx_trips_payment ON trips(payment_id);

-- -----------------------------
-- Views: helpful pre-aggregations for dashboard (optional)
-- -----------------------------
-- Average fares per hour of day
CREATE OR REPLACE VIEW vw_avg_fare_by_hour AS
SELECT
    EXTRACT(HOUR FROM pickup_datetime) AS hour_of_day,
    COUNT(*) AS trip_count,
    ROUND(AVG(fare_amount)::numeric, 2) AS avg_fare,
    ROUND(AVG(trip_distance_miles)::numeric, 3) AS avg_distance,
    ROUND(AVG(trip_speed_mph)::numeric, 3) AS avg_speed
FROM trips
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- Top pickup locations by trip count
CREATE OR REPLACE VIEW vw_top_pickup_locations AS
SELECT p.location_id, p.latitude, p.longitude, COUNT(t.trip_id) AS trips
FROM locations p
JOIN trips t ON t.pickup_id = p.location_id
GROUP BY p.location_id, p.latitude, p.longitude
ORDER BY trips DESC
LIMIT 100;

-- -----------------------------
-- Constraints / Data Integrity notes
-- -----------------------------
-- Example check to ensure pickup occurs before dropoff
ALTER TABLE trips
    ADD CONSTRAINT chk_pickup_before_dropoff CHECK (pickup_datetime <= dropoff_datetime);

-- Example trigger to update updated_at timestamp (optional)
CREATE OR REPLACE FUNCTION trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_trips_updated_at
BEFORE UPDATE ON trips
FOR EACH ROW EXECUTE FUNCTION trg_set_updated_at();

-- -----------------------------
-- Sample insert helpers (use in your ETL pipeline)
-- NOTES:
-- 1) Insert into locations: use INSERT ... ON CONFLICT to avoid duplicates
-- 2) Insert into vendors/payment_types: upsert if not exists
-- Example (for reference only; run from your ETL script with parameterized values):

-- Upsert vendor example:
-- INSERT INTO vendors(vendor_id, vendor_name) VALUES (1, 'Vendor A')
-- ON CONFLICT (vendor_id) DO UPDATE SET vendor_name = EXCLUDED.vendor_name;

-- Upsert payment type example:
-- INSERT INTO payment_types(payment_code, payment_desc) VALUES (1, 'Credit Card')
-- ON CONFLICT (payment_code) DO NOTHING;

-- Insert location (avoid duplicates by latitude+longitude):
-- WITH ins AS (
--   INSERT INTO locations(latitude, longitude) VALUES (40.712776, -74.005974)
--   ON CONFLICT (latitude, longitude) DO NOTHING
--   RETURNING location_id
-- )
-- SELECT location_id FROM ins
-- UNION
-- SELECT location_id FROM locations WHERE latitude = 40.712776 AND longitude = -74.005974;

-- -----------------------------
-- Final notes:
-- - Compute derived fields (trip_duration_sec, trip_distance_miles, fare_per_mile) in your ETL pipeline prior to insertion where appropriate,
--   or insert raw fields and rely on generated columns where defined. Generated columns above assume inputs obey checks (non-negative).
-- - Keep your excluded_records populated during ETL with the raw row and reason to satisfy transparency requirement.
-- - If you need geo-queries (radius, nearest neighbors), consider PostGIS (geometry/geography) and spatial indexes.
-- -----------------------------

