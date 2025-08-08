// src/components/listings/ListingCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import type { Listing } from '../../types';
import { formatArea } from '../../utils/formatters';

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

  // Format price to remove currency symbol and add /tháng
  const formatPriceWithSuffix = (price: number | string) => {
    const numericPrice = Number(price);
    if (isNaN(numericPrice)) return 'N/A';
    
    // Format price in Vietnamese style without currency symbol
    const formattedPrice = new Intl.NumberFormat('vi-VN').format(numericPrice);
    return formattedPrice;
  };

  return (
    <Link 
      to={`/listings/${listing.id}`} 
      className="block bg-surface rounded-card shadow-md overflow-hidden hover:shadow-lg hover:transform hover:-translate-y-1 transition-all duration-300"
    >
      {/* Image Section */}
      <div className="relative aspect-[4/3] overflow-hidden">
        {listing.image_urls && listing.image_urls.length > 0 ? (
          <img 
            src={listing.image_urls[0]} 
            alt={formatTitle()} 
            className="w-full h-full object-cover rounded-t-card" 
          />
        ) : (
          <div className="w-full h-full bg-gray-200 flex items-center justify-center rounded-t-card">
            <div className="text-center text-text-secondary">
              <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm">Chưa có ảnh</span>
            </div>
          </div>
        )}
      </div>
      
      {/* Content Section */}
      <div className="p-4 flex flex-col">
        {/* Time */}
        <div className="text-xs text-text-secondary mb-2">
          Vừa đăng
        </div>
        
        {/* Title */}
        <h3 className="font-semibold text-text-primary line-clamp-2 mb-3" title={formatTitle()}>
          {formatTitle()}
        </h3>
        
        {/* Price */}
        <div className="mb-3">
          <span className="text-xl font-bold text-primary">
            {formatPriceWithSuffix(listing.price_monthly_vnd)} đ
          </span>
          <span className="text-sm font-normal text-text-secondary">/tháng</span>
        </div>
        
        {/* Address & Key Stats */}
        <div className="flex items-center text-text-secondary">
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V6a2 2 0 012-2h2M4 8v8a2 2 0 002 2h2m0-16v16m8-16h2a2 2 0 012 2v2m-4-4v16m0-16h-2m2 0v4m0 0v8a2 2 0 01-2 2h-2" />
            </svg>
            <span className="text-sm">
              {formatArea(listing.area_m2)}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ListingCard;