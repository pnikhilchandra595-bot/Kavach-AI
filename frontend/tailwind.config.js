/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        industrial: {
          950: '#080c14',
          900: '#0b111e',
          850: '#10192a',
          800: '#162238',
          750: '#1a2944',
          700: '#1f304f',
          600: '#2d456f',
          500: '#3d5c94',
        },
        sovereign: {
          emerald: '#10b981',
          cyan: '#06b6d4',
          amber: '#f59e0b',
          red: '#ef4444',
          purple: '#8b5cf6',
          orange: '#f97316',
          blue: '#3b82f6',
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
