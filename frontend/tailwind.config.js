/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["'Space Grotesk'", "Inter", "sans-serif"],
      },
      colors: {
        brand: {
          DEFAULT: "#7c6cff",
          400: "#9a8cff",
          500: "#7c6cff",
          600: "#6450e6",
        },
      },
      keyframes: {
        drift1: {
          "0%,100%": { transform: "translate(0,0) scale(1)" },
          "50%": { transform: "translate(8%,12%) scale(1.15)" },
        },
        drift2: {
          "0%,100%": { transform: "translate(0,0) scale(1.1)" },
          "50%": { transform: "translate(-10%,-8%) scale(0.95)" },
        },
        drift3: {
          "0%,100%": { transform: "translate(0,0) scale(1)" },
          "50%": { transform: "translate(6%,-10%) scale(1.2)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "200% 0" },
          "100%": { backgroundPosition: "-200% 0" },
        },
      },
      animation: {
        drift1: "drift1 22s ease-in-out infinite",
        drift2: "drift2 26s ease-in-out infinite",
        drift3: "drift3 30s ease-in-out infinite",
        shimmer: "shimmer 6s linear infinite",
      },
    },
  },
  plugins: [],
};
