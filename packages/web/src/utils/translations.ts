// Shared translation utilities for enum/attribute values
export const enumTranslations: Record<string, Record<string, string>> = {
  status: {
    available: 'Còn trống',
    rented: 'Đã thuê',
    pending_review: 'Chờ duyệt',
    rejected: 'Bị từ chối',
  },
};

export const genericValueTranslations: Record<string, string> = {
  yes: 'Có',
  no: 'Không',
  true: 'Có',
  false: 'Không',
  // User-provided mappings
  female_only: 'Chỉ nữ',
  male_only: 'Chỉ nam',
  any: 'Nam nữ',
  free: 'Tự do',
  restricted: 'Có giới hạn',
  private: 'Riêng',
  shared: 'Chung',
};

export const translateEnumValue = (slug: string | undefined, value: any) => {
  const key = String(value);
  if (slug && enumTranslations[slug] && enumTranslations[slug][key]) return enumTranslations[slug][key];
  if (genericValueTranslations[key]) return genericValueTranslations[key];
  return String(key).replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

export default translateEnumValue;
