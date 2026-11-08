// Mock service worker contract: does not require a public network or browser.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'sw.js'), 'utf8');
const listeners = {};
const stored = new Map();
let fetches = 0;
const cache = {
  async addAll(paths) { paths.forEach(p => stored.set(new URL(p, 'https://epic.test/repo/').href, {ok: true})); },
  async match(url) { return stored.get(typeof url === 'string' ? url : url.url); },
  async put(url, val) { stored.set(url, val); },
  async keys() { return [...stored.keys()].map(url => ({url})); }
};
const ctx = {
  self: {location: {origin: 'https://epic.test'}, registration: {scope: 'https://epic.test/repo/'},
    addEventListener(name, callback) {listeners[name] = callback;},skipWaiting() {},clients:{claim() {}}},
  caches: {async open(){return cache;}, async keys(){return []},async delete(){return true}},
  fetch: async () => {fetches++; return {ok: true}},
  URL, Promise, Response, console
};
vm.runInNewContext(source, ctx);
assert.equal(typeof listeners.message, 'function');
const reports = [];
async function message(type) {
  const promises = [];
  listeners.message({data:{type},source:{postMessage(m){reports.push(m)}},waitUntil(p){promises.push(p)}});
  await Promise.all(promises);
}
(async () => {
  await message('CACHE_PHOTOS');
  let finish = reports.find(m => m.type === 'COMPLETE');
  assert.equal(finish.total, 230);
  assert.equal(finish.stored, 230);
  assert.equal(finish.failed, 0);
  assert.equal(fetches, 230);
  const firstFetchCount=fetches;
  await message('CACHE_PHOTOS');
  assert.equal(fetches, firstFetchCount, 'Should not fetch already cached images');
  await message('STATUS');
  assert.equal(reports.at(-1).done, 230);
  console.log('PASS offline worker: 230 images cached; repeat download makes no extra requests');
})().catch(error => {console.error(error);process.exit(1)});
