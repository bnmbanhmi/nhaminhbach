// src/types/index.ts

/**
 * Represents a single attribute of a listing, such as an amenity or a rule.
 * This aligns with the data shape returned by the get_listings API.
 */
export interface ListingAttribute {
  name: string;
  slug: string;
  value: string | number | boolean;
  type: 'boolean' | 'string' | 'integer' | 'enum';
}

/**
 * Represents the complete structure of a single rental listing object
 * as fetched from the API.
 */
export interface Listing {
  id: string;
  status: 'available' | 'rented' | 'pending_review' | 'rejected';
  source_url: string;
  title: string;
  description: string;
  price_monthly_vnd: number;
  area_m2: number;
  address_street: string | null;
  address_ward: string;
  address_district: string;
  latitude: number | null;
  longitude: number | null;
  contact_phone: string | null;
  image_urls: string[] | null;
  attributes: ListingAttribute[];
}