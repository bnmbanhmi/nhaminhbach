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
import SearchBar from '../components/ui/SearchBar';

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
  status: searchParams.get('status') ? searchParams.get('status')!.split(',') : [],
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
  if (debouncedFilters.status) params.set('status', Array.isArray(debouncedFilters.status) ? debouncedFilters.status.join(',') : String(debouncedFilters.status));

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
    if (debouncedFilters.status) next.set('status', Array.isArray(debouncedFilters.status) ? debouncedFilters.status.join(',') : String(debouncedFilters.status));
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

        // Client-side filter by amenities (match attribute values, not just presence)
        if (debouncedFilters.amenities && debouncedFilters.amenities.length > 0) {
          fetchedListings = fetchedListings.filter(listing => {
            if (!listing.attributes) return false;
            // For each selected amenity slug, ensure the listing has a matching attribute value
            for (const slug of debouncedFilters.amenities!) {
              const filterVal = (debouncedFilters as any)[slug];
              const attr = listing.attributes.find((a: any) => a.slug === slug);
              if (!attr) return false;
              const val = attr.value;

              // If the filter value is undefined, treat it as a truthy presence filter
              if (filterVal === undefined) {
                if (!(val === true || val === 'true' || val === 1 || val === '1')) return false;
              } else if (typeof filterVal === 'boolean') {
                // boolean filter: require truthy value when true
                if (filterVal) {
                  if (!(val === true || val === 'true' || val === 1 || val === '1')) return false;
                } else {
                  // if explicit false, require falsy
                  if (val === true || val === 'true' || val === 1 || val === '1') return false;
                }
              } else if (Array.isArray(filterVal)) {
                // selected multiple options (enum/integer): check membership
                const matched = (filterVal as Array<any>).some(f => String(f) === String(val) || Number(f) === Number(val));
                if (!matched) return false;
              } else {
                // scalar value (string/number)
                if (String(filterVal) !== String(val)) return false;
              }
            }
            return true;
          });
        }
        // Client-side filter by district, price and area (in case API doesn't support all filters)
        if (debouncedFilters.district) {
          const wanted = String(debouncedFilters.district).toLowerCase();
          fetchedListings = fetchedListings.filter(listing => (String(listing.address_district || '').toLowerCase() === wanted));
        }

        if (debouncedFilters.minPrice || debouncedFilters.maxPrice) {
          const minP = debouncedFilters.minPrice ? Number(debouncedFilters.minPrice) : undefined;
          const maxP = debouncedFilters.maxPrice ? Number(debouncedFilters.maxPrice) : undefined;
          fetchedListings = fetchedListings.filter(listing => {
            const p = Number(listing.price_monthly_vnd || 0);
            if (!isNaN(minP as number) && p < (minP as number)) return false;
            if (!isNaN(maxP as number) && p > (maxP as number)) return false;
            return true;
          });
        }

        if (debouncedFilters.minArea || debouncedFilters.maxArea) {
          const minA = debouncedFilters.minArea ? Number(debouncedFilters.minArea) : undefined;
          const maxA = debouncedFilters.maxArea ? Number(debouncedFilters.maxArea) : undefined;
          fetchedListings = fetchedListings.filter(listing => {
            const a = Number(listing.area_m2 || 0);
            if (!isNaN(minA as number) && a < (minA as number)) return false;
            if (!isNaN(maxA as number) && a > (maxA as number)) return false;
            return true;
          });
        }

        // Client-side filter by status (if provided)
        if (debouncedFilters.status && (Array.isArray(debouncedFilters.status) ? debouncedFilters.status.length > 0 : String(debouncedFilters.status).length > 0)) {
          const statuses = Array.isArray(debouncedFilters.status) ? debouncedFilters.status : [String(debouncedFilters.status)];
          fetchedListings = fetchedListings.filter(listing => statuses.includes(listing.status));
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
    <div className="w-full px-3 sm:px-4 md:px-6 lg:px-8">
      {/* Hero Section with Central Search Bar */}
      <div className="text-center py-6 sm:py-10 mb-4 sm:mb-6">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 mb-3 sm:mb-4">
          Tìm phòng trọ Hà Nội
        </h1>
        <p className="text-gray-600 text-base sm:text-lg mb-6 sm:mb-8 max-w-2xl mx-auto">
          Nguồn tin đáng tin cậy nhất. Gõ mã phòng để xem ngay.
        </p>
        
        {/* Central Search Bar - Google Style */}
        <div className="max-w-2xl mx-auto">
          <SearchBar 
            placeholder="Nhập mã phòng (VD: AB1) hoặc tìm kiếm..."
            autoFocus={false}
          />
        </div>
      </div>
      
      {/* Filter Section */}
      <div className="mb-4 sm:mb-6">
        <FilterBar value={filters} onChange={handleFilterChange} amenities={attributes} isAmenitiesLoading={isAttributesLoading} />
      </div>
      {error && (
        <div className="mt-2 mb-4 p-2 bg-red-50 text-red-700 rounded text-sm sm:text-base">Lỗi khi tải danh sách: {error.message}</div>
      )}
      {isLoading ? (
        <div className="text-center py-6 text-base sm:text-lg">Đang tải danh sách…</div>
      ) : listings.length === 0 ? (
        <div className="text-center py-6 text-gray-600 text-base sm:text-lg">Không có kết quả phù hợp với bộ lọc.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 justify-items-center w-full">
          {listings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      )}
    </div>
  );
};

export default HomePage;