import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

# 1. tailwind.config.js
tailwind_config = """/** @type {import('tailwindcss').Config} */
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
"""

with open(os.path.join(FRONTEND_DIR, "tailwind.config.js"), "w", encoding="utf-8") as f:
    f.write(tailwind_config)

# 2. postcss.config.js
postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
with open(os.path.join(FRONTEND_DIR, "postcss.config.js"), "w", encoding="utf-8") as f:
    f.write(postcss_config)

# 3. index.html
index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23D97450'><path d='M12 2L2 12h3v8h14v-8h3L12 2zm0 3.84L18 12h-2v6H8v-6H6l6-6.16z'/></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ResQFlow AI — From Community Needs to Verified Relief Delivery</title>
    <meta name="description" content="Intelligent AI-powered flood relief, resource coordination & transparent distribution platform connecting Affected Communities, Volunteers, NGOs, Warehouses, Donors, and Authorities." />
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  </head>
  <body class="bg-ivory text-navy selection:bg-terracotta/20 selection:text-terracotta">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
with open(os.path.join(FRONTEND_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# 4. src/index.css
index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-ivory text-navy antialiased min-h-screen font-sans;
  }
}

/* Custom restrained map container */
.leaflet-container {
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif !important;
  background-color: #EDE8DE !important;
  border-radius: 0.75rem;
}

.leaflet-popup-content-wrapper {
  background: #FDFBF7 !important;
  color: #0F1E36 !important;
  border-radius: 0.75rem !important;
  border: 1px solid rgba(107, 124, 150, 0.2) !important;
  box-shadow: 0 10px 25px -5px rgba(15, 30, 54, 0.1) !important;
}

.leaflet-popup-tip {
  background: #FDFBF7 !important;
}

/* Restrained scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: #F4EFE6;
}
::-webkit-scrollbar-thumb {
  background: #8FA0B8;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #6B7C96;
}
"""

with open(os.path.join(FRONTEND_DIR, "src", "index.css"), "w", encoding="utf-8") as f:
    f.write(index_css)

print("Frontend configuration and base styles written successfully.")
