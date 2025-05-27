// animals/frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./frontend/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brand-green': '#84CC16',
        'brand-beige': '#F5F5DC',
        'brand-gray': '#F3F4F6',
      }
    },
  },
  plugins: [],
}
