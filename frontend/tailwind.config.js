// animals/frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: { // Пример добавления кастомных цветов, если нужно
        'brand-green': '#84CC16', // Примерно как "Разместить"
        'brand-beige': '#F5F5DC', // Примерный фон для секции поиска
        'brand-gray': '#F3F4F6', // Светло-серый фон
      }
    },
  },
  plugins: [],
}