import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../config';

// API Endpoints for Cloud Functions
const CREATE_LISTING_ENDPOINT = `${API_BASE_URL}/create_listing`;
const GET_ATTRIBUTES_ENDPOINT = `${API_BASE_URL}/get_all_attributes`;

/**
 * Defines the structure of a single attribute from the API.
 * This is the schema for our dynamic form fields.
 */
interface Attribute {
  id: number;
  name: string;
  slug: string;
  type: 'boolean' | 'string' | 'integer' | 'enum';
  possible_values: string[] | null;
}

/**
 * Basic form data structure for the static part of the listing.
 * Matches the core fields from our `listings` table schema.
 */
interface ListingFormData {
  title: string;
  description: string;
  price_monthly_vnd: number | '';
  area_m2: number | '';
  address_ward: string;
  address_district: string;
}

/**
 * API Response structure from the `create_listing` Cloud Function.
 */
interface CreateListingResponse {
  success: boolean;
  id?: string;
  message?: string;
}

/**
 * ListingForm Component - A comprehensive form for creating new rental listings.
 *
 * This component handles both the static listing details (like title, price)
 * and dynamically generated fields for listing attributes (like amenities).
 * It fetches the attribute schema on mount to build the form.
 */
const ListingForm: React.FC = () => {
  // State for the static part of the form
  const [formData, setFormData] = useState<ListingFormData>({
    title: '',
    description: '',
    price_monthly_vnd: '',
    area_m2: '',
    address_ward: '',
    address_district: '',
  });

  // State for the dynamic attribute values, keyed by attribute slug
  const [formValues, setFormValues] = useState<Record<string, any>>({});

  // State for the fetched attribute schema
  const [attributesSchema, setAttributesSchema] = useState<Attribute[]>([]);
  const [isAttributesLoading, setIsAttributesLoading] = useState<boolean>(true);
  const [attributesError, setAttributesError] = useState<string | null>(null);

  // State for the submission process
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Fetch attributes schema when the component mounts
  useEffect(() => {
    const fetchAttributes = async () => {
      try {
        const response = await fetch(GET_ATTRIBUTES_ENDPOINT);
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Failed to fetch attributes: ${response.status} ${errorText}`);
        }
        const data: Attribute[] = await response.json();
        setAttributesSchema(data);
      } catch (error) {
        const msg = error instanceof Error ? error.message : 'An unknown error occurred.';
        setAttributesError(msg);
        console.error(msg);
      } finally {
        setIsAttributesLoading(false);
      }
    };

    fetchAttributes();
  }, []);

  // Generic handler for static form fields
  const handleStaticFieldChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Generic handler for dynamic attribute fields
  const handleAttributeChange = (slug: string, type: Attribute['type']) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const target = e.target as HTMLInputElement; // Cast to access 'checked' property
    const value = type === 'boolean' ? target.checked : target.value;
    setFormValues(prev => ({ ...prev, [slug]: value }));
  };

  // Submission Handler
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitError(null);

    // Client-side validation for core fields
    const priceValue = formData.price_monthly_vnd === '' ? 0 : Number(formData.price_monthly_vnd);
    const areaValue = formData.area_m2 === '' ? 0 : Number(formData.area_m2);

    if (priceValue <= 0 || areaValue <= 0) {
      alert('Price and Area must be greater than 0.');
      return;
    }

    setIsSubmitting(true);

    try {
      // Construct the attributes payload from formValues
      const attributesPayload = Object.entries(formValues)
        .map(([slug, value]) => {
          const attribute = attributesSchema.find(attr => attr.slug === slug);
          if (!attribute || value === '' || value === false || value === null) {
            return null; // Skip empty, false, or null values
          }

          let processedValue: any = value;
          if (attribute.type === 'integer') {
            processedValue = parseInt(value, 10);
            if (isNaN(processedValue)) return null;
          } else if (attribute.type === 'boolean') {
            processedValue = Boolean(value);
          }

          return {
            attribute_id: attribute.id,
            value: processedValue,
          };
        })
        .filter(Boolean); // Remove null entries

      // Prepare the final payload for the API
      const payload = {
        listing: {
          ...formData,
          price_monthly_vnd: priceValue,
          area_m2: areaValue,
        },
        attributes: attributesPayload,
      };

      const response = await fetch(CREATE_LISTING_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const responseData: CreateListingResponse = await response.json();
        console.log('Success! Listing created:', responseData);
        alert(`Listing created successfully with ID: ${responseData.id}`);
        // Reset form state
        setFormData({
          title: '', description: '', price_monthly_vnd: '', area_m2: '',
          address_ward: '', address_district: '',
        });
        setFormValues({});
      } else {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }
    } catch (error) {
      const msg = error instanceof Error ? error.message : 'An unknown network error occurred.';
      console.error('Submission failed:', msg);
      setSubmitError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Helper function to render the correct input based on attribute type
  const renderAttributeInput = (attribute: Attribute) => {
    const { id, slug, name, type, possible_values } = attribute;
    const commonClasses = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500";

    switch (type) {
      case 'boolean':
        return (
          <div className="flex items-center">
            <input
              id={`attr-${id}`}
              type="checkbox"
              checked={!!formValues[slug]}
              onChange={handleAttributeChange(slug, type)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor={`attr-${id}`} className="ml-2 block text-sm text-gray-900">
              {name}
            </label>
          </div>
        );
      case 'integer':
        return (
          <>
            <label htmlFor={`attr-${id}`} className="block text-sm font-medium text-gray-700 mb-2">{name}</label>
            <input
              id={`attr-${id}`}
              type="number"
              value={formValues[slug] || ''}
              onChange={handleAttributeChange(slug, type)}
              className={commonClasses}
              placeholder={`Enter ${name}`}
            />
          </>
        );
      case 'string':
        return (
          <>
            <label htmlFor={`attr-${id}`} className="block text-sm font-medium text-gray-700 mb-2">{name}</label>
            <input
              id={`attr-${id}`}
              type="text"
              value={formValues[slug] || ''}
              onChange={handleAttributeChange(slug, type)}
              className={commonClasses}
              placeholder={`Enter ${name}`}
            />
          </>
        );
      case 'enum':
        return (
          <>
            <label htmlFor={`attr-${id}`} className="block text-sm font-medium text-gray-700 mb-2">{name}</label>
            <select
              id={`attr-${id}`}
              value={formValues[slug] || ''}
              onChange={handleAttributeChange(slug, type)}
              className={commonClasses}
            >
              <option value="">-- Select {name} --</option>
              {possible_values?.map(val => (
                <option key={val} value={val}>{val}</option>
              ))}
            </select>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-lg shadow-md">
      {/* Submission Error Display */}
      {submitError && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-red-800">Error submitting form</h3>
          <p className="mt-2 text-sm text-red-700">{submitError}</p>
        </div>
      )}

      {/* --- Static Fields Section --- */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 border-b pb-2">Core Listing Details</h3>
        {/* Title Field */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">Title</label>
          <input
            type="text" id="title" name="title" value={formData.title}
            onChange={handleStaticFieldChange} required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Bright, spacious room for rent"
          />
        </div>

        {/* Description Field */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            id="description" name="description" value={formData.description}
            onChange={handleStaticFieldChange} required rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Detailed description of the property"
          />
        </div>

        {/* Price and Area Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="price_monthly_vnd" className="block text-sm font-medium text-gray-700 mb-2">Price (VND/month)</label>
            <input
              type="number" id="price_monthly_vnd" name="price_monthly_vnd" value={formData.price_monthly_vnd}
              onChange={handleStaticFieldChange} required min="1" step="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 3500000"
            />
          </div>
          <div>
            <label htmlFor="area_m2" className="block text-sm font-medium text-gray-700 mb-2">Area (m²)</label>
            <input
              type="number" id="area_m2" name="area_m2" value={formData.area_m2}
              onChange={handleStaticFieldChange} required min="1" step="0.1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 25.5"
            />
          </div>
        </div>

        {/* Address Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="address_ward" className="block text-sm font-medium text-gray-700 mb-2">Ward (Phường/Xã)</label>
            <input
              type="text" id="address_ward" name="address_ward" value={formData.address_ward}
              onChange={handleStaticFieldChange} required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Dịch Vọng Hậu"
            />
          </div>
          <div>
            <label htmlFor="address_district" className="block text-sm font-medium text-gray-700 mb-2">District (Quận/Huyện)</label>
            <input
              type="text" id="address_district" name="address_district" value={formData.address_district}
              onChange={handleStaticFieldChange} required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Cầu Giấy"
            />
          </div>
        </div>
      </div>

      {/* --- Dynamic Attributes Section --- */}
      <div className="space-y-4 pt-6 border-t">
        <h3 className="text-lg font-semibold text-gray-900">Property Attributes</h3>
        {isAttributesLoading && <p>Loading attributes...</p>}
        {attributesError && (
          <div className="text-red-600 bg-red-50 p-3 rounded-md">
            <p><strong>Error:</strong> Could not load property attributes.</p>
            <p className="text-sm">{attributesError}</p>
          </div>
        )}
        {!isAttributesLoading && !attributesError && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {attributesSchema.map(attr => (
              <div key={attr.id} className={attr.type === 'boolean' ? 'col-span-1 flex items-center' : 'col-span-1'}>
                {renderAttributeInput(attr)}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <button
          type="submit"
          disabled={isSubmitting || isAttributesLoading}
          className={`w-full py-3 px-4 rounded-md font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors ${
            isSubmitting || isAttributesLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isSubmitting ? 'Submitting...' : (isAttributesLoading ? 'Loading Form...' : 'Create Listing')}
        </button>
      </div>
    </form>
  );
};

export default ListingForm;