import { useState } from 'react';
import { API_BASE_URL } from '../config';
import type { Listing } from '../types';

/**
 * Custom hook for managing QC review actions (approve, reject, update)
 */
export const useQcActions = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const approveListingAsIs = async (listingId: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/update_listing_status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          listing_id: listingId,
          status: 'available'
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to approve listing: ${response.status} ${errorText}`);
      }

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to approve listing';
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const rejectListing = async (listingId: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/update_listing_status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          listing_id: listingId,
          status: 'rejected'
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to reject listing: ${response.status} ${errorText}`);
      }

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reject listing';
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const updateAndApproveListing = async (
    listingId: string, 
    updatedData: Partial<Listing>
  ): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/update_listing_data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          listing_id: listingId,
          listing: updatedData,
          // TODO: Add attributes support if needed
          attributes: []
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to update listing: ${response.status} ${errorText}`);
      }

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update listing';
      setError(errorMessage);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    approveListingAsIs,
    rejectListing,
    updateAndApproveListing,
  };
};
