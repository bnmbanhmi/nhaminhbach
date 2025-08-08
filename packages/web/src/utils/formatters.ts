// src/utils/formatters.ts

export const formatPrice = (price: number | string) => {
    const numericPrice = Number(price);
    if (isNaN(numericPrice)) return 'N/A';
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(numericPrice);
};

export const formatArea = (area: number | string) => {
    const numericArea = Number(area);
    if (isNaN(numericArea)) return 'N/A';
    return `${Math.round(numericArea)} m²`;
  };