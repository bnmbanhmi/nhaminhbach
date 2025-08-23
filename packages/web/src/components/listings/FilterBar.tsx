// src/components/listings/FilterBar.tsx
import React from 'react';

export interface FilterState {
  district?: string;
  minPrice?: string;
  maxPrice?: string;
  minArea?: string;
  maxArea?: string;
  status?: string;
  amenities?: string[];
}

import type { Attribute } from '../../types';

interface Props {
  value: FilterState;
  onChange: (next: FilterState) => void;
  amenities?: Attribute[];
  isAmenitiesLoading?: boolean;
}

const districts = ['Cầu Giấy', 'Đống Đa', 'Ba Đình', 'Hai Bà Trưng', 'Hoàn Kiếm'];
const statuses = ['available', 'rented', 'pending_review', 'rejected'];

const FilterBar: React.FC<Props> = ({ value, onChange, amenities = [], isAmenitiesLoading }) => {
  const update = (patch: Partial<FilterState>) => onChange({ ...value, ...patch });
  const reset = () => onChange({ district: undefined, minPrice: undefined, maxPrice: undefined, minArea: undefined, maxArea: undefined, status: undefined, amenities: [] });
  // Amenity checkbox handler
  const handleAmenityToggle = (slug: string) => {
    const current = value.amenities || [];
    if (current.includes(slug)) {
      update({ amenities: current.filter(s => s !== slug) });
    } else {
      update({ amenities: [...current, slug] });
    }
  };

  return (
    <div className="mb-6 p-3 bg-white rounded-md shadow-sm flex flex-col md:flex-row gap-3 items-start md:items-center" role="region" aria-label="Listing filters">
      <div className="flex gap-2 items-center">
        <label className="text-sm mr-2" htmlFor="filter-district">District</label>
        <select
          id="filter-district"
          aria-label="Filter by district"
          value={value.district || ''}
          onChange={(e) => update({ district: e.target.value || undefined })}
          className="border rounded px-2 py-1"
        >
          <option value="">All</option>
          {districts.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      <div className="flex gap-2 items-center">
        <label className="text-sm mr-2" htmlFor="filter-min-price">Price (VND)</label>
        <input
          id="filter-min-price"
          type="number"
          placeholder="min"
          aria-label="Minimum price"
          value={value.minPrice || ''}
          onChange={(e) => update({ minPrice: e.target.value || undefined })}
          className="border rounded px-2 py-1 w-24"
        />
        <input
          id="filter-max-price"
          type="number"
          placeholder="max"
          aria-label="Maximum price"
          value={value.maxPrice || ''}
          onChange={(e) => update({ maxPrice: e.target.value || undefined })}
          className="border rounded px-2 py-1 w-24"
        />
      </div>

      <div className="flex gap-2 items-center">
        <label className="text-sm mr-2" htmlFor="filter-min-area">Area (m²)</label>
        <input
          id="filter-min-area"
          type="number"
          placeholder="min"
          aria-label="Minimum area"
          value={value.minArea || ''}
          onChange={(e) => update({ minArea: e.target.value || undefined })}
          className="border rounded px-2 py-1 w-20"
        />
        <input
          id="filter-max-area"
          type="number"
          placeholder="max"
          aria-label="Maximum area"
          value={value.maxArea || ''}
          onChange={(e) => update({ maxArea: e.target.value || undefined })}
          className="border rounded px-2 py-1 w-20"
        />
      </div>

      <div className="flex gap-2 items-center">
        <label className="text-sm mr-2" htmlFor="filter-status">Status</label>
        <select
          id="filter-status"
          aria-label="Filter by status"
          value={value.status || ''}
          onChange={(e) => update({ status: e.target.value || undefined })}
          className="border rounded px-2 py-1"
        >
          <option value="">All</option>
          {statuses.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
      
      {/* Amenities filter */}
      <div className="flex gap-2 items-center">
        <span className="text-sm mr-2">Amenities</span>
        {isAmenitiesLoading ? (
          <span className="text-gray-400 text-xs">Loading…</span>
        ) : amenities.length === 0 ? (
          <span className="text-gray-400 text-xs">No amenities</span>
        ) : (
          <div className="flex flex-wrap gap-2">
            {amenities.map(attr => (
              <label key={attr.slug} className="flex items-center gap-1 text-xs bg-gray-100 px-2 py-1 rounded">
                <input
                  type="checkbox"
                  checked={value.amenities?.includes(attr.slug) || false}
                  onChange={() => handleAmenityToggle(attr.slug)}
                />
                {attr.name}
              </label>
            ))}
          </div>
        )}
      </div>
      <div className="ml-auto flex gap-2">
        <button type="button" onClick={reset} className="text-sm text-gray-600 underline">Reset</button>
      </div>
    </div>
  );
};

export default FilterBar;
