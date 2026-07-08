// Layer 5 — Centralized error handling (P-09)
// One place formats every error consistently and never leaks stack traces.
// Known 4xx cases throw an AppError with the exact legacy message/status so
// responses stay byte-for-byte compatible; unexpected errors become a generic
// 500 instead of ad-hoc per-handler strings.

class AppError extends Error {
  constructor(status, message) {
    super(message);
    this.name = 'AppError';
    this.status = status;
    this.expose = true; // message is safe to send to the client
  }
}

// Wraps an async route handler so any rejection is forwarded to Express's
// error pipeline (which ends at errorHandler below) instead of hanging.
function asyncHandler(handler) {
  return (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);
}

// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
  const status = err.status || 500;
  const message = err.expose ? err.message : 'Internal Server Error';
  if (status >= 500) {
    console.error('[ERROR]', err);
  }
  res.status(status).send(message);
}

module.exports = { AppError, asyncHandler, errorHandler };
