import React, { useState } from 'react';
import type { Listing } from '../../types';

interface EditableListingFormProps {
  listing: Listing;
  onSave: (updatedData: Partial<Listing>) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

/**
 * EditableListingForm Component - A form for editing existing rental listings
 * Pre-populated with current listing data and allows modification before approval
 */
const EditableListingForm: React.FC<EditableListingFormProps> = ({
  listing,
  onSave,
  onCancel,
  isSubmitting = false
}) => {
  // Form state initialized with current listing data
  const [formData, setFormData] = useState({
    title: listing.title || '',
    description: listing.description || '',
    price_monthly_vnd: listing.price_monthly_vnd || '',
    area_m2: listing.area_m2 || '',
    address_street: listing.address_street || '',
    address_ward: listing.address_ward || '',
    address_district: listing.address_district || '',
    contact_phone: listing.contact_phone || '',
  });

  // Handle form field changes
  const handleFieldChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.title.trim() || !formData.description.trim()) {
      alert('Title and description are required');
      return;
    }

    const priceValue = formData.price_monthly_vnd === '' ? 0 : Number(formData.price_monthly_vnd);
    const areaValue = formData.area_m2 === '' ? 0 : Number(formData.area_m2);

    if (priceValue <= 0 || areaValue <= 0) {
      alert('Price and Area must be greater than 0');
      return;
    }

    // Prepare updated data
    const updatedData = {
      ...formData,
      price_monthly_vnd: priceValue,
      area_m2: areaValue,
    };

    onSave(updatedData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg border">
      <div className="flex justify-between items-center border-b pb-4">
        <h3 className="text-lg font-medium text-gray-900">Edit Listing Data</h3>
        <div className="text-sm text-gray-500">
          Make corrections before approval
        </div>
      </div>

      {/* Core Listing Fields */}
      <div className="space-y-4">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleFieldChange}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter listing title"
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleFieldChange}
            required
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter listing description"
          />
        </div>

        {/* Price and Area */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="price_monthly_vnd" className="block text-sm font-medium text-gray-700 mb-2">
              Price (VND/month) *
            </label>
            <input
              type="number"
              id="price_monthly_vnd"
              name="price_monthly_vnd"
              value={formData.price_monthly_vnd}
              onChange={handleFieldChange}
              required
              min="1"
              step="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., 3500000"
            />
          </div>
          <div>
            <label htmlFor="area_m2" className="block text-sm font-medium text-gray-700 mb-2">
              Area (m²) *
            </label>
            <input
              type="number"
              id="area_m2"
              name="area_m2"
              value={formData.area_m2}
              onChange={handleFieldChange}
              required
              min="1"
              step="0.1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., 25.5"
            />
          </div>
        </div>

        {/* Address Fields */}
        <div>
          <label htmlFor="address_street" className="block text-sm font-medium text-gray-700 mb-2">
            Street Address
          </label>
          <input
            type="text"
            id="address_street"
            name="address_street"
            value={formData.address_street}
            onChange={handleFieldChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., 123 Nguyen Trai"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="address_ward" className="block text-sm font-medium text-gray-700 mb-2">
              Ward (Phường/Xã) *
            </label>
            <input
              type="text"
              id="address_ward"
              name="address_ward"
              value={formData.address_ward}
              onChange={handleFieldChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Dịch Vọng Hậu"
            />
          </div>
          <div>
            <label htmlFor="address_district" className="block text-sm font-medium text-gray-700 mb-2">
              District (Quận/Huyện) *
            </label>
            <input
              type="text"
              id="address_district"
              name="address_district"
              value={formData.address_district}
              onChange={handleFieldChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Cầu Giấy"
            />
          </div>
        </div>

        {/* Contact Phone */}
        <div>
          <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700 mb-2">
            Contact Phone
          </label>
          <input
            type="text"
            id="contact_phone"
            name="contact_phone"
            value={formData.contact_phone}
            onChange={handleFieldChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., 0123456789"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className={`px-6 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            isSubmitting
              ? 'bg-gray-400 cursor-not-allowed text-white'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {isSubmitting ? 'Saving...' : 'Save & Approve'}
        </button>
      </div>
    </form>
  );
};

export default EditableListingForm;
