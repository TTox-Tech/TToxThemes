const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const packageRoot = path.dirname(require.resolve('lucide/package.json'));
const metadata = JSON.parse(fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8'));
if (metadata.version !== '0.468.0') throw new Error('Expected locked Lucide version 0.468.0');
fs.copyFileSync(path.join(packageRoot, 'dist/umd/lucide.min.js'), path.join(root, 'dist/assets/lucide.min.js'));
require('./stamp-assets.cjs');
console.log('Prepared pinned Lucide browser asset; dependency source stays outside Git.');
