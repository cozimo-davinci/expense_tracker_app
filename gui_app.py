import customtkinter as tk
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk

class ExpenseTrackerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Ripple Expense Tracker")
        self.master.geometry("1600x800")

        # Load the background image
        bg_image = Image.open("bg2_image.jpg")
        resized_image = bg_image.resize((1600, 800), Image.ADAPTIVE)

        # Convert the resized image to a Tkinter PhotoImage
        bg_photo = ImageTk.PhotoImage(resized_image)

        # Create a label with the background image
        bg_label = tk.CTkLabel(self.master, image=bg_photo, text="")
        bg_label.place(relwidth=1, relheight=1)

        # Ensure the image is retained by tkinter
        bg_label.image = bg_photo

        self.connection = sqlite3.connect("expense_tracker.db")
        self.curr = self.connection.cursor()
        self.create_table()

        self.create_widgets()


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

    def add_expense(self):
        amount = float(self.amount_entry.get())
        category = self.category_entry.get()
        description = self.description_entry.get()
        expense_type = self.expense_type_entry.get()

        date = datetime.now().strftime('%Y-%m-%d')
        self.curr.execute(
            'INSERT INTO expenses (amount, category, description, date, expense_type) VALUES (?, ?, ?, ?, ?)',
            (amount, category, description, date, expense_type))
        self.connection.commit()

        # Update status label
        self.status_label.configure(text="👽Expense has been added successfully👽", text_color="black", font=("Helvetica", 22))

        # Clear input fields
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.expense_type_entry.delete(0, tk.END)

    def view_expenses(self):
        self.curr.execute("SELECT * FROM expenses ORDER BY date")
        expenses = self.curr.fetchall()

        self.expenses_text.delete(1.0, tk.END)
        if expenses:
            for expense in expenses:
                expense_info = (f"👾 ID: {expense[0]}\n🤠 Amount: ${expense[1]}\n"
                                f"🤖 Category: {expense[2]}\n🧐 Description: {expense[3]}\n"
                                f"👻 Date: {expense[4]}\n"
                                f"🥷 Expense Type: {expense[5]}\n\n")
                self.expenses_text.insert(tk.END, expense_info)
        else:
            self.expenses_text.insert(tk.END, "No expenses found! Please try again...")

    def get_monthly_expenses(self, month, year):
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d')

        self.curr.execute("SELECT SUM(amount) FROM expenses WHERE date >= ? AND date < ?", (start_date, end_date))
        total_monthly_expense = self.curr.fetchone()[0]

        self.curr.execute("SELECT category, SUM(amount) FROM expenses WHERE date >= ? AND date < ? GROUP BY category",
                          (start_date, end_date))
        monthly_expenses_by_category = self.curr.fetchall()

        max_category_width = max(len(category) for category, _ in monthly_expenses_by_category) + 8
        max_total_width = max(len(f"${total:.2f}") for _, total in monthly_expenses_by_category) + 8
        max_percentage_width = max(
            len(f"{(total / total_monthly_expense) * 100:.2f}%") for _, total in monthly_expenses_by_category) + 8
        max_annual_avg_width = max(len(f"${total / 12:.2f}") for _, total in monthly_expenses_by_category) + 8

        report = f"Monthly Expense Report for {datetime(year, month, 1).strftime('%B %Y')}:\n"
        report += "🏺 Category      |  🪤 Total Expense   |  💷 Percentage   | 💲 Annual Avg   |  ⚖️ Comparison\n"
        report += "-" * (max_category_width + max_total_width + max_percentage_width + max_annual_avg_width + len(
            " | ") * 8) + "\n"

        for category, total in monthly_expenses_by_category:
            category_percentage = (total / total_monthly_expense) * 100
            annual_avg = total / 12
            comparison = "Higher" if total > annual_avg else "Lower" if total < annual_avg else "Equal"
            report += f"{category:<{max_category_width}} |   ${total:>{max_total_width - 1}.2f}   |   {category_percentage:>{max_percentage_width - 1}.2f}%  |   ${annual_avg:>{max_annual_avg_width - 1}.2f}  |   {comparison}\n"

        report += "-" * (
                    max_category_width + max_total_width + max_percentage_width + max_annual_avg_width + len(" | ") * 8)
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)


    def create_widgets(self):

        custom_font = tk.CTkFont(family="Lobster", size=22, weight="bold", slant="italic", underline=True,
                                 overstrike=False)
        h3_headers = tk.CTkFont(family="Lobster", size=16, weight="bold", slant="roman", underline=False, overstrike=False)

        h2_headers = tk.CTkFont(family="Lobster", size=18, weight="bold", slant="roman", underline=False,
                                overstrike=False)
        button_font = tk.CTkFont(family="Lobster", size=14, weight="bold", slant="roman", underline=False,
                                overstrike=False)
        # Add expense widgets
        add_expense_frame = tk.CTkFrame(self.master, width=400, height=200, fg_color="#EAE151")
        add_expense_frame.grid(row=0, column=0, padx=30, pady=10, sticky=tk.N)

        tk.CTkLabel(add_expense_frame, text="Add Expense Overview", font=custom_font).grid(row=0, column=0, columnspan=2, pady=5)

        tk.CTkLabel(add_expense_frame, text="Amount:", font=h3_headers).grid(row=1, column=0, sticky=tk.W, padx=20)
        self.amount_entry = tk.CTkEntry(add_expense_frame, width=250)
        self.amount_entry.grid(row=1, column=1, pady=5)

        tk.CTkLabel(add_expense_frame, text="Category:", font=h3_headers).grid(row=2, column=0, sticky=tk.W, padx=20)
        self.category_entry = tk.CTkEntry(add_expense_frame, width=250)
        self.category_entry.grid(row=2, column=1, pady=5)

        tk.CTkLabel(add_expense_frame, text="Description:", font=h3_headers).grid(row=3, column=0, sticky=tk.W, padx=20)
        self.description_entry = tk.CTkEntry(add_expense_frame, width=250, height=70)
        self.description_entry.grid(row=3, column=1, pady=5, padx=20)

        tk.CTkLabel(add_expense_frame, text="Expense Type:", font=h3_headers).grid(row=4, column=0, sticky=tk.W, padx=20)
        self.expense_type_entry = tk.CTkEntry(add_expense_frame, width=250)
        self.expense_type_entry.grid(row=4, column=1, pady=5)

        add_button = tk.CTkButton(add_expense_frame, text="Add Expense",
                                  command=self.add_expense, fg_color="#E43F6F", hover_color="#EC0B43", font=button_font)
        add_button.grid(row=5, column=1, columnspan=2, pady=10, padx=20)

        self.status_label = tk.CTkLabel(add_expense_frame, text="")
        self.status_label.grid(row=6, column=0, columnspan=2)

        # View expenses widgets
        view_expenses_frame = tk.CTkFrame(self.master, width=400, height=200, fg_color="#EAE151")
        view_expenses_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.N)

        tk.CTkLabel(view_expenses_frame, text="View Expenses", font=custom_font).grid(row=0, column=0, columnspan=2, pady=5)

        view_button = tk.CTkButton(view_expenses_frame, text="View Expenses", command=self.view_expenses, font=button_font, fg_color="#E43F6F",
                                   hover_color="#EC0B43")
        view_button.grid(row=1, column=0, columnspan=2, pady=10, padx=20)

        self.expenses_text = tk.CTkTextbox(view_expenses_frame, height=250, width=400)
        self.expenses_text.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

        # Monthly expense report widgets
        monthly_report_frame = tk.CTkFrame(self.master, width=400, height=200, fg_color="#EAE151")
        monthly_report_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky=tk.N)

        tk.CTkLabel(monthly_report_frame, text="Monthly Expense Overview", font=custom_font).grid(row=0, column=0, columnspan=2, pady=5)

        report_button = tk.CTkButton(monthly_report_frame, text="Monthly Expense Report",
                                     command=self.show_monthly_report, font=button_font, fg_color="#E43F6F", hover_color="#EC0B43")
        report_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.report_text = tk.CTkTextbox(monthly_report_frame, height=250, width=500)
        self.report_text.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

        # Update and delete expenses widgets
        update_delete_frame = tk.CTkFrame(self.master, width=400, height=400, fg_color="#EAE151")
        update_delete_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky=tk.N)

        tk.CTkLabel(update_delete_frame, text="Update and Delete Expenses Overview", font=custom_font).grid(row=0, column=0, columnspan=2, pady=5)

        # Update expense widgets
        tk.CTkLabel(update_delete_frame, text="Update Expense Overview", font=h2_headers).grid(row=1, column=0, columnspan=2, pady=5)

        tk.CTkLabel(update_delete_frame, text="Expense ID:", font=h3_headers).grid(row=2, column=0, sticky=tk.W, padx=20)
        self.update_id_entry = tk.CTkEntry(update_delete_frame, width=250)
        self.update_id_entry.grid(row=2, column=1, pady=5)

        tk.CTkLabel(update_delete_frame, text="Amount:", font=h3_headers).grid(row=3, column=0, sticky=tk.W, padx=20)
        self.update_amount_entry = tk.CTkEntry(update_delete_frame, width=250)
        self.update_amount_entry.grid(row=3, column=1, pady=5)

        tk.CTkLabel(update_delete_frame, text="Category:", font=h3_headers).grid(row=4, column=0, sticky=tk.W, padx=20)
        self.update_category_entry = tk.CTkEntry(update_delete_frame, width=250)
        self.update_category_entry.grid(row=4, column=1, pady=5)

        tk.CTkLabel(update_delete_frame, text="Description:", font=h3_headers).grid(row=5, column=0, sticky=tk.W, padx=20)
        self.update_description_entry = tk.CTkEntry(update_delete_frame, width=250, height=70)
        self.update_description_entry.grid(row=5, column=1, pady=5, padx=20)

        tk.CTkLabel(update_delete_frame, text="Expense Type:", font=h3_headers).grid(row=6, column=0, sticky=tk.W, padx=20)
        self.update_expense_type_entry = tk.CTkEntry(update_delete_frame, width=250)
        self.update_expense_type_entry.grid(row=6, column=1, pady=5)

        update_button = tk.CTkButton(update_delete_frame, text="Update Expense", command=self.update_expense, font=button_font, fg_color="#E43F6F",
                                     hover_color="#EC0B43")
        update_button.grid(row=7, column=1, columnspan=2, pady=10, padx=20)

        self.update_status_label = tk.CTkLabel(update_delete_frame, text="")
        self.update_status_label.grid(row=8, column=0, columnspan=2)

        # Delete expense widgets
        tk.CTkLabel(update_delete_frame, text="Delete Expense Overview", font=h2_headers).grid(row=9, column=0, columnspan=2, pady=5)

        tk.CTkLabel(update_delete_frame, text="Expense ID:", font=h3_headers).grid(row=10, column=0, sticky=tk.W, padx=20)
        self.delete_id_entry = tk.CTkEntry(update_delete_frame, width=250)
        self.delete_id_entry.grid(row=10, column=1, pady=5)

        delete_button = tk.CTkButton(update_delete_frame, text="Delete Expense", command=self.delete_expense, font=button_font, fg_color="#E43F6F",
                                     hover_color="#EC0B43")
        delete_button.grid(row=11, column=1, columnspan=2, pady=10)

        self.delete_status_label = tk.CTkLabel(update_delete_frame, text="")
        self.delete_status_label.grid(row=12, column=0, columnspan=2)

    def show_monthly_report(self):
        text_font = tk.CTkFont(family="Lobster", size=18, weight="bold", slant="roman", underline=False,
                               overstrike=False)
        button_font = tk.CTkFont(family="Lobster", size=14, weight="bold", slant="roman", underline=False,
                                 overstrike=False)
        # Create a new window for input
        input_window = tk.CTkToplevel(self.master)
        input_window.title("Enter Month and Year")
        input_window.geometry("300x150")

        # Labels and Entry fields for month and year input
        tk.CTkLabel(input_window, text="Month (1-12):", font=text_font).grid(row=0, column=0, padx=10, pady=5)
        month_entry = tk.CTkEntry(input_window)
        month_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.CTkLabel(input_window, text="Year:", font=text_font).grid(row=1, column=0, padx=10, pady=5)
        year_entry = tk.CTkEntry(input_window)
        year_entry.grid(row=1, column=1, padx=10, pady=5)

        # Button to trigger monthly report generation
        generate_button = tk.CTkButton(input_window, text="Generate Report",
                                       command=lambda: self.generate_report(input_window, month_entry.get(),
                                                                            year_entry.get()), font=button_font,
                                       hover_color="#EC0B43", fg_color="#E43F6F")
        generate_button.grid(row=2, columnspan=2, padx=10, pady=10)

    def generate_report(self, input_window, month, year):
        text_font = tk.CTkFont(family="Lobster", size=18, weight="bold", slant="roman", underline=False,
                                overstrike=False)
        button_font = tk.CTkFont(family="Lobster", size=14, weight="bold", slant="roman", underline=False,
                                 overstrike=False)

        # Check if records exist for the given month and year
        self.curr.execute("SELECT COUNT(*) FROM expenses WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?",
                          (month.zfill(2), year))
        records_exist = self.curr.fetchone()[0] > 0

        if records_exist:
            # Generate the report
            self.get_monthly_expenses(int(month), int(year))
        else:
            input_window.geometry("465x150")
            # Display error message
            error_message = "🥷 Such records weren't found. Please try again 🥷"

            # Remove previous error message and entry fields
            for widget in input_window.winfo_children():
                widget.destroy()

            # Display error message
            tk.CTkLabel(input_window, text=error_message, font=text_font).grid(row=0, columnspan=2, padx=10, pady=5)

            # Button to go back to the entry window
            retry_button = tk.CTkButton(input_window, text="💀 Retry 💀", command=self.show_monthly_report, font=button_font, hover_color="#EC0B43", fg_color="#E43F6F")
            retry_button.grid(row=1, columnspan=2, padx=10, pady=10)

    def update_expense(self):
        # Retrieve data from entry fields
        expense_id = int(self.update_id_entry.get())
        amount = float(self.update_amount_entry.get())
        category = self.update_category_entry.get()
        description = self.update_description_entry.get()
        expense_type = self.update_expense_type_entry.get()

        # Update the expense in the database
        self.curr.execute("""
            UPDATE expenses
            SET amount=?, category=?, description=?, expense_type=?
            WHERE id=?
        """, (amount, category, description, expense_type, expense_id))
        self.connection.commit()

        # Update status label
        self.update_status_label.configure(text="⚖️ Expense has been updated successfully ⚖️", text_color="#420039",
                                           font=("Helvetica", 22))

        # Clear input fields
        self.update_id_entry.delete(0, tk.END)
        self.update_amount_entry.delete(0, tk.END)
        self.update_category_entry.delete(0, tk.END)
        self.update_description_entry.delete(0, tk.END)
        self.update_expense_type_entry.delete(0, tk.END)

    def delete_expense(self):
        # Retrieve expense ID to delete
        expense_id = int(self.delete_id_entry.get())

        # Delete the expense from the database
        self.curr.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        self.connection.commit()

        # Update status label
        self.delete_status_label.configure(text="🥷 Expense has been deleted successfully 🥷", text_color="#420039",
                                           font=("Helvetica", 22))

        # Clear input field
        self.delete_id_entry.delete(0, tk.END)

    def create_update_delete_widgets(self):
        # Update expense widgets
        update_label = tk.CTkLabel(self.master, text="Update Expense")
        update_label.grid(row=10, column=0, columnspan=2, pady=10)

        tk.CTkLabel(self.master, text="Expense ID:").grid(row=11, column=0, sticky=tk.W)
        self.update_id_entry = tk.CTkEntry(self.master)
        self.update_id_entry.grid(row=11, column=1, pady=5)

        tk.CTkLabel(self.master, text="Amount:").grid(row=12, column=0, sticky=tk.W)
        self.update_amount_entry = tk.CTkEntry(self.master)
        self.update_amount_entry.grid(row=12, column=1, pady=5)

        tk.CTkLabel(self.master, text="Category:").grid(row=13, column=0, sticky=tk.W)
        self.update_category_entry = tk.CTkEntry(self.master)
        self.update_category_entry.grid(row=13, column=1, pady=5)

        tk.CTkLabel(self.master, text="Description:").grid(row=14, column=0, sticky=tk.W)
        self.update_description_entry = tk.CTkEntry(self.master)
        self.update_description_entry.grid(row=14, column=1, pady=5)

        tk.CTkLabel(self.master, text="Expense Type:").grid(row=15, column=0, sticky=tk.W)
        self.update_expense_type_entry = tk.CTkEntry(self.master)
        self.update_expense_type_entry.grid(row=15, column=1, pady=5)

        update_button = tk.CTkButton(self.master, text="Update Expense", command=self.update_expense)
        update_button.grid(row=16, column=0, columnspan=2, pady=10)

        self.update_status_label = tk.CTkLabel(self.master, text="")
        self.update_status_label.grid(row=17, column=0, columnspan=2)

        # Delete expense widgets
        delete_label = tk.CTkLabel(self.master, text="Delete Expense")
        delete_label.grid(row=18, column=0, columnspan=2, pady=10)

        tk.CTkLabel(self.master, text="Expense ID:").grid(row=19, column=0, sticky=tk.W)
        self.delete_id_entry = tk.CTkEntry(self.master)
        self.delete_id_entry.grid(row=19, column=1, pady=5)

        delete_button = tk.CTkButton(self.master, text="Delete Expense", command=self.delete_expense)
        delete_button.grid(row=20, column=0, columnspan=2, pady=10)

        self.delete_status_label = tk.CTkLabel(self.master, text="")
        self.delete_status_label.grid(row=21, column=0, columnspan=2)

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    root = tk.CTk()
    app = ExpenseTrackerGUI(root)
    root.mainloop()
