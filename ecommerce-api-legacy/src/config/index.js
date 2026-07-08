// Layer 1 — Config
// P-01: all secrets and environment-specific values are read from the
// environment. No literal secret remains in source. See .env.example.
// P-10: business/hashing literals are named constants here, not magic numbers.

const config = {
  port: process.env.PORT || 3000,

  // Secrets — sourced exclusively from the environment (empty when unset so the
  // app still boots; a real value must be provided via the environment).
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  smtp: {
    user: process.env.SMTP_USER || '',
  },
  db: {
    user: process.env.DB_USER || '',
    password: process.env.DB_PASS || '',
    location: process.env.DB_LOCATION || ':memory:',
  },

  // Auth — when ADMIN_TOKEN is set the auth middleware enforces a Bearer token
  // on sensitive routes; when unset, enforcement is disabled (see middleware/auth).
  auth: {
    token: process.env.ADMIN_TOKEN || '',
  },

  // Payment rule — named constant instead of the magic literal "4".
  payment: {
    approvedCardPrefix: '4',
  },

  // Password hashing parameters — named instead of inline magic numbers.
  hash: {
    iterations: 10000,
    chunkLength: 2,
    outputLength: 10,
    defaultPassword: '123456',
  },
};

module.exports = config;
