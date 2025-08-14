**This is the single source of truth for our data structure. All code must conform to this model.**

### Table: `listings` (Core listing information)
- `id` (UUID, Primary Key)
- `status` (ENUM: 'available', 'rented', 'pending_review', 'rejected')
- `source_url` (TEXT, UNIQUE)
- `title` (TEXT)
- `description` (TEXT)
- `price_monthly_vnd` (INTEGER)
- `area_m2` (NUMERIC)
- `address_street`, `address_ward`, `address_district` (TEXT)
- `latitude`, `longitude` (NUMERIC)
- `contact_phone` (TEXT)
- `image_urls` (TEXT ARRAY)

### Table: `attributes` (The dictionary of all possible amenities/properties)
- `id` (INTEGER, Primary Key)
- `type` (ENUM: 'boolean', 'string', 'integer', 'enum')
- `name` (TEXT, e.g., "Điều hoà")
- `slug` (TEXT, e.g., "air_conditioner")
- `possible_values` (TEXT ARRAY, for 'enum' type)

### Table: `listing_attributes` (Connects a listing to its attributes and their values)
- `listing_id` (UUID, Foreign Key to `listings.id`)
- `attribute_id` (INTEGER, Foreign Key to `attributes.id`)
- `value_string` (TEXT)
- `value_integer` (INTEGER)
- `value_boolean` (BOOLEAN)

**Key Principle:** All interactions with these tables from the backend (Python Cloud Functions) MUST use **SQLAlchemy Core** and be wrapped in **database transactions** to ensure data integrity.