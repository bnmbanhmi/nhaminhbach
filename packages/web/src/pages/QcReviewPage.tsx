import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import type { Listing } from '../types';

const QcReviewPage: React.FC = () => {
  const { listingId } = useParams<{ listingId: string }>();
  const navigate = useNavigate();
  const [listing, setListing] = useState<Listing | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!listingId) {
      setError('No listing ID provided');
      setIsLoading(false);
      return;
    }

    fetchListingDetails();
  }, [listingId]);

  const fetchListingDetails = async () => {
    try {
      setIsLoading(true);
      // Since get_listing_by_id is not deployed, we'll use get_admin_listings 
      // and filter by the specific ID
      const response = await fetch(
        `${API_BASE_URL}/get_admin_listings?status=pending_review&limit=50`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch listing: ${response.status}`);
      }

      const data = await response.json();
      const targetListing = data.listings.find((l: Listing) => l.id === listingId);
      
      if (!targetListing) {
        throw new Error('Listing not found');
      }

      setListing(targetListing);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch listing');
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN').format(price) + ' VNĐ';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading listing details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️ Error</div>
          <p className="text-gray-700 mb-4">{error}</p>
          <button
            onClick={() => navigate('/internal/qc/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-700 mb-4">Listing not found</p>
          <button
            onClick={() => navigate('/internal/qc/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/internal/qc/dashboard')}
                className="text-gray-500 hover:text-gray-700 mr-4"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-xl font-semibold text-gray-900">
                QC Review: Side-by-Side Comparison
              </h1>
            </div>
            <div className="flex space-x-3">
              <button className="px-4 py-2 border border-red-300 text-red-700 rounded-md hover:bg-red-50">
                Reject
              </button>
              <button className="px-4 py-2 border border-yellow-300 text-yellow-700 rounded-md hover:bg-yellow-50">
                Edit
              </button>
              <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
                Approve
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Listing Info Bar */}
        <div className="bg-white rounded-lg border p-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-medium text-gray-900">Listing ID: {listing.id}</h2>
              <p className="text-sm text-gray-500">
                Created: {formatDate(listing.created_at)} | Updated: {formatDate(listing.updated_at)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Source URL:</p>
              <a 
                href={listing.source_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 text-sm truncate max-w-xs inline-block"
              >
                {listing.source_url}
              </a>
            </div>
          </div>
        </div>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Side: Raw Text */}
          <div className="bg-white rounded-lg border">
            <div className="px-6 py-4 bg-red-50 border-b">
              <h3 className="text-lg font-medium text-red-800">🔍 Raw Scraped Text</h3>
              <p className="text-sm text-red-600">Original data from source</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Raw Description:
                  </label>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
                      {listing.description}
                    </pre>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source URL:
                  </label>
                  <div className="bg-gray-50 p-3 rounded-md">
                    <code className="text-sm text-blue-600 break-all">
                      {listing.source_url}
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side: Structured Data */}
          <div className="bg-white rounded-lg border">
            <div className="px-6 py-4 bg-green-50 border-b">
              <h3 className="text-lg font-medium text-green-800">✨ AI-Structured Data</h3>
              <p className="text-sm text-green-600">Processed and normalized information</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title:
                  </label>
                  <div className="bg-green-50 p-3 rounded-md">
                    <p className="text-sm font-medium text-gray-900">
                      {listing.title || 'No title extracted'}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price:
                  </label>
                  <div className="bg-green-50 p-3 rounded-md">
                    <p className="text-sm font-medium text-gray-900">
                      {listing.price_monthly_vnd ? formatPrice(listing.price_monthly_vnd) : 'No price extracted'}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Area:
                  </label>
                  <div className="bg-green-50 p-3 rounded-md">
                    <p className="text-sm font-medium text-gray-900">
                      {listing.area_m2 ? `${listing.area_m2} m²` : 'No area extracted'}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Address:
                  </label>
                  <div className="bg-green-50 p-3 rounded-md space-y-1">
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">Street:</span> {listing.address_street || 'Not extracted'}
                    </p>
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">Ward:</span> {listing.address_ward || 'Not extracted'}
                    </p>
                    <p className="text-sm text-gray-900">
                      <span className="font-medium">District:</span> {listing.address_district || 'Not extracted'}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact:
                  </label>
                  <div className="bg-green-50 p-3 rounded-md">
                    <p className="text-sm font-medium text-gray-900">
                      {listing.contact_phone || 'No contact extracted'}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Images:
                  </label>
                  <div className="bg-green-50 p-3 rounded-md">
                    {listing.image_urls && listing.image_urls.length > 0 ? (
                      <div className="grid grid-cols-2 gap-2">
                        {listing.image_urls.slice(0, 4).map((url, index) => (
                          <img
                            key={index}
                            src={url}
                            alt={`Listing image ${index + 1}`}
                            className="w-full h-20 object-cover rounded border"
                            onError={(e) => {
                              e.currentTarget.src = 'https://via.placeholder.com/100x80?text=No+Image';
                            }}
                          />
                        ))}
                        {listing.image_urls.length > 4 && (
                          <div className="w-full h-20 bg-gray-200 rounded border flex items-center justify-center">
                            <span className="text-sm text-gray-500">
                              +{listing.image_urls.length - 4} more
                            </span>
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">No images extracted</p>
                    )}
                  </div>
                </div>

                {listing.attributes && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Attributes:
                    </label>
                    <div className="bg-green-50 p-3 rounded-md">
                      <div className="flex flex-wrap gap-2">
                        {Array.isArray(listing.attributes) && listing.attributes.map((attr: any, index: number) => (
                          <span 
                            key={index} 
                            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                          >
                            {attr.name}: {attr.value}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons (Bottom) */}
        <div className="mt-8 flex justify-center space-x-4">
          <button className="px-8 py-3 border border-red-300 text-red-700 rounded-md hover:bg-red-50 font-medium">
            Reject Listing
          </button>
          <button className="px-8 py-3 border border-yellow-300 text-yellow-700 rounded-md hover:bg-yellow-50 font-medium">
            Edit & Approve
          </button>
          <button className="px-8 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium">
            Approve as-is
          </button>
        </div>
      </div>
    </div>
  );
};

export default QcReviewPage;
