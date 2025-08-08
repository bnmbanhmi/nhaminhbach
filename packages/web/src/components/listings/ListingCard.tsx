// src/components/listings/ListingCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import type { Listing } from '../../types';
import { formatPrice } from '../../utils/formatters';

interface ListingCardProps {
  listing: Listing;
}

const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  // Helper function to build a clean address string, ignoring null/empty parts
  const formatAddress = () => {
    return [listing.address_ward, listing.address_district]
      .filter(part => part) // This removes any null, undefined, or empty strings
      .join(', ');
  };

  // Create standardized title: "[Loại phòng] tại [Phường], [Quận]"
  const formatTitle = () => {
    return `Phòng trọ tại ${formatAddress()}`;
  };

  return (
    <Link 
      to={`/listings/${listing.id}`} 
      className="group block w-full bg-surface rounded-card shadow-md overflow-hidden text-text-primary hover:shadow-lg hover:-translate-y-1 transition-transform duration-300 relative no-underline"
    >
      {/* Image Section */}
      {listing.image_urls && listing.image_urls.length > 0 ? (
        <img 
          src={listing.image_urls[0]} 
          alt={formatTitle()} 
          className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105" 
        />
      ) : (
        <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
          <div className="text-center text-text-secondary">
            <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
            </svg>
            <span className="text-sm">Chưa có ảnh</span>
          </div>
        </div>
      )}
      
      {/* Content Section */}
      <div className="p-4 flex flex-col gap-2">
        {/* Title */}
        <h3 className="font-semibold line-clamp-2 text-text-primary text-left" title={formatTitle()}>
          {formatTitle()}
        </h3>
        
        {/* Price */}
        <div className="flex items-baseline">
          <span className="font-bold text-primary text-xl">
            {formatPrice(listing.price_monthly_vnd)}
          </span>
        </div>
      </div>
    </Link>
  );
};

export default ListingCard;