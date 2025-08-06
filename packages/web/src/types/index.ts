// src/types/index.ts

/**
 * Represents the structure of a single rental listing,
 * aligning with the `listings` table in the database schema.
 */
export interface Listing {
  id: string;
  status: 'available' | 'rented' | 'pending_review' | 'rejected';
  source_url: string;
  title: string;
  description: string;
  price_monthly_vnd: number;
  area_m2: number;
  address_street: string;
  address_ward: string;
  address_district: string;
  latitude: number;
  longitude: number;
  contact_phone: string;
  image_urls: string[];
}
