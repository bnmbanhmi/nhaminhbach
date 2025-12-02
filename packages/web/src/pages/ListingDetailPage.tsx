// src/pages/ListingDetailPage.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import type { Listing } from '../types';
import { API_BASE_URL } from '../config';
import { formatPrice, formatArea } from '../utils/formatters';
import translateEnumValue from '../utils/translations';
import { getListingDisplayId } from '../utils/geoid';

const ListingDetailPage: React.FC = () => {
  const { listingId } = useParams<{ listingId: string }>();
  const [listing, setListing] = useState<Listing | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const displayId = listing ? getListingDisplayId(listing) : '';

  const handleCopyId = () => {
    if (!displayId) return;
    navigator.clipboard.writeText(displayId).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleCopyUrl = () => {
    const url = `${window.location.origin}/${displayId}`;
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  useEffect(() => {
    if (!listingId) {
      setIsLoading(false);
      setError('No listing ID provided.');
      return;
    }

    const fetchListing = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/get_listing_by_id?id=${listingId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch listing: ${response.statusText}`);
        }
        const data = await response.json();
        setListing(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchListing();
  }, [listingId]);

  if (isLoading) {
    return <div className="text-center p-8">Loading...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">Error: {error}</div>;
  }

  if (!listing) {
    return <div className="text-center p-8">Không tìm thấy tin đăng.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        {/* GeoID Header Badge */}
        <div className="bg-gray-900 text-white px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-gray-400 text-sm">Mã phòng:</span>
            <span className="font-mono font-bold text-2xl text-primary">#{displayId}</span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleCopyId}
              className={`
                px-4 py-2 rounded-full text-sm font-medium transition-all
                ${copied ? 'bg-green-500 text-white' : 'bg-white/10 hover:bg-white/20 text-white'}
              `}
            >
              {copied ? '✓ Đã copy!' : 'Copy mã'}
            </button>
            <button
              onClick={handleCopyUrl}
              className="px-4 py-2 rounded-full text-sm font-medium bg-primary hover:bg-primary-dark text-white transition-colors"
            >
              Chia sẻ link
            </button>
          </div>
        </div>
        
        {listing.image_urls && listing.image_urls.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {listing.image_urls.slice(0, 4).map((url, index) => (
              <img key={index} src={url} alt={`${listing.title} - image ${index + 1}`} className="w-full h-64 object-cover" />
            ))}
          </div>
        )}
        <div className="p-6">
          <h1 className="text-3xl font-bold mb-2">{listing.title}</h1>
          <p className="text-lg text-gray-600 mb-4">{[listing.address_ward, listing.address_district].filter(Boolean).join(', ')}</p>
          
          <div className="flex items-center justify-between mb-4">
            <span className="text-2xl font-semibold text-green-600">{formatPrice(listing.price_monthly_vnd)}</span>
            <span className="text-xl text-gray-800">{formatArea(listing.area_m2)}</span>
          </div>

          <p className="text-gray-700 whitespace-pre-wrap mb-6">{listing.description}</p>

          <h2 className="text-2xl font-semibold mb-4 border-b pb-2">Tiện ích</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {listing.attributes?.map(attr => (
              <div key={attr.slug} className="p-2">
                <span className="font-medium">{attr.name}: </span>
                <span>
                  {typeof attr.value === 'boolean'
                    ? (attr.value ? translateEnumValue(undefined, 'true') : translateEnumValue(undefined, 'false'))
                    : translateEnumValue(attr.slug, attr.value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListingDetailPage;
