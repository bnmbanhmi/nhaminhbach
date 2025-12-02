// src/components/listings/ListingCard.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Listing } from '../../types';
import { formatPrice } from '../../utils/formatters';
import { getListingDisplayId } from '../../utils/geoid';

interface ListingCardProps {
  listing: Listing;
}

const ListingCard: React.FC<ListingCardProps> = ({ listing }) => {
  const [copied, setCopied] = useState(false);
  const displayId = getListingDisplayId(listing);
  
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

  // Copy GeoID to clipboard
  const handleCopyId = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    navigator.clipboard.writeText(displayId).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <Link 
      to={`/listings/${listing.id}`} 
      className="group block w-full bg-surface rounded-card shadow-md overflow-hidden text-text-primary hover:shadow-lg hover:-translate-y-1 transition-transform duration-300 relative no-underline min-h-[340px] sm:min-h-[360px]"
      style={{ touchAction: 'manipulation' }}
    >
      {/* GeoID Badge - Top Right */}
      <div className="absolute top-2 right-2 z-10">
        <button
          onClick={handleCopyId}
          className={`
            px-3 py-1.5 rounded-full font-mono font-bold text-sm
            backdrop-blur-sm transition-all duration-200
            ${copied 
              ? 'bg-green-500 text-white' 
              : 'bg-black/70 text-white hover:bg-primary'
            }
          `}
          title={copied ? 'Đã copy!' : `Copy mã: ${displayId}`}
        >
          {copied ? '✓ Copied!' : `#${displayId}`}
        </button>
      </div>
      
      {/* Image Section */}
      {listing.image_urls && listing.image_urls.length > 0 ? (
        <img 
          src={listing.image_urls[0]} 
          alt={formatTitle()} 
          className="w-full h-40 sm:h-48 object-cover transition-transform duration-300 group-hover:scale-105" 
        />
      ) : (
        <div className="w-full h-40 sm:h-48 bg-gray-200 flex items-center justify-center">
          <div className="text-center text-text-secondary">
            <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Zm.375 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
            </svg>
            <span className="text-sm sm:text-base">Chưa có ảnh</span>
          </div>
        </div>
      )}
      
      {/* Content Section */}
      <div className="p-3 sm:p-4 flex flex-col gap-2">
        {/* Title */}
        <h3 className="font-semibold line-clamp-2 text-text-primary text-left text-base sm:text-lg" title={formatTitle()}>
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