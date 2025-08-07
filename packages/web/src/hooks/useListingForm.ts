import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import type { Attribute, ListingFormData, CreateListingResponse } from '../types';

// API Endpoints
const CREATE_LISTING_ENDPOINT = `${API_BASE_URL}/create_listing`;
const GET_ATTRIBUTES_ENDPOINT = `${API_BASE_URL}/get_all_attributes`;

/**
 * Custom hook to manage the state and logic for the listing creation form.
 * It handles fetching attribute schemas, managing form data, and submitting
 * the new listing to the backend.
 */
export const useListingForm = () => {
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

  // Fetch attributes schema when the hook is used
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
    setFormData((prev: ListingFormData) => ({ ...prev, [name]: value }));
  };

  // Generic handler for dynamic attribute fields
  const handleAttributeChange = (slug: string, value: any) => {
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

  return {
    formData,
    formValues,
    attributesSchema,
    isAttributesLoading,
    attributesError,
    isSubmitting,
    submitError,
    handleStaticFieldChange,
    handleAttributeChange,
    handleSubmit,
  };
};
