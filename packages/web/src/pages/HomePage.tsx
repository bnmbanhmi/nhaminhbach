// src/pages/HomePage.tsx
import React, { useState, useEffect } from 'react';
import type { Listing } from '../types';
import ListingCard from '../components/listings/ListingCard';
import { API_BASE_URL } from '../config'; // <-- THAY ĐỔI: Import từ file config

// Sử dụng biến đã import để xây dựng endpoint
const API_ENDPOINT = `${API_BASE_URL}/get_listings`;

const HomePage: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const response = await fetch(API_ENDPOINT);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setListings(data);
      } catch (e) {
        if (e instanceof Error) {
          setError(e);
        } else {
          setError(new Error('An unknown error occurred'));
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchListings();
  }, []);

  if (isLoading) {
    return <div className="text-center mt-10">Loading...</div>;
  }

  if (error) {
    return <div className="text-center mt-10 text-red-500">Error: {error.message}</div>;
  }

  return (
    <div className="w-full px-1 md:px-2 lg:px-3">
      <h1 className="text-3xl font-bold mb-6">Available Listings</h1>
      <div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-4 md:gap-6 justify-items-center">
        {listings.map((listing) => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </div>
    </div>
  );
};

export default HomePage;