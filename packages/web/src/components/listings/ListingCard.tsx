// src/components/listings/ListingCard.tsx
import React from 'react';
import { Link } from 'react-router-dom';
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

  // Get the first 2-3 boolean attributes that are true
  const getBooleanAttributes = () => {
    return listing.attributes
      ?.filter(attr => attr.value === true)
      .slice(0, 3) || [];
  };

  return (
    <Link 
      to={`/listings/${listing.id}`} 
      className="group block bg-white rounded-xl shadow-md border border-gray-100 overflow-hidden hover:shadow-xl hover:scale-[1.02] transition-all duration-300 ease-out"
    >
      {/* Image Section */}
      <div className="relative h-48 overflow-hidden">
        {listing.image_urls && listing.image_urls.length > 0 ? (
          <img 
            src={listing.image_urls[0]} 
            alt={listing.title} 
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="text-sm">Chưa có ảnh</span>
            </div>
          </div>
        )}
      </div>
      
      {/* Content Section */}
      <div className="p-5">
        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 mb-3 line-clamp-2 leading-tight" title={listing.title}>
          {listing.title}
        </h3>
        
        {/* Key Details - Price and Area */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center text-green-600">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            <span className="text-xl font-bold">
              {formatPrice(listing.price_monthly_vnd)}
            </span>
          </div>
          
          <div className="flex items-center text-gray-600">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V6a2 2 0 012-2h2M4 8v8a2 2 0 002 2h2m0-16v16m8-16h2a2 2 0 012 2v2m-4-4v16m0-16h-2m2 0v4m0 0v8a2 2 0 01-2 2h-2" />
            </svg>
            <span className="font-medium">
              {formatArea(listing.area_m2)}
            </span>
          </div>
        </div>
        
        {/* Address */}
        <div className="flex items-start mb-4">
          <svg className="w-4 h-4 text-gray-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p className="text-gray-600 text-sm leading-relaxed" title={formatAddress()}>
            {formatAddress()}
          </p>
        </div>
        
        {/* Attributes/Amenities Tags */}
        {getBooleanAttributes().length > 0 && (
          <div className="flex flex-wrap gap-2">
            {getBooleanAttributes().map((attr) => (
              <span 
                key={attr.slug} 
                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200"
              >
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {attr.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
};

export default ListingCard;