/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Orbitron", "sans-serif"],
        body: ["Rajdhani", "sans-serif"],
      },
      boxShadow: {
        neon: "0 0 30px rgba(0, 245, 255, 0.28)",
      },
      backgroundImage: {
        grid: "radial-gradient(circle at center, rgba(255,255,255,0.08) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
};
