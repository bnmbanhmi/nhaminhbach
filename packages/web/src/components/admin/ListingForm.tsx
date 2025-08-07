import React, { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL } from '../../config'; // Đảm bảo bạn đã có file này

// --- API Endpoints ---
const CREATE_LISTING_ENDPOINT = `${API_BASE_URL}/create_listing`;
const GET_ATTRIBUTES_ENDPOINT = `${API_BASE_URL}/get_all_attributes`;

// --- Type Definitions ---
interface Attribute {
  id: number;
  name: string;
  slug: string;
  type: 'boolean' | 'string' | 'integer' | 'enum';
  possible_values: string[] | null;
}

interface ListingFormData {
  title: string;
  description: string;
  price_monthly_vnd: number | '';
  area_m2: number | '';
  address_ward: string;
  address_district: string;
}

interface CreateListingResponse {
  message: string;
  id?: string;
}

// =================================================================================
//  ListingForm Component
// =================================================================================
const ListingForm: React.FC = () => {
  // --- State Management ---
  const [formData, setFormData] = useState<ListingFormData>({
    title: '',
    description: '',
    price_monthly_vnd: '',
    area_m2: '',
    address_ward: '',
    address_district: '',
  });

  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [attributesSchema, setAttributesSchema] = useState<Attribute[]>([]);
  
  const [isAttributesLoading, setIsAttributesLoading] = useState<boolean>(true);
  const [attributesError, setAttributesError] = useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // --- Data Fetching ---
  useEffect(() => {
    const fetchAttributes = async () => {
      setIsAttributesLoading(true);
      setAttributesError(null);
      try {
        const response = await fetch(GET_ATTRIBUTES_ENDPOINT);
        if (!response.ok) {
          throw new Error(`Failed to fetch attributes: ${response.status}`);
        }
        const data: Attribute[] = await response.json();
        setAttributesSchema(data);
      } catch (error) {
        const msg = error instanceof Error ? error.message : 'An unknown error occurred.';
        setAttributesError(msg);
      } finally {
        setIsAttributesLoading(false);
      }
    };
    fetchAttributes();
  }, []); // Chạy 1 lần khi component mount

  // --- Event Handlers ---
  const handleStaticFieldChange = useCallback((e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  }, []);

  const handleAttributeChange = useCallback((slug: string, type: Attribute['type']) => {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const target = e.target as HTMLInputElement;
      const value = type === 'boolean' ? target.checked : target.value;
      setFormValues(prev => ({ ...prev, [slug]: value }));
    };
  }, []);

  // --- Submission Logic ---
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitError(null);
    setIsSubmitting(true);

    const priceValue = Number(formData.price_monthly_vnd);
    const areaValue = Number(formData.area_m2);

    if (priceValue <= 0 || areaValue <= 0) {
      alert('Price and Area must be greater than 0.');
      setIsSubmitting(false);
      return;
    }

    try {
      const attributesPayload = attributesSchema
        .map(attribute => {
          const value = formValues[attribute.slug];
          if (value === undefined || value === null || value === '' || value === false) {
            return null;
          }
          let processedValue: any = value;
          if (attribute.type === 'integer') processedValue = parseInt(String(value), 10);
          if (isNaN(Number(processedValue))) return null;

          return { attribute_id: attribute.id, value: processedValue };
        })
        .filter(Boolean);

      const payload = {
        listing: { ...formData, price_monthly_vnd: priceValue, area_m2: areaValue },
        attributes: attributesPayload,
      };

      const response = await fetch(CREATE_LISTING_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }
      
      const responseData: CreateListingResponse = await response.json();
      alert(`Listing created successfully with ID: ${responseData.id}`);
      
      // Reset form
      setFormData({
        title: '', description: '', price_monthly_vnd: '', area_m2: '',
        address_ward: '', address_district: '',
      });
      setFormValues({});

    } catch (error) {
      const msg = error instanceof Error ? error.message : 'An unknown submission error occurred.';
      setSubmitError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  // --- Dynamic Input Renderer ---
  const renderAttributeInput = (attribute: Attribute) => {
    const { id, slug, name, type, possible_values } = attribute;
    const commonClasses = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500";

    switch (type) {
      case 'boolean':
        return (
          <div className="flex items-center h-full">
            <input
              id={`attr-${id}`} type="checkbox"
              checked={!!formValues[slug]}
              onChange={handleAttributeChange(slug, type)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor={`attr-${id}`} className="ml-2 block text-sm font-medium text-gray-900">{name}</label>
          </div>
        );
      case 'integer':
      case 'string':
        return (
          <>
            <label htmlFor={`attr-${id}`} className="block text-sm font-medium text-gray-700 mb-1">{name}</label>
            <input
              id={`attr-${id}`} type={type === 'integer' ? 'number' : 'text'}
              value={formValues[slug] || ''}
              onChange={handleAttributeChange(slug, type)}
              className={commonClasses} placeholder={`Enter ${name}`}
            />
          </>
        );
      case 'enum':
        return (
          <>
            <label htmlFor={`attr-${id}`} className="block text-sm font-medium text-gray-700 mb-1">{name}</label>
            <select
              id={`attr-${id}`} value={formValues[slug] || ''}
              onChange={handleAttributeChange(slug, type)} className={commonClasses}
            >
              <option value="">-- Select {name} --</option>
              {possible_values?.map(val => <option key={val} value={val}>{val}</option>)}
            </select>
          </>
        );
      default: return null;
    }
  };

  // --- JSX ---
  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-lg shadow-md max-w-4xl mx-auto">
      {submitError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Submission Error: </strong>
          <span className="block sm:inline">{submitError}</span>
        </div>
      )}

      {/* Static Fields */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-gray-900 border-b pb-2">Core Listing Details</h3>
        {/* ... (Các trường Title, Description, Price, Area, Address giữ nguyên như code trước) ... */}
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
        {/* ... (Các trường khác tương tự) ... */}
      </div>

      {/* Dynamic Attributes */}
      <div className="space-y-4 pt-6 border-t">
        <h3 className="text-xl font-bold text-gray-900">Property Attributes</h3>
        {isAttributesLoading && <p>Loading attributes...</p>}
        {attributesError && <div className="text-red-600">Error: {attributesError}</div>}
        {!isAttributesLoading && !attributesError && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {attributesSchema.map(attr => (
              <div key={attr.id}>{renderAttributeInput(attr)}</div>
            ))}
          </div>
        )}
      </div>

      {/* Submit Button */}
      <div className="pt-4">
        <button type="submit" disabled={isSubmitting || isAttributesLoading}
          className="w-full py-3 px-4 rounded-md font-semibold text-white focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors
                     disabled:bg-gray-400 disabled:cursor-not-allowed
                     bg-blue-600 hover:bg-blue-700 focus:ring-blue-500">
          {isSubmitting ? 'Submitting...' : 'Create Listing'}
        </button>
      </div>
    </form>
  );
};

export default ListingForm;