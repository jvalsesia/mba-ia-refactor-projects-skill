// Layer 5 — Centralized auth middleware (P-08, fixes AP-03)
// The legacy app guarded no sensitive route. This middleware centralizes the
// check so /api/admin/* and destructive routes are protected in one place.
//
// Enforcement is env-gated to preserve the captured baseline: when ADMIN_TOKEN
// is unset (as in the legacy environment) the middleware is a pass-through, so
// existing behavior is unchanged. Setting ADMIN_TOKEN activates Bearer-token
// enforcement without touching any route.

const config = require('./../config');
const { AppError } = require('./errorHandler');

function requireAuth(req, res, next) {
  if (!config.auth.token) {
    return next(); // enforcement disabled — no token configured
  }
  const provided = req.headers['authorization'];
  if (provided !== `Bearer ${config.auth.token}`) {
    return next(new AppError(401, 'Unauthorized'));
  }
  return next();
}

module.exports = { requireAuth };
