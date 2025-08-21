import { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../config';
import type { AdminListingsResponse, AdminListingFilters } from '../types';

const ADMIN_LISTINGS_ENDPOINT = `${API_BASE_URL}/get_admin_listings`;

/**
 * Custom hook for fetching and managing admin listings with filtering and pagination
 */
export const useAdminListings = () => {
  const [data, setData] = useState<AdminListingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<AdminListingFilters>({
    status: 'pending_review',
    limit: 20,
    offset: 0
  });

  const fetchListings = useCallback(async (customFilters?: AdminListingFilters) => {
    setIsLoading(true);
    setError(null);

    const params = new URLSearchParams();
    const activeFilters = customFilters || filters;

    // Add filters to query parameters
    if (activeFilters.status) {
      params.append('status', activeFilters.status);
    }
    if (activeFilters.district) {
      params.append('district', activeFilters.district);
    }
    if (activeFilters.limit) {
      params.append('limit', activeFilters.limit.toString());
    }
    if (activeFilters.offset) {
      params.append('offset', activeFilters.offset.toString());
    }

    try {
      const response = await fetch(`${ADMIN_LISTINGS_ENDPOINT}?${params.toString()}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to fetch admin listings: ${response.status} ${errorText}`);
      }

      const responseData: AdminListingsResponse = await response.json();
      setData(responseData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
      setError(errorMessage);
      setData(null);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  // Update filters and trigger new fetch
  const updateFilters = useCallback((newFilters: Partial<AdminListingFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    fetchListings(updatedFilters);
  }, [filters, fetchListings]);

  // Load next page
  const loadNextPage = useCallback(() => {
    if (data?.pagination.has_more) {
      const currentOffset = filters.offset || 0;
      const currentLimit = filters.limit || 20;
      const nextOffset = currentOffset + currentLimit;
      updateFilters({ offset: nextOffset });
    }
  }, [data, filters, updateFilters]);

  // Reset to first page
  const resetPagination = useCallback(() => {
    updateFilters({ offset: 0 });
  }, [updateFilters]);

  // Initial load
  useEffect(() => {
    fetchListings();
  }, []);

  return {
    data,
    isLoading,
    error,
    filters,
    updateFilters,
    loadNextPage,
    resetPagination,
    refresh: () => fetchListings()
  };
};
