# Expense Tracker

A simple personal expense tracker web app.

## What it does

- Add expenses with title, amount, category (Food / Transport / Shopping), date (defaults to today), and an optional note
- View all expenses, sorted by date (most recent first)
- Edit or delete any expense
- See a monthly summary: total spent this month + breakdown by category
- Filter expenses by category, date range, and title search

## Why these choices

- **Flask** — lightweight Python web framework, fast to set up for a small CRUD app, no heavy configuration needed
- **SQLite** — file-based database, no separate database server to install/configure, perfect for a small single-user app
- **Plain HTML/CSS/JS** — no frontend framework needed for this scope; keeps the app simple and easy to run with zero build steps

## How to run

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   python app.py
   ```

3. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

The database file (`expenses.db`) is created automatically on first run.

## Edge cases handled

- Empty expense list shows a friendly "No expenses found" message instead of a blank table
- Empty monthly summary (no expenses yet this month) shows a friendly message instead of ₹0.00 with no context
- Invalid inputs (empty title, non-positive or non-numeric amount, invalid category) are rejected with clear error messages, both on add and edit
- Date defaults to today if left blank when adding an expense
- Filtering by a date range where "from" is after "to" simply returns no results (no crash) since the underlying SQL comparison naturally handles it
- Deleting or editing a non-existent expense ID returns a proper error instead of crashing
- Title search is case-insensitive partial match, so partial/typo-free substrings still find results