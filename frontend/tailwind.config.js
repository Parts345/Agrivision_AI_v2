/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Inter", "ui-sans-serif", "system-ui"],
        body: ["Inter", "ui-sans-serif", "system-ui"]
      },
      colors: {
        chlorophyll: "#65f6a7",
        cyber: "#46d9ff",
        aurora: "#b8ff5c",
        ink: "#06130f"
      },
      boxShadow: {
        glow: "0 0 34px rgba(101, 246, 167, 0.32)",
        panel: "0 24px 80px rgba(2, 12, 8, 0.28)"
      },
      backgroundImage: {
        "field-grid": "linear-gradient(rgba(101,246,167,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(70,217,255,.08) 1px, transparent 1px)"
      }
    }
  },
  plugins: []
};
