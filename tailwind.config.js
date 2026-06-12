/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './inventario/templates/**/*.html',
    './inventario/static/inventario/js/**/*.js'
  ],
  prefix: 'tw-',
  corePlugins: {
    preflight: false
  },
  theme: {
    extend: {}
  },
  plugins: []
};
