// src/components/listings/ListingCard.tsx
import React from 'react';
import type { Listing } from '../../types';

interface ListingCardProps {
  listing: Listing;
}

const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
    }).format(price);
  };

  return (
    <div className="border rounded-lg shadow-md p-4 bg-white hover:shadow-lg transition-shadow duration-200">
      {listing.image_urls && listing.image_urls.length > 0 && (
        <img 
          src={listing.image_urls[0]} 
          alt={listing.title} 
          className="w-full h-48 object-cover rounded-t-lg mb-4" 
        />
      )}
      <h2 className="text-xl font-bold mb-2 truncate">{listing.title}</h2>
      <p className="text-lg font-semibold text-green-600 mb-2">{formatPrice(listing.price_monthly_vnd)}</p>
      <p className="text-gray-700 mb-1">{listing.area_m2} m²</p>
      <p className="text-gray-600 truncate">{`${listing.address_street}, ${listing.address_ward}, ${listing.address_district}`}</p>
    </div>
  );
};

export default ListingCard;
