import React from 'react';
import ListingForm from '../components/admin/ListingForm';

/**
 * QC Create Page - Internal tool for Quality Control team to create new listings
 * This page provides a form interface for manually adding verified rental listings
 * to the platform after quality control review.
 */
const QcCreatePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-sm rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-semibold text-gray-900">
              Create New Listing
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              Add a new verified rental listing to the platform
            </p>
          </div>
          <div className="px-6 py-6">
            <ListingForm />
          </div>
        </div>
      </div>
    </div>
  );
};

export default QcCreatePage;
