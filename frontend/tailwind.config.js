/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: "#0A1424",
          DEFAULT: "#0F1E36",
          800: "#162B4D",
          700: "#1F3B66",
        },
        ivory: {
          DEFAULT: "#FDFBF7",
          50: "#FFFFFF",
          100: "#FAF7F0",
          200: "#F4EFE6",
          300: "#EDE5D8",
        },
        slate: {
          DEFAULT: "#6B7C96",
          light: "#8FA0B8",
          muted: "#A2B1C6",
          dark: "#4B586E",
        },
        terracotta: {
          DEFAULT: "#D97450",
          hover: "#C4623F",
          light: "#F5DFD7",
          50: "#FAF1ED",
        },
        status: {
          critical: "#DC2626",
          high: "#EA580C",
          medium: "#D97706",
          low: "#16A34A",
          fulfilled: "#059669",
          transit: "#0284C7",
          pending: "#64748B"
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 10px rgba(15, 30, 54, 0.04), 0 1px 3px rgba(15, 30, 54, 0.02)',
        'card': '0 4px 16px rgba(15, 30, 54, 0.06), 0 1px 2px rgba(15, 30, 54, 0.03)',
        'elevated': '0 12px 32px rgba(15, 30, 54, 0.08), 0 2px 6px rgba(15, 30, 54, 0.04)',
      }
    },
  },
  plugins: [],
}
