const india = require('@svg-maps/india');
const fs = require('fs');

const paths = india.default.locations.map(l => 
    `<path id="${l.id}" name="${l.name}" d="${l.path}" class="state-path" fill="#e5e7eb" stroke="#ffffff" stroke-width="1"></path>`
).join('\n');

const svg = `<svg viewBox="${india.default.viewBox}" xmlns="http://www.w3.org/2000/svg" class="india-map-svg">\n${paths}\n</svg>`;

fs.writeFileSync('css/india.svg', svg);
console.log('SVG generated successfully!');
