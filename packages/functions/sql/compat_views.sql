-- Compatibility views to expose legacy `listings` and `listing_attributes` shape
-- Safe and reversible. Drop the views to rollback.

-- listings view (aliases v_current_listings columns to legacy names)
CREATE OR REPLACE VIEW public.listings AS
SELECT
  v.room_history_id::text AS id,
  v.status,
  v.source_url,
  v.title,
  v.description,
  v.price_monthly_vnd,
  v.area_m2,
  v.address_street,
  v.address_ward,
  v.address_district,
  v.latitude,
  v.longitude,
  v.contact_phone,
  v.image_urls,
  v.created_at,
  v.attributes
FROM v_current_listings v;

-- listing_attributes view (expand JSONB attributes into rows matched to attributes dictionary)
-- Note: this view exposes attribute values typed into the three legacy columns.
CREATE OR REPLACE VIEW public.listing_attributes AS
SELECT
  v.room_history_id::text AS listing_id,
  a.id AS attribute_id,
  CASE WHEN a.type = 'boolean' THEN (v.attributes ->> a.slug)::boolean ELSE NULL END AS value_boolean,
  CASE WHEN a.type = 'integer' THEN (v.attributes ->> a.slug)::integer ELSE NULL END AS value_integer,
  CASE WHEN a.type IN ('string','enum') THEN v.attributes ->> a.slug ELSE NULL END AS value_string
FROM v_current_listings v
-- ensure attributes jsonb is not null to avoid errors
CROSS JOIN LATERAL (
  SELECT * FROM jsonb_each(v.attributes) AS t(slug, value)
) j
JOIN attributes a ON a.slug = j.slug;
