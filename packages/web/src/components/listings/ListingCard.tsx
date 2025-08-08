// src/components/listings/ListingCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Squares2X2Icon } from '@heroicons/react/24/outline';
import type { Listing } from '../../types';
import { formatPrice, formatArea } from '../../utils/formatters';

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
      className="group bg-surface rounded-card shadow-md overflow-hidden text-text-primary hover:shadow-lg transition-all duration-300"
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
            <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-sm">Chưa có ảnh</span>
          </div>
        </div>
      )}
      
      {/* Content Section */}
      <div className="p-4 flex flex-col gap-2">
        {/* Title */}
        <h3 className="font-semibold line-clamp-2" title={formatTitle()}>
          {formatTitle()}
        </h3>
        
        {/* Price */}
        <div>
          <span className="font-bold text-primary text-lg">
            {formatPrice(listing.price_monthly_vnd)}
          </span>
          <span className="text-sm font-normal text-text-secondary">/tháng</span>
        </div>
        
        {/* Area & Address */}
        <div className="flex items-center text-sm text-text-secondary mt-1">
          <Squares2X2Icon className="w-4 h-4 mr-1.5" />
          <span>{formatArea(listing.area_m2)}</span>
          <span className="mx-2">·</span>
          <span>{formatAddress()}</span>
        </div>
      </div>
    </Link>
  );
};

export default ListingCard;