// src/utils/geoid.ts
/**
 * GeoID Utilities for NhaMinhBach Frontend
 * =========================================
 * 
 * GeoID Format: 29CG.HHHRR
 * - 29: City code (Hà Nội)
 * - CG: Ward code (2 chars)
 * - HHH: House ID (3 chars Base36)
 * - RR: Room ID (2 chars Base36, 00=whole house)
 * 
 * Display Format: AB1 (elastic, removes leading zeros)
 * URL Format: /AB1 or /CGAB1 or /29CGAB1
 */

const BASE36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

/**
 * Convert number to Base36 string with padding
 */
export function toBase36(num: number, width: number = 3): string {
  if (num === 0) return '0'.repeat(width);
  
  let result = '';
  let n = num;
  while (n > 0) {
    result = BASE36[n % 36] + result;
    n = Math.floor(n / 36);
  }
  
  return result.padStart(width, '0');
}

/**
 * Convert Base36 string to number
 */
export function fromBase36(s: string): number {
  return parseInt(s.toUpperCase(), 36);
}

/**
 * Generate a temporary display ID from UUID
 * This is used before the full GeoID migration is complete.
 * 
 * Takes first 6 hex chars of UUID, converts to a 3-char Base36 ID.
 * This gives us 46,656 unique IDs per ward (more than enough for now).
 * 
 * @param uuid - Full UUID string
 * @returns Display ID like "AB1" or "K7M"
 */
export function generateDisplayIdFromUuid(uuid: string): string {
  // Remove dashes and take first 6 hex chars
  const hex = uuid.replace(/-/g, '').slice(0, 6).toUpperCase();
  
  // Convert hex to number, mod by 36^3 (46656) to get 3-char Base36
  const num = parseInt(hex, 16) % (36 * 36 * 36);
  
  // Convert to Base36, remove leading zeros for display
  const base36 = toBase36(num, 3);
  
  // Return compact form (remove leading zeros)
  return base36.replace(/^0+/, '') || '0';
}

/**
 * Generate full GeoID from UUID (temporary bridge)
 * Format: 29XX.0{displayId}00
 */
export function generateFullGeoIdFromUuid(uuid: string, wardCode: string = 'XX'): string {
  const displayId = generateDisplayIdFromUuid(uuid);
  const paddedHouse = displayId.padStart(3, '0');
  return `29${wardCode}.${paddedHouse}00`;
}

/**
 * Format GeoID for display (elastic, removes padding)
 * 
 * Examples:
 * - "29CG.0AB01" → "CGAB1"
 * - "29ND.00A0R" → "NDA.R"
 * - "29CG.W8K00" → "CGW8K"
 */
export function formatGeoIdDisplay(fullGeoId: string): string {
  // Parse: 29CG.HHHRR
  const match = fullGeoId.toUpperCase().match(/(\d{2})([A-Z]{2})\.([0-9A-Z]{3})([0-9A-Z]{2})/);
  if (!match) return fullGeoId;
  
  const [, , ward, house, room] = match;
  
  // Remove leading zeros
  const houseCompact = house.replace(/^0+/, '') || '0';
  const roomCompact = room.replace(/^0+/, '') || '0';
  
  // If room is '00', omit it (whole house)
  if (room === '00') {
    return `${ward}${houseCompact}`;
  }
  
  // For single char house + single char room with alpha, use separator
  if (houseCompact.length === 1 && roomCompact.length === 1) {
    if (!/^\d$/.test(houseCompact) || !/^\d$/.test(roomCompact)) {
      return `${ward}${houseCompact}.${roomCompact}`;
    }
  }
  
  return `${ward}${houseCompact}${roomCompact}`;
}

/**
 * Check if a string looks like a GeoID pattern
 * Matches: AB1, CG.AB1, 29CGAB1, CGAB01, etc.
 */
export function isGeoIdPattern(input: string): boolean {
  const normalized = input.toUpperCase().trim();
  
  // Pattern 1: Short form - 1-5 alphanumeric chars (the elastic ID)
  // Examples: AB1, K7M, W8K01
  if (/^[0-9A-Z]{1,5}$/.test(normalized)) {
    return true;
  }
  
  // Pattern 2: With ward prefix - 2 letters + ID
  // Examples: CGAB1, NDAB01, DDW8K
  if (/^[A-Z]{2}[0-9A-Z]{1,5}$/.test(normalized)) {
    return true;
  }
  
  // Pattern 3: Full format with dot - XX.XXX or similar
  // Examples: CG.AB1, 29CG.0AB01
  if (/^(\d{2})?[A-Z]{2}\.[0-9A-Z]{1,5}$/.test(normalized)) {
    return true;
  }
  
  // Pattern 4: Full format - 29CGAB1 style
  if (/^29[A-Z]{2}[0-9A-Z]{1,5}$/.test(normalized)) {
    return true;
  }
  
  return false;
}

/**
 * Parse a GeoID input into components
 * Returns null if not a valid GeoID pattern
 */
export function parseGeoId(input: string): { 
  cityCode?: string; 
  wardCode?: string; 
  houseId: string; 
  roomId?: string;
  displayId: string;
} | null {
  const normalized = input.toUpperCase().trim();
  
  if (!isGeoIdPattern(normalized)) {
    return null;
  }
  
  // Try full format first: 29CG.0AB01 or 29CG0AB01
  let match = normalized.match(/^(\d{2})([A-Z]{2})\.?([0-9A-Z]{3})([0-9A-Z]{2})$/);
  if (match) {
    const [, city, ward, house, room] = match;
    return {
      cityCode: city,
      wardCode: ward,
      houseId: house,
      roomId: room,
      displayId: formatGeoIdDisplay(`${city}${ward}.${house}${room}`)
    };
  }
  
  // Try ward + ID format: CGAB1 or CG.AB1
  match = normalized.match(/^([A-Z]{2})\.?([0-9A-Z]{1,5})$/);
  if (match) {
    const [, ward, id] = match;
    return {
      wardCode: ward,
      houseId: id.padStart(3, '0').slice(0, 3),
      roomId: id.length > 3 ? id.slice(3).padStart(2, '0') : '00',
      displayId: `${ward}${id}`
    };
  }
  
  // Bare ID format: AB1, K7M
  return {
    houseId: normalized.padStart(3, '0').slice(0, 3),
    roomId: normalized.length > 3 ? normalized.slice(3).padStart(2, '0') : '00',
    displayId: normalized
  };
}

/**
 * Check if a string is a valid UUID
 */
export function isUuid(input: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(input);
}

/**
 * Get the short display ID for a listing
 * Uses geo_id if available, otherwise generates from UUID
 */
export function getListingDisplayId(listing: { 
  id: string; 
  geo_id?: string; 
  display_id?: string;
  address_ward?: string;
}): string {
  // If we have a pre-computed display_id, use it
  if (listing.display_id) {
    return listing.display_id;
  }
  
  // If we have a full geo_id, format it
  if (listing.geo_id) {
    return formatGeoIdDisplay(listing.geo_id);
  }
  
  // Generate from UUID (temporary bridge)
  return generateDisplayIdFromUuid(listing.id);
}
