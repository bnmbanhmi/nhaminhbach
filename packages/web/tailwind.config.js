const colors = require('tailwindcss/colors');

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    // Chúng ta định nghĩa các token trực tiếp ở đây,
    // Tailwind sẽ tự động hợp nhất chúng với các giá trị mặc định.
    colors: {
      // Thêm các màu tùy chỉnh của chúng ta
      primary: '#F06D65',
      background: '#FDFBF7',
      surface: '#FFFFFF',
      'text-primary': '#2C2C2C',
      'text-secondary': '#757575',
      'accent-cool': '#6C8B9A',
      
      // Giữ lại các màu mặc định của Tailwind nếu cần
      transparent: 'transparent',
      current: 'currentColor',
      black: '#000',
      white: '#fff',
      gray: colors.gray,
      // Thêm các màu khác nếu cần, ví dụ:
      // red: colors.red,
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
    },
    // Chúng ta sẽ mở rộng (extend) borderRadius để không mất đi các giá trị mặc định
    extend: {
      borderRadius: {
        'card': '0.75rem',  // Giá trị của chúng ta
        'button': '0.5rem', // Giá trị của chúng ta
      },
    },
  },
  plugins: [
    // Giữ lại plugin của bạn
    require('@tailwindcss/line-clamp'),
  ],
}