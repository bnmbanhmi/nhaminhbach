/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Bảo Tailwind cách sử dụng các biến CSS của chúng ta
      colors: {
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        background: 'rgb(var(--color-background) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        'text-primary': 'rgb(var(--color-text-primary) / <alpha-value>)',
        'text-secondary': 'rgb(var(--color-text-secondary) / <alpha-value>)',
        'accent-cool': 'rgb(var(--color-accent-cool) / <alpha-value>)',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
      },
      borderRadius: {
        'button': 'var(--radius-button)',
        'card': 'var(--radius-card)',
      }
    },
  },
  plugins: [
    require('@tailwindcss/line-clamp'),
  ],
}