import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: { colors: { ink: '#18343b', teal: '#146b72', cream: '#f5f8f7', amber: '#f2b84b' } } },
  plugins: [],
} satisfies Config
