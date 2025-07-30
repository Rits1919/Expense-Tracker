import sqlite3
from datetime import date
import csv

# ------------------ DATABASE SETUP ------------------ #
conn = sqlite3.connect("expenses.db")
cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create expenses table with category
cur.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    item TEXT,
    amount REAL,
    category TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
conn.commit()

# ------------------ USER LOGIN SYSTEM ------------------ #
def register_user():
    username = input("👤 New username: ")
    password = input("🔐 New password: ")

    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("✅ Registered successfully!\n")
    except sqlite3.IntegrityError:
        print("❌ Username already exists. Try login.\n")

def login_user():
    username = input("👤 Username: ")
    password = input("🔒 Password: ")

    cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    result = cur.fetchone()
    if result:
        print(f"\n✅ Welcome back, {username}!\n")
        return result[0]  # return user_id
    else:
        print("❌ Login failed. Try again.\n")
        return None

def reset_password():
    username = input("👤 Username: ")
    new_password = input("🔐 New Password: ")
    cur.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    print("✅ Password updated successfully!\n")


# ------------------ EXPENSE TRACKER ------------------ #

def add_multiple_expenses(user_id):
    print("\n🗓 Expense Entry ")

    # Step 1: Ask date once
    date_choice = input("📅 Enter custom date? (y/n): ")
    if date_choice.lower() == 'y':
        expense_date = input("Enter date (YYYY-MM-DD): ")
    else:
        expense_date = str(date.today())

    # 🟢 Step 2: Start first expense entry directly
    while True:
        category = input("🏷️ Category (Food/Travel/etc): ")
        item = input("💸 What did you spend on? ")
        amount = float(input("₹ Amount: "))

        cur.execute("INSERT INTO expenses (user_id, date, item, amount,category) VALUES (?, ?, ?, ?, ?)",
                    (user_id, expense_date, item, amount,category))
        conn.commit()
        print(f"✅ Saved: {item} ({category}) - ₹{amount} on {expense_date}\n")

        # 🔁 Step 3: Ask for more
        add_more = input("➕ Add another expense for this date? (y/n): ")
        if add_more.lower() != 'y':
            break

def view_expenses(user_id):
    print("📃 Your Expenses:\n")
    cur.execute("SELECT id, date, item, category, amount FROM expenses WHERE user_id=? ORDER BY date", (user_id,))
    records = cur.fetchall()
    if not records:
        print("No expenses found.")
    else:
        for row in records:
            print(f"ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} | ₹{row[4]}")
    print()


def show_total_expense(user_id):
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (user_id,))
    result = cur.fetchone()
    total = result[0] if result[0] else 0
    print(f"\n📊 Total Spent: ₹{total}")


def show_category_expense(user_id):
    category = input("🏷️ Enter category to filter (e.g. Food, Travel): ").strip().lower()
    cur.execute("SELECT date, item, amount FROM expenses WHERE user_id=? AND LOWER(category)=?", (user_id, category))
    records = cur.fetchall()

    if not records:
        print(f"❌ No expenses found in category '{category}'\n")
        return

    total = 0
    print(f"\n📋 Expenses in category '{category}':\n")
    for row in records:
        print(f"{row[0]} | {row[1]} | ₹{row[2]}")
        total += row[2]

    print(f"\n💰 Total in '{category}': ₹{total}\n")


#1.Day-wise Total Function
def show_day_total(user_id):
    day = input("📅 Enter date (YYYY-MM-DD): ")
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND date=?", (user_id, day))
    result = cur.fetchone()                #Database se query ka result uthata hai
    total = result[0] if result[0] else 0  #Agar None hai to total 0 le lo, warna actual sum
    print(f"\n📅 Total on {day}: ₹{total}")

#2. Month-wise Total Function
def show_month_total(user_id):
    month = input("🗓 Enter month (YYYY-MM): ")
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?", (user_id, month))
    result = cur.fetchone()
    total = result[0] if result[0] else 0   #Agar None hai to total 0 le lo, warna actual sum
    print(f"\n🗓 Total in {month}: ₹{total}")

#3.Year-wise Total Function
def show_year_total(user_id):
    year = input("📆 Enter year (YYYY): ")
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND strftime('%Y', date)=?", (user_id, year))
    result = cur.fetchone()
    total = result[0] if result[0] else 0  #Agar None hai to total 0 le lo, warna actual sum
    print(f"\n📆 Total in {year}: ₹{total}")

#export to csv file
def export_expenses(user_id):
    with open("my_expenses.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Item", "Category", "Amount"])
        cur.execute("SELECT date, item, category, amount FROM expenses WHERE user_id=?", (user_id,))
        writer.writerows(cur.fetchall())
    print("✅ Exported to my_expenses.csv\n")

#update the expense
def update_expense(user_id):
    print("✏️ Your Expenses:\n")
    cur.execute("SELECT id, date, item, amount, category FROM expenses WHERE user_id=?", (user_id,))
    records = cur.fetchall()

    if not records:
        print("No expenses to update.\n")
        return

    for row in records:
        print(f"ID: {row[0]} | {row[1]} | {row[2]} | ₹{row[3]} | {row[4]}")

    expense_id = input("\n🔁 Enter the ID of the expense to update: ")

    # Fetch current values
    cur.execute("SELECT item, category, amount, date FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
    current = cur.fetchone()

    if not current:
        print("❌ Invalid expense ID.")
        return

    print(f"\nCurrent → Item: {current[0]}, Category: {current[1]}, Amount: ₹{current[2]}, Date: {current[3]}")

    # Optional new values
    new_item = input("💬 New item name (press Enter to keep same): ") or current[0]
    new_category = input("🏷️ New category (press Enter to keep same): ") or current[1]

    new_amount_input = input("₹ New amount (press Enter to keep same): ")
    new_amount = float(new_amount_input) if new_amount_input else current[2]

    new_date = input("📅 New date (YYYY-MM-DD) (press Enter to keep same): ") or current[3]

    cur.execute("""
        UPDATE expenses
        SET item=?, category=?, amount=?, date=?
        WHERE id=? AND user_id=?
    """, (new_item, new_category, new_amount, new_date, expense_id, user_id))
    conn.commit()
    print("✅ Expense updated successfully!\n")


# delete the expense
def delete_expense(user_id):
    view_expenses(user_id)
    expense_id = input("🆔 Enter Expense ID to delete: ")

    # Check if this expense belongs to the user
    cur.execute("SELECT * FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
    record = cur.fetchone()
    if not record:
        print("❌ Invalid ID or not your expense.\n")
        return

    confirm = input("⚠️ Are you sure you want to delete this expense? (y/n): ")
    if confirm.lower() == 'y':
        cur.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, user_id))
        conn.commit()
        print("🗑️ Expense deleted successfully!\n")
    else:
        print("❎ Deletion cancelled.\n")



# ------------------ MAIN APP FLOW ------------------ #
print("🔐 Welcome to Expense Tracker")

while True:
    action = input("Do you want to (r)egister, (l)ogin, (f)orgot password or (q)uit? ").lower()
    if action == 'r':
        register_user()
    elif action == 'l':
        user_id = login_user()
        if user_id:
            while True:
                print("\nChoose an option:")
                print("  (a) ➕ Add expense")
                print("  (v) 📄 View all expenses")
                print("  (t) 💰 Show total expense")
                print("  (c) 🏷️ Category-wise total")
                print("  (d) 📅 Day-wise total")
                print("  (m) 🗓 Month-wise total")
                print("  (y) 📆 Year-wise total")
                print("  (u) ✏️ Update an expense")
                print("  (x) ❌ Delete an expense")
                print("  (e) 📃 Export to CSV")
                print("  (l) 🔓 Logout")

                task = input("Enter your choice: ").lower()
                if task == 'a':
                    add_multiple_expenses(user_id)
                elif task == 'v':
                    view_expenses(user_id)
                    show_total_expense(user_id)
                elif task == 't':
                    show_total_expense(user_id)
                elif task == 'c':
                    show_category_expense(user_id)
                elif task == 'd':
                    show_day_total(user_id)
                elif task == 'm':
                    show_month_total(user_id)
                elif task == 'y':
                    show_year_total(user_id)
                elif task == 'e':
                    export_expenses(user_id)
                elif task == 'l':
                    print("🔓 Logged out.👋\n")
                    break
                elif task == 'u':
                    update_expense(user_id)
                elif task == 'x':
                    delete_expense(user_id)

                else:
                    print("❌ Invalid choice. Try again.")
    elif action == 'f':
        reset_password()
    elif action == 'q':
        print("👋 Goodbye!")
        break
    else:
        print("❓ Invalid input. Try again.")

# Close DB connection at the end
conn.close()

