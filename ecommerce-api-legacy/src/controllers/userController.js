// Layer 4 — User orchestration (P-04).

class UserController {
  constructor({ userModel }) {
    this.userModel = userModel;
  }

  async remove(id) {
    await this.userModel.deleteById(id);
    // Message preserved verbatim from the legacy endpoint (behavior parity).
    return 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';
  }
}

module.exports = UserController;
