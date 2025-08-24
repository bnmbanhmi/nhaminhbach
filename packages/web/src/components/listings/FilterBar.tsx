// src/components/listings/FilterBar.tsx
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import translateEnumValue from '../../utils/translations';
import type { Attribute } from '../../types';
import SimpleDualSlider from '../ui/SimpleDualSlider';

export interface FilterState {
  district?: string;
  minPrice?: string;
  maxPrice?: string;
  minArea?: string;
  maxArea?: string;
  status?: string | string[];
  amenities?: string[];
  // Dynamic amenity keys: string-indexed values (boolean, number, string)
  [amenitySlug: string]: string | number | boolean | string[] | number[] | undefined;
}

interface Props {
  value: FilterState;
  onChange: (next: FilterState) => void;
  amenities?: Attribute[];
  isAmenitiesLoading?: boolean;
}

const districts = ['Cầu Giấy', 'Đống Đa', 'Ba Đình', 'Hai Bà Trưng', 'Hoàn Kiếm'];
const statuses = ['available', 'rented', 'pending_review', 'rejected'];

// use shared translateEnumValue from utils/translations

const FilterBar: React.FC<Props> = ({ value, onChange, amenities = [], isAmenitiesLoading: _isAmenitiesLoading }) => {
  // Local draft state: edits are staged locally and applied when user clicks "Apply"
  const [draft, setDraft] = useState<FilterState>(value);
  useEffect(() => setDraft(value), [value]);

  const update = (patch: Partial<FilterState>) => setDraft(prev => ({ ...(prev || {}), ...patch }));

  // Using rc-slider Range component for smooth dual-thumb sliders.

  // Helper to set an amenity attribute and keep `draft.amenities` array in sync.
  const setAmenityValue = (slug: string, value: any) => {
    setDraft(prev => {
      const next: FilterState = { ...(prev || {}) };
      // assign the raw value for the specific attribute
      if (value === undefined) {
        delete next[slug];
      } else {
        next[slug] = value;
      }

      // compute amenities array membership
      const currAmenities = Array.isArray(prev?.amenities) ? [...(prev!.amenities as string[])] : [];
      const shouldInclude = !(value === undefined || value === false || (Array.isArray(value) && value.length === 0) || value === '');
      if (shouldInclude) {
        if (!currAmenities.includes(slug)) currAmenities.push(slug);
      } else {
        const idx = currAmenities.indexOf(slug);
        if (idx !== -1) currAmenities.splice(idx, 1);
      }
      next.amenities = currAmenities.length ? currAmenities : undefined;
      return next;
    });
  };

  const resetDraft = () => {
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
    setDraft(resetState);
  };
  // Amenity checkbox handler
  // Removed legacy amenities array logic

  const [showAmenities, setShowAmenities] = useState(false);

  const amenityAttributes = amenities;

  const applyFilters = () => {
    // Ensure we pass a shallow copy
    setIsApplying(true);
    onChange({ ...(draft || {}) });
    // Close amenities panel for better UX
    setShowAmenities(false);
  };

  const [isApplying, setIsApplying] = useState(false);

  // Clear applying state when parent `value` reflects the applied draft
  useEffect(() => {
    try {
      if (JSON.stringify(value || {}) === JSON.stringify(draft || {})) {
        setIsApplying(false);
      }
    } catch (e) {
      // ignore serialization errors
      setIsApplying(false);
    }
  }, [value, draft]);

  return (
    <div className="mb-6 p-3 bg-white rounded-md shadow-sm w-full" role="region" aria-label="Bộ lọc danh sách">
      {/* Base attributes */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-start w-full">
        {/* District */}
        <div className="flex flex-col gap-2">
          <label className="text-sm" htmlFor="filter-district">Quận</label>
          <select
            id="filter-district"
            aria-label="Lọc theo quận"
            value={draft?.district || ''}
            onChange={(e) => update({ district: e.target.value || undefined })}
            className="border rounded px-2 py-1"
          >
            <option value="">Tất cả</option>
            {districts.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>
        {/* Price */}
        <div className="flex flex-col gap-2">
          <label className="text-sm">Giá (VND)</label>
          {/* removed top Min/Max labels per design */}
          <SimpleDualSlider
            min={0}
            max={10000000}
            step={50000}
            values={[draft?.minPrice ? Number(draft.minPrice) : 0, draft?.maxPrice ? Number(draft.maxPrice) : 10000000]}
            onChange={(v) => update({ minPrice: String(v[0]), maxPrice: String(v[1]) })}
            format={(n) => `${(n / 1000000).toFixed(1)}tr`}
            ariaLabel="Giá"
          />
        </div>
        {/* Area */}
        <div className="flex flex-col gap-2">
          <label className="text-sm">Diện tích (m²)</label>
          {/* removed top Min/Max labels per design */}
          <SimpleDualSlider
            min={0}
            max={100}
            step={1}
            values={[draft?.minArea ? Number(draft.minArea) : 0, draft?.maxArea ? Number(draft.maxArea) : 100]}
            onChange={(v) => update({ minArea: String(v[0]), maxArea: String(v[1]) })}
            format={(n) => `${n}m²`}
            ariaLabel="Diện tích"
          />
        </div>
        {/* Trạng thái (multi-select) */}
        <div className="flex flex-col gap-2">
          <label className="text-sm" htmlFor="filter-status">Trạng thái</label>
          <Select
            inputId="filter-status"
            isMulti
            options={statuses.map(s => ({ value: s, label: translateEnumValue('status', s) }))}
            value={
              Array.isArray(draft?.status)
                ? (draft!.status as string[]).map(v => ({ value: v, label: translateEnumValue('status', v) }))
                : draft?.status
                ? [{ value: String(draft.status), label: translateEnumValue('status', draft.status) }]
                : []
            }
            onChange={(selected) => {
              const vals = (selected as Array<any> || []).map(s => s.value);
              update({ status: vals.length ? vals : undefined });
            }}
            classNamePrefix="react-select"
            styles={{ menu: (provided) => ({ ...provided, zIndex: 50 }) }}
            aria-label="Lọc theo trạng thái"
            placeholder="Tất cả"
          />
        </div>
      </div>
      {/* Show More Amenities Section */}
      <div className="mt-4">
        <button
          type="button"
          className="text-sm text-primary underline"
          onClick={() => setShowAmenities((prev) => !prev)}
        >
          {showAmenities ? 'Ẩn tiện ích' : 'Hiện thêm tiện ích'}
        </button>
        {showAmenities && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mt-4">
            {amenityAttributes.map(attr => {
              // read the staged value from draft so interactions update immediately
              const amenityValue = draft ? draft[attr.slug] : undefined;
              let inputEl = null;
              if (attr.type === 'boolean') {
                inputEl = (
                  <button
                    type="button"
                    aria-pressed={!!amenityValue}
                    onClick={() => setAmenityValue(attr.slug, !amenityValue)}
                    className={`px-3 py-1 rounded border text-xs font-medium transition-colors duration-200 ${amenityValue ? 'bg-primary text-white' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'}`}
                  >
                    {attr.name}
                  </button>
                );
                } else if (attr.type === 'integer') {
                  // Use react-select for better multi-select UX (mobile friendly)
                  const intOptions = [0, 1, 2, 3].map(v => ({ value: v, label: String(v) }));
                  inputEl = (
                    <div className="flex flex-col gap-1 w-full">
                      <label className="text-xs font-medium mb-1">{attr.name}</label>
                      <Select
                        isMulti
                        options={intOptions}
                                    value={Array.isArray(amenityValue) ? (amenityValue as Array<number>).map(v => ({ value: v, label: String(v) })) : []}
                        onChange={(selected) => {
                          const vals = (selected as Array<any> || []).map(s => Number(s.value));
                          setAmenityValue(attr.slug, vals.length ? vals : undefined);
                        }}
                        classNamePrefix="react-select"
                        styles={{ menu: (provided) => ({ ...provided, zIndex: 50 }) }}
                        aria-label={attr.name}
                      />
                      {Array.isArray(amenityValue) && (amenityValue as Array<number>).length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(amenityValue as Array<number>).map((v: number|string) => (
                            <span key={String(v)} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs">{String(v)}</span>
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
                      onChange={e => setAmenityValue(attr.slug, e.target.value || undefined)}
                      className="border rounded px-2 py-1 w-full text-xs"
                      placeholder={attr.name}
                    />
                  </div>
                );
              } else if (attr.type === 'enum' && attr.possible_values) {
                const enumOptions = attr.possible_values.map(v => ({ value: v, label: translateEnumValue(attr.slug, v) }));
                inputEl = (
                  <div className="flex flex-col gap-1 w-full">
                    <label className="text-xs font-medium mb-1">{attr.name}</label>
                    <Select
                      isMulti
                      options={enumOptions}
                      value={Array.isArray(amenityValue) ? (amenityValue as Array<any>).map(v => ({ value: v, label: translateEnumValue(attr.slug, v) })) : []}
                      onChange={(selected) => {
                        const vals = (selected as Array<any> || []).map(s => s.value);
                        setAmenityValue(attr.slug, vals.length ? vals : undefined);
                      }}
                      classNamePrefix="react-select"
                      styles={{ menu: (provided) => ({ ...provided, zIndex: 50 }) }}
                      aria-label={attr.name}
                    />
                    {Array.isArray(amenityValue) && (amenityValue as Array<any>).length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {(amenityValue as Array<any>).map((v) => (
                          <span key={String(v)} className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs">{translateEnumValue(attr.slug, v)}</span>
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
        <div className="flex justify-end mt-2 gap-3">
        <button type="button" onClick={resetDraft} className="text-sm text-gray-600 underline">Đặt lại</button>
        <button type="button" onClick={applyFilters} className="text-sm bg-primary text-white px-3 py-1 rounded" disabled={isApplying}>
          {isApplying ? 'Đang áp dụng…' : 'Áp dụng'}
        </button>
      </div>
    </div>
  );
};

export default FilterBar;
