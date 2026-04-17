/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'crypto-dark': '#0d1117',
        'crypto-card': '#161b22',
        'crypto-border': '#30363d',
        'crypto-green': '#2ea043',
        'crypto-red': '#da3633',
        'crypto-blue': '#58a6ff',
        'crypto-purple': '#bc8cff',
        'crypto-yellow': '#d29922',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(88, 166, 255, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(88, 166, 255, 0.6)' },
        },
      },
    },
  },
  plugins: [],
}
