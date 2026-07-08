// Layer 2 — Data access foundation.
// P-05: a single injectable connection wrapper. It is constructed once in the
// composition root (app.js) and injected into every model, instead of each
// module opening its own global connection at import time (fixes AP-06).
// The callback-based sqlite3 API is wrapped in promises so controllers can
// orchestrate with async/await instead of nested callbacks.

const sqlite3 = require('sqlite3').verbose();
const config = require('../config');

class Database {
  constructor(location = config.db.location) {
    this.db = new sqlite3.Database(location);
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function (err) {
        if (err) return reject(err);
        resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
  }

  // Schema + seed data, identical to the legacy initDb so the seeded baseline
  // is reproduced exactly.
  async init() {
    await this.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await this.run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await this.run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await this.run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await this.run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

    await this.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
    await this.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
    await this.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await this.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
  }
}

module.exports = Database;
