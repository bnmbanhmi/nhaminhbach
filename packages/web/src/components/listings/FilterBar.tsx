// src/components/listings/FilterBar.tsx
import React, { useState } from 'react';

export interface FilterState {
  district?: string;
  minPrice?: string;
  maxPrice?: string;
  minArea?: string;
  maxArea?: string;
  status?: string;
  // Dynamic amenity keys: string-indexed values (boolean, number, string)
  [amenitySlug: string]: string | number | boolean | string[] | number[] | undefined;
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
  const reset = () => {
    // Reset all known filter fields and dynamic amenity keys
    const resetState: FilterState = {
      district: undefined,
      minPrice: undefined,
      maxPrice: undefined,
      minArea: undefined,
      maxArea: undefined,
      status: undefined,
    };
    if (amenities && amenities.length > 0) {
      amenities.forEach(attr => {
        resetState[attr.slug] = undefined;
      });
    }
    onChange(resetState);
  };
  // Amenity checkbox handler
  // Removed legacy amenities array logic

  const [showAmenities, setShowAmenities] = useState(false);

  // Split base and amenity attributes
  const baseAttributes = [
    { label: 'District', id: 'filter-district', value: value.district || '', options: districts, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => update({ district: e.target.value || undefined }) },
    { label: 'Price (VND)', id: 'filter-price', value: [value.minPrice || '', value.maxPrice || ''], onChange: (min: string, max: string) => update({ minPrice: min || undefined, maxPrice: max || undefined }) },
    { label: 'Area (m²)', id: 'filter-area', value: [value.minArea || '', value.maxArea || ''], onChange: (min: string, max: string) => update({ minArea: min || undefined, maxArea: max || undefined }) },
    { label: 'Status', id: 'filter-status', value: value.status || '', options: statuses, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => update({ status: e.target.value || undefined }) },
  ];

  const amenityAttributes = amenities;

  return (
    <div className="mb-6 p-3 bg-white rounded-md shadow-sm w-full" role="region" aria-label="Listing filters">
      {/* Base attributes */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-start w-full">
        {/* District */}
        <div className="flex flex-col gap-2">
          <label className="text-sm" htmlFor="filter-district">District</label>
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
        {/* Price */}
        <div className="flex flex-col gap-2">
          <label className="text-sm" htmlFor="filter-min-price">Price (VND)</label>
          <div className="flex gap-2">
            <input
              id="filter-min-price"
              type="number"
              placeholder="min"
              aria-label="Minimum price"
              value={value.minPrice || ''}
              onChange={(e) => update({ minPrice: e.target.value || undefined })}
              className="border rounded px-2 py-1 w-20"
            />
            <input
              id="filter-max-price"
              type="number"
              placeholder="max"
              aria-label="Maximum price"
              value={value.maxPrice || ''}
              onChange={(e) => update({ maxPrice: e.target.value || undefined })}
              className="border rounded px-2 py-1 w-20"
            />
          </div>
        </div>
        {/* Area */}
        <div className="flex flex-col gap-2">
          <label className="text-sm" htmlFor="filter-min-area">Area (m²)</label>
          <div className="flex gap-2">
            <input
              id="filter-min-area"
              type="number"
              placeholder="min"
              aria-label="Minimum area"
              value={value.minArea || ''}
              onChange={(e) => update({ minArea: e.target.value || undefined })}
              className="border rounded px-2 py-1 w-16"
            />
            <input
              id="filter-max-area"
              type="number"
              placeholder="max"
              aria-label="Maximum area"
              value={value.maxArea || ''}
              onChange={(e) => update({ maxArea: e.target.value || undefined })}
              className="border rounded px-2 py-1 w-16"
            />
          </div>
        </div>
        {/* Status */}
        <div className="flex flex-col gap-2">
          <label className="text-sm" htmlFor="filter-status">Status</label>
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
      </div>
      {/* Show More Amenities Section */}
      <div className="mt-4">
        <button
          type="button"
          className="text-sm text-primary underline"
          onClick={() => setShowAmenities((prev) => !prev)}
        >
          {showAmenities ? 'Hide Amenities' : 'Show More Amenities'}
        </button>
        {showAmenities && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mt-4">
            {amenityAttributes.map(attr => {
              const amenityValue = value[attr.slug];
              let inputEl = null;
              if (attr.type === 'boolean') {
                inputEl = (
                  <button
                    type="button"
                    aria-pressed={!!amenityValue}
                    onClick={() => update({ [attr.slug]: !amenityValue })}
                    className={`px-3 py-1 rounded border text-xs font-medium transition-colors duration-200 ${amenityValue ? 'bg-primary text-white' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'}`}
                  >
                    {attr.name}
                  </button>
                );
                } else if (attr.type === 'integer') {
                inputEl = (
                  <div className="flex flex-col gap-1 w-full">
                    <label className="text-xs font-medium mb-1">{attr.name}</label>
                    <div className="relative">
                      <select
                        multiple
                        value={Array.isArray(amenityValue) ? amenityValue.map(String) : []}
                        onChange={e => {
                          const selected = Array.from(e.target.selectedOptions).map(opt => opt.value);
                          update({ [attr.slug]: selected.length ? selected.map(Number) : undefined });
                        }}
                        className="border rounded px-2 py-1 w-full text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        size={4}
                        style={{ minHeight: '2.5rem', background: '#fff' }}
                      >
                        {[0,1,2,3].map(val => (
                          <option key={val} value={val}>{val}</option>
                        ))}
                      </select>
                      <span className="absolute right-2 top-2 text-gray-400 pointer-events-none">⇧/⌘+Click to select</span>
                    </div>
                    {Array.isArray(amenityValue) && amenityValue.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {amenityValue.map((v: number|string) => (
                          <span key={v} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs">{v}</span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              } else if (attr.type === 'string') {
                inputEl = (
                  <div className="flex flex-col gap-1 w-full">
                    <label className="text-xs font-medium mb-1">{attr.name}</label>
                    <input
                      type="text"
                      value={typeof amenityValue === 'string' ? amenityValue : ''}
                      onChange={e => update({ [attr.slug]: e.target.value })}
                      className="border rounded px-2 py-1 w-full text-xs"
                      placeholder={attr.name}
                    />
                  </div>
                );
              } else if (attr.type === 'enum' && attr.possible_values) {
                inputEl = (
                  <div className="flex flex-col gap-1 w-full">
                    <label className="text-xs font-medium mb-1">{attr.name}</label>
                    <div className="relative">
                      <select
                        multiple
                        value={Array.isArray(amenityValue) ? amenityValue.map(String) : []}
                        onChange={e => {
                          const selected = Array.from(e.target.selectedOptions).map(opt => opt.value);
                          update({ [attr.slug]: selected.length ? selected : undefined });
                        }}
                        className="border rounded px-2 py-1 w-full text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        size={Math.max(4, attr.possible_values.length)}
                        style={{ minHeight: '2.5rem', background: '#fff' }}
                      >
                        {attr.possible_values.map(val => (
                          <option key={val} value={val}>{val}</option>
                        ))}
                      </select>
                      <span className="absolute right-2 top-2 text-gray-400 pointer-events-none">⇧/⌘+Click to select</span>
                    </div>
                    {Array.isArray(amenityValue) && amenityValue.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {amenityValue.map((v) => (
                          <span key={String(v)} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs">{String(v)}</span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              }
              return (
                <div key={attr.slug} className="flex flex-col gap-1 bg-gray-100 px-2 py-2 rounded items-start">
                  {inputEl}
                </div>
              );
            })}
          </div>
        )}
      </div>
      <div className="flex justify-end mt-2">
        <button type="button" onClick={reset} className="text-sm text-gray-600 underline">Reset</button>
      </div>
    </div>
  );
};

export default FilterBar;
