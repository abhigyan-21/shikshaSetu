/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'opendyslexic': ['OpenDyslexic', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
