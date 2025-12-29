# Web Frontend Architecture

## Executive Summary
The Web Frontend is a high-performance, responsive Single Page Application (SPA) built with React 19 and Vite. It serves as the primary user interface for property seekers and administrators.

## Technology Stack
-   **Framework**: React 19
-   **Build Tool**: Vite
-   **Styling**: TailwindCSS
-   **Routing**: React Router
-   **Language**: TypeScript

## Architecture Pattern
**Component-Based Architecture**: The UI is decomposed into reusable, independent components.
-   **UI Library**: Custom components in `src/components/ui`.
-   **Layouts**: shared page structures in `src/components/layout`.
-   **Pages**: Route-specific views in `src/pages`.

## Directory Structure
```
packages/web/src/
├── components/
│   ├── ui/          # Atomic components (Buttons, Inputs, SearchBar)
│   ├── layout/      # Navbar, Footer, MainLayout
│   └── ...
├── pages/           # Page components mapped to routes
├── utils/           # Helper functions (GeoID validation)
├── App.tsx          # Root component
└── main.tsx         # Entry point
```

## Key Features
-   **GeoID Search**: Intelligent search bar that detects and routes GeoIDs (`29CG.AB1`).
-   **Listing Display**: Rich presentation of rental listings with images and attributes.
-   **Admin Dashboard**: Interface for reviewing and approving listings.
