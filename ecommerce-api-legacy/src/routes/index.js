// Layer 3 — Routes (views).
// Routing only: each handler parses the request, calls a controller, and
// returns the result. No business logic and no DB access here (fixes AP-05 at
// the route layer). Sensitive routes are guarded by the centralized auth
// middleware (P-08). asyncHandler forwards rejections to the central error
// handler (P-09).

const { asyncHandler } = require('../middleware/errorHandler');

function registerRoutes(app, controllers, middleware) {
  const { checkoutController, reportController, userController } = controllers;
  const { requireAuth } = middleware;

  app.post(
    '/api/checkout',
    asyncHandler(async (req, res) => {
      const result = await checkoutController.handle(req.body);
      res.status(200).json(result);
    })
  );

  app.get(
    '/api/admin/financial-report',
    requireAuth,
    asyncHandler(async (req, res) => {
      const report = await reportController.generate();
      res.json(report);
    })
  );

  app.delete(
    '/api/users/:id',
    requireAuth,
    asyncHandler(async (req, res) => {
      const message = await userController.remove(req.params.id);
      res.send(message);
    })
  );
}

module.exports = registerRoutes;
