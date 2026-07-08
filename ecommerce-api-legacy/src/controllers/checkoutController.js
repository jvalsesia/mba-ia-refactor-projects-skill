// Layer 4 — Checkout orchestration (P-04, fixes AP-05).
// All of the checkout business logic that used to live inside the route
// callback now lives here, decoupled from Express and testable in isolation.
// P-12: cryptic identifiers (u, e, p, cid, cc) are renamed for intent.

const config = require('../config');
const { AppError } = require('../middleware/errorHandler');
const { hashPassword } = require('../services/passwordService');

class CheckoutController {
  constructor({ userModel, courseModel, enrollmentModel, paymentModel, auditLogModel }) {
    this.userModel = userModel;
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.auditLogModel = auditLogModel;
  }

  async handle(body) {
    const userName = body.usr;
    const email = body.eml;
    const password = body.pwd;
    const courseId = body.c_id;
    const cardNumber = body.card;

    if (!userName || !email || !courseId || !cardNumber) {
      throw new AppError(400, 'Bad Request');
    }

    const course = await this.courseModel.findActiveById(courseId);
    if (!course) {
      throw new AppError(404, 'Curso não encontrado');
    }

    const userId = await this._resolveUserId(userName, email, password);

    const status = cardNumber.startsWith(config.payment.approvedCardPrefix) ? 'PAID' : 'DENIED';
    if (status === 'DENIED') {
      throw new AppError(400, 'Pagamento recusado');
    }

    const enrollment = await this.enrollmentModel.create(userId, courseId);
    const enrollmentId = enrollment.lastID;
    await this.paymentModel.create(enrollmentId, course.price, status);
    await this.auditLogModel.create(`Checkout curso ${courseId} por ${userId}`);

    return { msg: 'Sucesso', enrollment_id: enrollmentId };
  }

  // Returns the id of the existing user for this email, creating one first if
  // absent — mirroring the legacy "create-then-checkout" behavior.
  async _resolveUserId(userName, email, password) {
    const existing = await this.userModel.findByEmail(email);
    if (existing) {
      return existing.id;
    }
    const passHash = hashPassword(password || config.hash.defaultPassword);
    const created = await this.userModel.create(userName, email, passHash);
    return created.lastID;
  }
}

module.exports = CheckoutController;
