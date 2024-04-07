import sqlite3
from datetime import datetime


class ExpenseTracker:
    def __init__(self, db_name="expense_tracker.db"):
        self.connection = sqlite3.connect(db_name)
        self.curr = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            date DATE,
            expense_type TEXT
            )
        """)
        self.connection.commit()

    def add_expense(self, amount, category, description, expense_type):
        date = datetime.now().strftime('%Y-%m-%d')
        self.curr.execute(
            'INSERT INTO expenses (amount, category, description, date, expense_type) VALUES (?, ?, ?, ?, ?)',
            (amount, category, description, date, expense_type))
        self.connection.commit()
        print("Expense has been added successfully!")

    def get_monthly_expenses(self, month, year):
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d')

        # Total monthly expenses
        self.curr.execute("SELECT SUM(amount) FROM expenses WHERE date >= ? AND date < ?", (start_date, end_date))
        total_monthly_expense = self.curr.fetchone()[0]

        # Total annual expenses
        start_year = datetime(year, 1, 1).strftime('%Y-%m-%d')
        end_year = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
        self.curr.execute("SELECT category, SUM(amount) FROM expenses WHERE date >= ? AND date < ? GROUP BY category",
                          (start_year, end_year))
        annual_expenses_by_category = self.curr.fetchall()

        # Average expenses for each category for the year
        average_expenses_by_category = {category: total / 12 for category, total in annual_expenses_by_category}

        # Total expenses for the month by category
        self.curr.execute("SELECT category, SUM(amount) FROM expenses WHERE date >= ? AND date < ? GROUP BY category",
                          (start_date, end_date))
        monthly_expenses_by_category = self.curr.fetchall()

        # Display monthly expense report
        print(f"Monthly Expense Report for {datetime(year, month, 1).strftime('%B %Y')}:")
        print("Category      |   Total Expense   |   Percentage   |   Annual Avg   |   Comparison")

        # Calculate maximum column widths
        max_category_width = max(len(category) for category, _ in monthly_expenses_by_category) + 3
        max_total_width = max(len(f"${total:.2f}") for _, total in monthly_expenses_by_category) + 3
        max_percentage_width = max(
            len(f"{(total / total_monthly_expense) * 100:.2f}%") for _, total in monthly_expenses_by_category) + 3
        max_annual_avg_width = max(len(f"${average_expenses_by_category.get(category, 0):.2f}") for category, _ in
                                   monthly_expenses_by_category) + 3

        # Print table header
        print(
            "-" * (max_category_width + max_total_width + max_percentage_width + max_annual_avg_width + len(" | ") * 4))

        # Print table rows
        for category, total in monthly_expenses_by_category:
            category_percentage = (total / total_monthly_expense) * 100
            annual_avg = average_expenses_by_category.get(category, 0)
            comparison = "Higher" if total > annual_avg else "Lower" if total < annual_avg else "Equal"

            print(
                f"{category:<{max_category_width}} |   ${total:>{max_total_width - 1}.2f}   |   {category_percentage:>{max_percentage_width - 1}.2f}%  |   ${annual_avg:>{max_annual_avg_width - 1}.2f}  |   {comparison}")

        # Print bottom line of table
        print(
            "-" * (max_category_width + max_total_width + max_percentage_width + max_annual_avg_width + len(" | ") * 4))

    def view_expenses(self):
        self.curr.execute("SELECT * FROM expenses ORDER BY date")
        expenses = self.curr.fetchall()
        if expenses:
            # Define column names
            columns = ["ID", "Amount", "Category", "Description", "Expense Type", "Date"]
            # Calculate maximum width for each column
            max_widths = [max(len(str(expense[i])) for expense in expenses) for i in range(len(columns))]
            # Add some extra padding
            max_widths = [max_width + 3 for max_width in max_widths]

            # Print header
            header = " | ".join(f"{column:<{max_widths[i]}}" for i, column in enumerate(columns))
            print(header)
            print("-" * sum(max_widths))

            # Print expenses
            for expense in expenses:
                row = " | ".join(f"{str(expense[i]):<{max_widths[i]}}" for i in range(len(columns)))
                print(row)
        else:
            print("No expenses found! Please try again...")

    def main(self):
        while True:
            print("🧬Main Menu🧬")
            print("1. 💷Add expense💷")
            print("2. 🔍View expenses🔍")
            print("3. 📅View total expenses for a month📅")
            print("4. 👀Exit👀")

            choice = int(input("Enter your choice: "))

            if choice == 1:
                amount = float(input("Enter the amount of money spent: $"))
                category = input("Enter the category name: ")
                description = input("Provide a small description: ")
                expense_type = input("Enter the expense type: ")
                self.add_expense(amount, category, description, expense_type)

            elif choice == 2:
                self.view_expenses()

            elif choice == 3:
                year = int(input("Enter the year: "))
                month = int(input("Enter a month: "))
                self.get_monthly_expenses(month, year)

            elif choice == 4:
                print("Initializing exit...")
                break

            else:
                print("Invalid choice. Please try again!")

        self.connection.close()


if __name__ == "__main__":
    tracker = ExpenseTracker()
    tracker.main()
