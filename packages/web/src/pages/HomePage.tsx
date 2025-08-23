// src/pages/HomePage.tsx
import React, { useState, useEffect } from 'react';
import type { Listing } from '../types';
import ListingCard from '../components/listings/ListingCard';
import { API_BASE_URL } from '../config'; // <-- THAY ĐỔI: Import từ file config
import FilterBar from '../components/listings/FilterBar';
import type { FilterState } from '../components/listings/FilterBar';
import type { Attribute } from '../types';
import { useDebouncedValue } from '../hooks/useDebouncedValue';
import { useSearchParams } from 'react-router-dom';

// Sử dụng biến đã import để xây dựng endpoint
const API_ENDPOINT = `${API_BASE_URL}/get_listings`;

const HomePage: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const [attributes, setAttributes] = useState<Attribute[]>([]);
  const [isAttributesLoading, setIsAttributesLoading] = useState<boolean>(true);

  // Parse amenities from searchParams
  const amenitiesParam = searchParams.get('amenities');
  const initialFilters: FilterState = {
    district: searchParams.get('district') || undefined,
    minPrice: searchParams.get('minPrice') || undefined,
    maxPrice: searchParams.get('maxPrice') || undefined,
    minArea: searchParams.get('minArea') || undefined,
    maxArea: searchParams.get('maxArea') || undefined,
    status: searchParams.get('status') || undefined,
    amenities: amenitiesParam ? amenitiesParam.split(',') : [],
  };
  // Fetch attributes for amenities filter
  useEffect(() => {
    const fetchAttributes = async () => {
      setIsAttributesLoading(true);
      try {
        const resp = await fetch(`${API_BASE_URL}/get_all_attributes`);
        if (!resp.ok) throw new Error('Failed to fetch attributes');
        const data = await resp.json();
        setAttributes(data);
      } catch (e) {
        // Ignore error for now
      } finally {
        setIsAttributesLoading(false);
      }
    };
    fetchAttributes();
  }, []);

  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const debouncedFilters = useDebouncedValue(filters, 300);

  useEffect(() => {
    const fetchListings = async () => {
      setIsLoading(true);
      try {
        const params = new URLSearchParams();
        if (debouncedFilters.district) params.set('district', debouncedFilters.district);
        if (debouncedFilters.minPrice) params.set('min_price', debouncedFilters.minPrice);
        if (debouncedFilters.maxPrice) params.set('max_price', debouncedFilters.maxPrice);
        if (debouncedFilters.minArea) params.set('min_area', debouncedFilters.minArea);
        if (debouncedFilters.maxArea) params.set('max_area', debouncedFilters.maxArea);
        if (debouncedFilters.status) params.set('status', debouncedFilters.status);

        // Update URL for shareability
        setSearchParams((prev) => {
          const next = new URLSearchParams(prev as any);
          next.delete('district');
          next.delete('minPrice');
          next.delete('maxPrice');
          next.delete('minArea');
          next.delete('maxArea');
          next.delete('status');
          next.delete('amenities');
          if (debouncedFilters.district) next.set('district', debouncedFilters.district);
          if (debouncedFilters.minPrice) next.set('minPrice', debouncedFilters.minPrice);
          if (debouncedFilters.maxPrice) next.set('maxPrice', debouncedFilters.maxPrice);
          if (debouncedFilters.minArea) next.set('minArea', debouncedFilters.minArea);
          if (debouncedFilters.maxArea) next.set('maxArea', debouncedFilters.maxArea);
          if (debouncedFilters.status) next.set('status', debouncedFilters.status);
          if (debouncedFilters.amenities && debouncedFilters.amenities.length > 0) next.set('amenities', debouncedFilters.amenities.join(','));
          return next;
        });

        const url = `${API_ENDPOINT}?${params.toString()}`;
        const response = await fetch(url);

        let fetchedListings: Listing[] = [];
        // If public listings endpoint isn't deployed (404), fall back to admin endpoint
        if (response.status === 404) {
          const adminUrl = `${API_BASE_URL}/get_admin_listings?limit=50&offset=0`;
          const adminResp = await fetch(adminUrl);
          if (!adminResp.ok) throw new Error(`Admin endpoint error status: ${adminResp.status}`);
          const adminData = await adminResp.json();
          if (Array.isArray(adminData)) {
            fetchedListings = adminData as any;
          } else if (Array.isArray(adminData.listings)) {
            fetchedListings = adminData.listings as any;
          } else {
            throw new Error('Unexpected admin listings response shape');
          }
        } else {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          fetchedListings = Array.isArray(data) ? data : (data.listings || []);
        }

        // Client-side filter by amenities
        if (debouncedFilters.amenities && debouncedFilters.amenities.length > 0) {
          fetchedListings = fetchedListings.filter(listing => {
            if (!listing.attributes) return false;
            const attrs = listing.attributes.filter((a: any) => debouncedFilters.amenities!.includes(a.slug) && (a.value === true || a.value === 'true' || a.value === 1 || a.value === '1'));
            return attrs.length === (debouncedFilters.amenities ? debouncedFilters.amenities.length : 0);
          });
        }
        setListings(fetchedListings);
      } catch (e) {
        if (e instanceof Error) setError(e);
        else setError(new Error('An unknown error occurred'));
      } finally {
        setIsLoading(false);
      }
    };
    fetchListings();
  }, [debouncedFilters]);

  // Always render the filter UI; show status messages inline so users can adjust filters

  const handleFilterChange = (nextFilters: typeof filters) => setFilters(nextFilters);

  return (
    <div className="w-full px-1 md:px-2 lg:px-3">
      <h1 className="text-3xl font-bold mb-6">Available Listings</h1>
      <FilterBar value={filters} onChange={handleFilterChange} amenities={attributes.filter(a => a.type === 'boolean')} isAmenitiesLoading={isAttributesLoading} />
      {error && (
        <div className="mt-2 mb-4 p-2 bg-red-50 text-red-700 rounded">Error loading listings: {error.message}</div>
      )}
      {isLoading ? (
        <div className="text-center py-6">Loading listings…</div>
      ) : listings.length === 0 ? (
        <div className="text-center py-6 text-gray-600">No listings match your filters.</div>
      ) : (
        <div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-4 md:gap-6 justify-items-center">
          {listings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      )}
    </div>
  );
};

export default HomePage;