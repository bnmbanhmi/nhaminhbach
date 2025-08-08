/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#F06D65',
        background: '#FDFBF7',
        surface: '#FFFFFF',
        'text-primary': '#2C2C2C',
        'text-secondary': '#757575',
        'accent-cool': '#6C8B9A',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'card': '0.75rem',
        'button': '0.5rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
}