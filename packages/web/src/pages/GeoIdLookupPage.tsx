// src/pages/GeoIdLookupPage.tsx
/**
 * GeoID Lookup Page
 * =================
 * Handles short URL routing like /AB1, /CGAB1, /29CGAB1
 * 
 * This is the magic page that enables "Instant Gratification":
 * User types AB1 → sees the listing immediately
 */
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Navigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import { isGeoIdPattern, generateDisplayIdFromUuid } from '../utils/geoid';
import type { Listing } from '../types';

const GeoIdLookupPage: React.FC = () => {
  const { geoId } = useParams<{ geoId: string }>();
  const navigate = useNavigate();
  const [listing, setListing] = useState<Listing | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allListings, setAllListings] = useState<Listing[]>([]);

  useEffect(() => {
    if (!geoId) {
      setError('Không có mã phòng');
      setIsLoading(false);
      return;
    }

    // Check if it's a valid GeoID pattern
    if (!isGeoIdPattern(geoId)) {
      setError('Mã phòng không hợp lệ');
      setIsLoading(false);
      return;
    }

    const lookupListing = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const normalizedInput = geoId.toUpperCase().trim();

        // 1) Try backend GeoID lookup endpoint
        const resp = await fetch(`${API_BASE_URL}/get_listing_by_geoid?geoid=${encodeURIComponent(normalizedInput)}`);
        if (resp.ok) {
          const listingObj = await resp.json();
          setListing(listingObj);
          setIsLoading(false);
          return;
        }

        // 2) If backend returned 404 or other problem, fall back to existing client-side method
        // Fetch all public listings
        const response = await fetch(`${API_BASE_URL}/get_listings`);

        let listings: Listing[] = [];
        if (response.status === 404) {
          // Fallback to admin endpoint
          const adminResp = await fetch(`${API_BASE_URL}/get_admin_listings?limit=100&offset=0`);
          if (!adminResp.ok) throw new Error('Không thể tải danh sách');
          const adminData = await adminResp.json();
          listings = Array.isArray(adminData) ? adminData : (adminData.listings || []);
        } else if (response.ok) {
          const data = await response.json();
          listings = Array.isArray(data) ? data : (data.listings || []);
        } else {
          throw new Error('Không thể tải danh sách');
        }

        setAllListings(listings);

        // Find listing by matching generated display ID
        const foundListing = listings.find((l: Listing) => {
          const displayId = generateDisplayIdFromUuid(l.id);
          return (
            displayId === normalizedInput ||
            `XX${displayId}` === normalizedInput ||
            normalizedInput.endsWith(displayId)
          );
        });

        if (foundListing) {
          setListing(foundListing);
        } else {
          setError(`Không tìm thấy phòng với mã ${geoId.toUpperCase()}`);
        }
      } catch (err) {
        console.error('Lookup error:', err);
        setError(err instanceof Error ? err.message : 'Đã xảy ra lỗi');
      } finally {
        setIsLoading(false);
      }
    };

    lookupListing();
  }, [geoId]);

  // If we found the listing, redirect to the detail page
  if (listing) {
    return <Navigate to={`/listings/${listing.id}`} replace />;
  }

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4"></div>
        <p className="text-lg text-gray-600">
          Đang tìm phòng <span className="font-mono font-bold text-primary">{geoId?.toUpperCase()}</span>...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center px-4">
        <div className="text-center max-w-md">
          {/* Error Icon */}
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
            <svg className="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          
          {/* Error Message */}
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Không tìm thấy phòng
          </h1>
          <p className="text-gray-600 mb-6">
            Mã <span className="font-mono font-semibold text-primary">{geoId?.toUpperCase()}</span> không tồn tại hoặc đã bị xóa.
          </p>
          
          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-primary text-white font-medium rounded-full hover:bg-primary-dark transition-colors"
            >
              Về trang chủ
            </button>
            <button
              onClick={() => navigate(-1)}
              className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-full hover:bg-gray-200 transition-colors"
            >
              Quay lại
            </button>
          </div>
          
          {/* Suggestions */}
          {allListings.length > 0 && (
            <div className="mt-8 pt-6 border-t">
              <p className="text-sm text-gray-500 mb-4">Có thể bạn muốn tìm:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {allListings.slice(0, 5).map((l) => {
                  const displayId = generateDisplayIdFromUuid(l.id);
                  return (
                    <button
                      key={l.id}
                      onClick={() => navigate(`/${displayId}`)}
                      className="px-3 py-1 bg-gray-100 hover:bg-primary hover:text-white rounded-full text-sm font-mono transition-colors"
                    >
                      {displayId}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return null;
};

export default GeoIdLookupPage;
