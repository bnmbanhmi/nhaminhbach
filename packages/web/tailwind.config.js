/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#F06D65',        // For main CTAs, links, highlights
        background: '#FDFBF7',     // Main page background
        surface: '#FFFFFF',        // Card and navbar backgrounds
        'text-primary': '#2C2C2C', // Main text color
        'text-secondary': '#757575',// Subdued text for descriptions, metadata
        'accent-cool': '#6C8B9A',   // For specific tags or success states
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'], // Set Inter as the default font
      },
      borderRadius: {
        'card': '0.75rem',         // For larger elements like ListingCard
        'button': '0.5rem',        // For smaller elements like buttons and tags
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
}
