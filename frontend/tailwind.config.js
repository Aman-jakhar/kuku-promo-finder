/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Professional neutral-dark palette — no color tint in backgrounds
        ink: {
          0:   '#000000',
          50:  '#0A0A0A',  // page bg
          100: '#111111',  // elevated surface
          200: '#161616',  // card
          300: '#1C1C1C',  // card hover / input
          400: '#252525',  // subtle separator
          500: '#2E2E2E',  // border strong
        },
        // Single accent: clean blue — used sparingly
        accent: '#3B82F6',
        // Semantic states — desaturated, not "AI rainbow"
        ok:   '#22C55E',  // success / validated
        warn: '#F59E0B',  // caution only
        // Keep for phase labels (hook/cliff) but use them sparingly
        hook: '#F97316',  // orange — hook zone only
        cliff: '#8B5CF6', // violet — cliffhanger only
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderColor: {
        DEFAULT: 'rgba(255,255,255,0.08)',
      }
    },
  },
  plugins: [],
}
