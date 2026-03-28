/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        surface: {
          1: "var(--surface-1)",
          2: "var(--surface-2)",
          3: "var(--surface-3)",
        },
        accent: {
          1: "var(--accent-1)",
          2: "var(--accent-2)",
          3: "var(--accent-3)",
        },
        brand: {
          purple: "#7c3aed",
          blue: "#3b82f6",
          indigo: "#6366f1",
          violet: "#8b5cf6",
          fuchsia: "#a855f7",
        },
      },
      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },
      boxShadow: {
        "glow-sm": "0 0 10px -2px var(--accent-1)",
        "glow": "0 0 20px -3px var(--accent-1)",
        "glow-lg": "0 0 40px -5px var(--accent-1)",
        "glow-purple": "0 0 20px -3px rgba(124, 58, 237, 0.4)",
        "glow-blue": "0 0 20px -3px rgba(59, 130, 246, 0.4)",
        "glow-green": "0 0 20px -3px rgba(34, 197, 94, 0.35)",
        "glow-red": "0 0 20px -3px rgba(239, 68, 68, 0.35)",
        "card": "0 8px 32px -4px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05)",
        "card-hover": "0 16px 48px -8px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.08), 0 0 30px -5px rgba(124, 58, 237, 0.15)",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
        "mesh-1": "radial-gradient(at 0% 0%, rgba(124, 58, 237, 0.15) 0px, transparent 50%), radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.12) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%)",
        "mesh-2": "radial-gradient(at 20% 80%, rgba(124, 58, 237, 0.12) 0px, transparent 50%), radial-gradient(at 80% 20%, rgba(59, 130, 246, 0.1) 0px, transparent 50%)",
        "gradient-brand": "linear-gradient(135deg, #7c3aed, #3b82f6)",
        "gradient-brand-hover": "linear-gradient(135deg, #8b5cf6, #60a5fa)",
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "shimmer": "shimmer 2.5s linear infinite",
        "gradient-x": "gradient-x 6s ease infinite",
        "glow-pulse": "glow-pulse 3s ease-in-out infinite",
        "slide-up": "slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1)",
        "fade-in": "fade-in 0.4s ease-out",
        "spin-slow": "spin 8s linear infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "gradient-x": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        "glow-pulse": {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        "slide-up": {
          "0%": { transform: "translateY(16px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
}
