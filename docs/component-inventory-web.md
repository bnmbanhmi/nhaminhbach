# Component Inventory (Web)

## UI Components (`src/components/ui`)

### `SearchBar`
-   **Purpose**: Universal search input.
-   **Features**:
    -   Detects GeoID patterns automatically.
    -   Navigates to detail page on exact match.
    -   Supports standard text search.

### `DualRange` / `SimpleDualSlider`
-   **Purpose**: Price and Area filtering.
-   **State**: Controlled component.

## Layout Components (`src/components/layout`)

### `MainLayout`
-   **Purpose**: Wrapper for all public pages.
-   **Structure**: Navbar + Content + Footer.

### `Navbar`
-   **Purpose**: Top navigation bar.
-   **Features**: Links to Home, About, Post Listing.

## Pages (`src/pages`)

-   **Home**: Listing feed with filters.
-   **ListingDetail**: Single listing view.
-   **AdminDashboard**: QC interface.
