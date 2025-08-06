import React, { useState } from 'react';

// API Endpoint for Cloud Function (local development with Firebase Emulators)
const CREATE_LISTING_ENDPOINT = 'https://5001-firebase-nhaminhbach-1754197535766.cluster-ikxjzjhlifcwuroomfkjrx437g.cloudworkstations.dev/omega-sorter-467514-q6/asia-southeast1/create_listing';

/**
 * Basic form data structure for listing creation
 * Matches the core fields from our listings table schema
 */
interface ListingFormData {
  title: string;
  description: string;
  price_monthly_vnd: number;
}

/**
 * API Response structure from create_listing Cloud Function
 */
interface CreateListingResponse {
  success: boolean;
  id?: string;
  message?: string;
}

/**
 * ListingForm Component - Form for creating new rental listings
 * 
 * This component provides a basic form interface for QC team members
 * to manually input new rental listing data. The form follows our
 * database schema for the listings table.
 */
const ListingForm: React.FC = () => {
  // State Management: Initialize price as number (0), others as empty strings
  const [formData, setFormData] = useState<ListingFormData>({
    title: '',
    description: '',
    price_monthly_vnd: 0,
  });

  // Loading state for submit button
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Error state for API error messages
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Event Handler for title input
  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      title: e.target.value,
    }));
  };

  // Event Handler for description textarea
  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      description: e.target.value,
    }));
  };

  // Event Handler for price input with proper number conversion
  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData(prev => ({
      ...prev,
      price_monthly_vnd: value === '' ? 0 : Number(value),
    }));
  };

  // Submission Handler
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Prevent default browser form submission
    
    // Clear any previous error messages
    setErrorMessage(null);
    setIsLoading(true);
    
    try {
      // Prepare the payload to match Cloud Function expected structure
      const payload = {
        listing: {
          title: formData.title,
          description: formData.description,
          price_monthly_vnd: formData.price_monthly_vnd,
        },
        attributes: [
          // Hardcoded attributes for testing (will make dynamic later)
          { attribute_id: 1, value: true },
          { attribute_id: 2, value: true }
        ]
      };

      // Send POST request to Cloud Function
      const response = await fetch(CREATE_LISTING_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      // Check if the response is successful
      if (response.ok) {
        const responseData: CreateListingResponse = await response.json();
        console.log('Success! Listing created:', responseData);
        
        if (responseData.id) {
          console.log('New listing ID:', responseData.id);
        }
        
        // Reset form on successful submission
        setFormData({
          title: '',
          description: '',
          price_monthly_vnd: 0,
        });
      } else {
        // Handle API errors
        const errorText = await response.text();
        const errorMsg = `Error ${response.status}: ${errorText}`;
        console.error('API Error:', errorMsg);
        setErrorMessage(errorMsg);
      }
    } catch (error) {
      // Handle network errors or other exceptions
      const errorMsg = error instanceof Error ? error.message : 'Network error occurred';
      console.error('Request failed:', errorMsg);
      setErrorMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error Message Display */}
      {errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error submitting form
              </h3>
              <div className="mt-2 text-sm text-red-700">
                {errorMessage}
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Title Field */}
      <div>
        <label 
          htmlFor="title" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Title
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleTitleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter listing title"
        />
      </div>

      {/* Description Field */}
      <div>
        <label 
          htmlFor="description" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleDescriptionChange}
          required
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter detailed listing description"
        />
      </div>

      {/* Price Field */}
      <div>
        <label 
          htmlFor="price_monthly_vnd" 
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Price (VND/month)
        </label>
        <input
          type="number"
          id="price_monthly_vnd"
          name="price_monthly_vnd"
          value={formData.price_monthly_vnd}
          onChange={handlePriceChange}
          required
          min="0"
          step="1000"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter monthly rent price"
        />
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isLoading ? 'Submitting...' : 'Submit'}
        </button>
      </div>
    </form>
  );
};

export default ListingForm;
