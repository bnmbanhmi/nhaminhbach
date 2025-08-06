// src/components/listings/ListingCard.tsx
import React from 'react';
import type { Listing } from '../../types';

interface ListingCardProps {
  listing: Listing;
}

const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  // Helper function to format price to VND currency
  const formatPrice = (price: number | string) => {
    // Convert to number safely
    const numericPrice = Number(price);
    if (isNaN(numericPrice)) {
      return 'N/A'; // Return a fallback if conversion fails
    }
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(numericPrice);
  };

  // Helper function to format area
  const formatArea = (area: number | string) => {
    // Convert to number safely
    const numericArea = Number(area);
    if (isNaN(numericArea)) {
      return 'N/A'; // Return a fallback if conversion fails
    }
    return `${numericArea.toFixed(2)} m²`;
  };

  // Helper function to build a clean address string, ignoring null/empty parts
  const formatAddress = () => {
    return [listing.address_street, listing.address_ward, listing.address_district]
      .filter(part => part) // This removes any null, undefined, or empty strings
      .join(', ');
  };

  return (
    <div className="border rounded-lg shadow-md bg-white hover:shadow-lg transition-shadow duration-200 flex flex-col">
      <div className="relative">
        {listing.image_urls && listing.image_urls.length > 0 ? (
          <img 
            src={listing.image_urls[0]} 
            alt={listing.title} 
            className="w-full h-48 object-cover rounded-t-lg" 
          />
        ) : (
          <div className="w-full h-48 bg-gray-200 flex items-center justify-center rounded-t-lg">
            <span className="text-gray-500">No Image</span>
          </div>
        )}
      </div>
      
      <div className="p-4 flex-grow flex flex-col">
        <h2 className="text-lg font-bold mb-2 truncate" title={listing.title}>
          {listing.title}
        </h2>
        <p className="text-xl font-semibold text-green-600 mb-2">
          {formatPrice(listing.price_monthly_vnd)}
        </p>
        <p className="text-gray-700 mb-2">
          {formatArea(listing.area_m2)}
        </p>
        <p className="text-gray-600 text-sm truncate" title={formatAddress()}>
          {formatAddress()}
        </p>

        {/* Spacer to push tags to the bottom */}
        <div className="flex-grow"></div>

        {/* Render a few key amenities as tags */}
        <div className="mt-4 pt-2 border-t flex flex-wrap gap-2 text-xs">
          {listing.attributes?.slice(0, 4).map((attr) => (
            // Only show boolean attributes that are true
            attr.type === 'boolean' && attr.value === true && (
              <span key={attr.slug} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {attr.name}
              </span>
            )
          ))}
        </div>
      </div>
    </div>
  );
};

export default ListingCard;