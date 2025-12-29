# Data Models

## Schema Overview
The database uses **PostgreSQL**. The core design pattern is **Entity-Attribute-Value (EAV)** to support dynamic property features without schema migrations for every new amenity.

## Tables

### `listings`
Core property information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `status` | Enum | `available`, `rented`, `pending_review`, `rejected` |
| `title` | Text | Listing headline |
| `description` | Text | Full content |
| `price_monthly_vnd` | Integer | Price in VND |
| `area_m2` | Decimal | Size in square meters |
| `address_district` | Text | District name |
| `address_ward` | Text | Ward name |
| `full_geo_id` | Text | Unique GeoID (e.g., `29CG.AB1`) |
| `source_url` | Text | Unique source link (deduplication key) |

### `attributes`
Definitions of available features.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Serial | Primary Key |
| `name` | Text | Display name (e.g., "Air Conditioner") |
| `slug` | Text | Machine name (e.g., "ac") |
| `type` | Enum | `boolean`, `integer`, `string` |

### `listing_attributes` (EAV Link)
Connects listings to values.

| Column | Type | Description |
|--------|------|-------------|
| `listing_id` | UUID | FK to listings |
| `attribute_id` | Integer | FK to attributes |
| `value_boolean` | Boolean | Value if type=boolean |
| `value_integer` | Integer | Value if type=integer |
| `value_string` | Text | Value if type=string |
