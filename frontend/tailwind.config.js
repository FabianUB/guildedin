/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        'rpg-purple': '#8B5CF6',
        'rpg-blue': '#3B82F6',
        'rpg-gold': '#F59E0B',
        'rpg-red': '#EF4444',
        'rpg-green': '#10B981'
      },
      fontFamily: {
        'rpg': ['Cinzel', 'serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          'from': { boxShadow: '0 0 20px #8B5CF6' },
          'to': { boxShadow: '0 0 30px #8B5CF6, 0 0 40px #8B5CF6' },
        }
      }
    },
  },
  plugins: [],
}