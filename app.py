from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import date

app = Flask(__name__)
DB_NAME = "expenses.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return render_template("index.html")


# ---- CREATE ----
@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    title = data.get("title", "").strip()
    amount = data.get("amount")
    category = data.get("category", "").strip()
    expense_date = data.get("date", "").strip() or str(date.today())
    note = data.get("note", "").strip()

    # Validation - edge cases
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if amount is None or not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400
    if category not in ["Food", "Transport", "Shopping"]:
        return jsonify({"error": "Invalid category"}), 400

    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (title, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
        (title, amount, category, expense_date, note)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added"}), 201


# ---- READ (list, with optional filters) ----
@app.route("/api/expenses", methods=["GET"])
def list_expenses():
    category = request.args.get("category")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    title_search = request.args.get("title")

    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    if title_search:
        query += " AND title LIKE ?"
        params.append(f"%{title_search}%")

    query += " ORDER BY date DESC"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    expenses = [dict(row) for row in rows]
    return jsonify(expenses)


# ---- UPDATE ----
@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json()

    title = data.get("title", "").strip()
    amount = data.get("amount")
    category = data.get("category", "").strip()
    expense_date = data.get("date", "").strip()
    note = data.get("note", "").strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if amount is None or not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400
    if category not in ["Food", "Transport", "Shopping"]:
        return jsonify({"error": "Invalid category"}), 400
    if not expense_date:
        return jsonify({"error": "Date is required"}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    conn.execute(
        "UPDATE expenses SET title=?, amount=?, category=?, date=?, note=? WHERE id=?",
        (title, amount, category, expense_date, note, expense_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense updated"})


# ---- DELETE ----
@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    conn = get_db()
    existing = conn.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if existing is None:
        conn.close()
        return jsonify({"error": "Expense not found"}), 404

    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense deleted"})


# ---- MONTHLY SUMMARY ----
@app.route("/api/summary", methods=["GET"])
def monthly_summary():
    today = date.today()
    month_prefix = today.strftime("%Y-%m")  # e.g. "2026-06"

    conn = get_db()
    rows = conn.execute(
        "SELECT category, amount FROM expenses WHERE date LIKE ?",
        (f"{month_prefix}%",)
    ).fetchall()
    conn.close()

    total = 0
    breakdown = {}

    for row in rows:
        total += row["amount"]
        breakdown[row["category"]] = breakdown.get(row["category"], 0) + row["amount"]

    return jsonify({"total": total, "breakdown": breakdown, "month": month_prefix})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)