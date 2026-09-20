const profile = require('../site-profile');
const fs = require('node:fs');
const path = require('node:path');

if (profile.prototype) {
  throw new Error('To nadal wzór z przykładami New Balance. Po przygotowaniu pełnej wiki ustaw prototype: false w site-profile.js.');
}

const url = new URL(profile.url);
if (url.protocol !== 'https:' || ['localhost', '127.0.0.1'].includes(url.hostname)) {
  throw new Error('Przed publikacją ustaw potwierdzoną domenę HTTPS w site-profile.js i dodaj static/CNAME.');
}
const cname = path.join(__dirname, '../static/CNAME');
if (!fs.existsSync(cname) || fs.readFileSync(cname, 'utf8').trim() !== url.hostname) {
  throw new Error('static/CNAME musi odpowiadać domenie w site-profile.js.');
}

const branch = process.env.WIKI_DEFAULT_BRANCH;
if (!branch || profile.branch !== branch) {
  throw new Error(`Gałąź źródeł w site-profile.js (${profile.branch}) musi odpowiadać domyślnej gałęzi repozytorium (${branch || 'brak wartości'}).`);
}

console.log(`Profil wiki jest gotowy do publikacji z ${branch}.`);
