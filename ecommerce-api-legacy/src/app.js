// Layer 6 — Composition root / entry point (P-05).
// The one place that wires the app together: loads config, constructs the
// single DB connection and all dependencies, injects them downward, registers
// routes and the centralized error handler, then starts the server. No module
// self-instantiates a global connection at import time (fixes AP-06).

const express = require('express');
const config = require('./config');

const Database = require('./models/database');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditLogModel = require('./models/auditLogModel');
const ReportModel = require('./models/reportModel');

const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');

const registerRoutes = require('./routes');
const { requireAuth } = require('./middleware/auth');
const { errorHandler } = require('./middleware/errorHandler');

async function bootstrap() {
  const database = new Database();
  await database.init();

  const models = {
    userModel: new UserModel(database),
    courseModel: new CourseModel(database),
    enrollmentModel: new EnrollmentModel(database),
    paymentModel: new PaymentModel(database),
    auditLogModel: new AuditLogModel(database),
    reportModel: new ReportModel(database),
  };

  const controllers = {
    checkoutController: new CheckoutController(models),
    reportController: new ReportController(models),
    userController: new UserController(models),
  };

  const app = express();
  app.use(express.json());

  registerRoutes(app, controllers, { requireAuth });
  app.use(errorHandler);

  app.listen(config.port, () => {
    console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
  });
}

bootstrap().catch((err) => {
  console.error('[FATAL] Falha ao iniciar a aplicação', err);
  process.exit(1);
});
