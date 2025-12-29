# API Contracts

## Base URL
-   **Production**: `https://nhaminhbach.com/api` (approximate)
-   **Local**: `http://localhost:8000`

## Endpoints

### Listings

#### `GET /get_listings`
-   **Description**: Get all available listings.
-   **Response**: `Array<Listing>`

#### `GET /get_listing_by_id`
-   **Params**: `id` (UUID)
-   **Response**: `Listing`

#### `GET /get_listing_by_geoid`
-   **Params**: `geoid` (e.g., "29CG.AB1")
-   **Response**: `Listing`

#### `POST /create_listing`
-   **Body**: `{ listing: ListingData, attributes: AttributeData[] }`
-   **Response**: `{ id: UUID, message: string }`

### Administration

#### `POST /update_listing_status`
-   **Body**: `{ listing_id: UUID, status: "available" | "rejected" }`
-   **Auth**: Required (Implied)

#### `POST /ingest_scraped_data`
-   **Headers**: `X-API-Key`
-   **Body**: `{ posts: RawPost[] }`
-   **Description**: Ingests raw data from scrapers.

### Metadata

#### `GET /get_all_attributes`
-   **Description**: Returns list of available attributes for UI rendering.
