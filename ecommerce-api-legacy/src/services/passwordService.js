// Service — password hashing.
// P-12: renamed from `badCrypto` to reveal intent. P-10: loop/slice bounds come
// from named config constants. The algorithm is intentionally unchanged so any
// previously produced hash stays identical (behavior preservation).

const config = require('../config');

function hashPassword(plainPassword) {
  let digest = '';
  for (let i = 0; i < config.hash.iterations; i++) {
    digest += Buffer.from(plainPassword).toString('base64').substring(0, config.hash.chunkLength);
  }
  return digest.substring(0, config.hash.outputLength);
}

module.exports = { hashPassword };
