// src/types/index.ts

/**
 * Defines the structure of a single attribute from the API.
 * This is the schema for our dynamic form fields.
 */
export interface Attribute {
  id: number;
  name: string;
  slug: string;
  type: 'boolean' | 'string' | 'integer' | 'enum';
  possible_values: string[] | null;
}

/**
 * Basic form data structure for the static part of the listing.
 * Matches the core fields from our `listings` table schema.
 */
export interface ListingFormData {
  title: string;
  description: string;
  price_monthly_vnd: number | '';
  area_m2: number | '';
  address_ward: string;
  address_district: string;
}

/**
 * API Response structure from the `create_listing` Cloud Function.
 */
export interface CreateListingResponse {
  success: boolean;
  id?: string;
  message?: string;
}

/**
 * Represents a single attribute of a listing, such as an amenity or a rule.
 * This aligns with the data shape returned by the get_listings API.
 */
export interface ListingAttribute {
  name: string;
  slug: string;
  value: string | number | boolean;
}

/**
 * Represents a full listing, including its core data and attributes.
 * This aligns with the data shape returned by the get_listings API.
 */
export interface Listing {
  id: string;
  title: string;
  description: string;
  price_monthly_vnd: number;
  area_m2: number;
  address_ward: string;
  address_district: string;
  attributes: ListingAttribute[];
  image_urls: string[];
  created_at: string;
  updated_at: string;
}
