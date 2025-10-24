import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys

# Excel file for persistent storage

if len(sys.argv) < 3:
    messagebox.showerror("Error", "This app must be launched from the launcher.")
    sys.exit()

excel_file = sys.argv[1]
sheet_title = sys.argv[2]

# Load or create DataFrame
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file, engine='openpyxl')
    if 'Category' not in df.columns:
        df['Category'] = 'Uncategorized'
else:
    df = pd.DataFrame(columns=["S.No", "Description", "Amount", "Date/Time", "Remaining Budget", "Category"])
    df.to_excel(excel_file, index=False, engine='openpyxl')



# Initialize budget and expenses
if not df.empty:
    total_expense = round(df["Amount"].sum(), 2)
    total_budget = round(total_expense + df["Remaining Budget"].iloc[-1], 2)
else:
    total_budget = 0.00
    total_expense = 0.00
remaining_budget = round(total_budget - total_expense, 2)
total_expense = round(df["Amount"].sum(), 2)
remaining_budget = round(total_budget - total_expense, 2)

# GUI setup
root = tk.Tk()
root.title(os.path.splitext(os.path.basename(excel_file))[0])

# Budget Entry
tk.Label(root, text="Enter Budget:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
budget_entry = tk.Entry(root)
budget_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
budget_entry.bind("<Return>", lambda event: set_budget())
tk.Button(root, text="Set Budget", command=lambda: set_budget()).grid(row=0, column=2, padx=5, pady=5)


chart_frame = tk.Frame(root)
chart_frame.grid(row=6, column=0, columnspan=7, pady=10)

fig, ax = plt.subplots(figsize=(7, 4))
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.get_tk_widget().pack()


def update_pie_chart():
    ax.clear()
    if not df.empty and "Category" in df.columns:
        category_totals = df.groupby("Category")["Amount"].sum()
        if not category_totals.empty:
            labels = [f"{cat} (₹{amt:.2f})" for cat, amt in category_totals.items()]
            ax.pie(category_totals, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title("Expenses by Category", fontsize=14)
    canvas.draw()

def show_histogram():
    if df.empty or "Date/Time" not in df.columns:
        messagebox.showinfo("No Data", "No expenses to visualize.")
        return

    # Convert Date/Time to datetime
    df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='%d %b, %Y %H:%M', errors='coerce')
    df['Date'] = df['Date/Time'].dt.date

    # Group by date and sum amounts
    daily_totals = df.groupby('Date')['Amount'].sum()

    # Calculate mean spending
    mean_spending = daily_totals.mean()

    # Plot histogram
    import matplotlib.pyplot as plt
    import mplcursors

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(daily_totals.index, daily_totals.values, color='skyblue')

    # Format x-axis labels as DD/MM
    ax.set_xticks(daily_totals.index)
    ax.set_xticklabels([date.strftime('%d/%m') for date in daily_totals.index], rotation=45)

    # Add mean line
    ax.axhline(mean_spending, color='red', linestyle='dotted', linewidth=2,
               label=f'Mean: ₹{mean_spending:.2f}')
    ax.set_title('Daily Spending Histogram')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Spending (₹)')
    ax.legend()

    # Add interactive hover tooltips
    cursor = mplcursors.cursor(bars, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        date = daily_totals.index[sel.index]
        amount = daily_totals.values[sel.index]
        sel.annotation.set_text(f"Date: {date.strftime('%d/%m/%Y')}\nSpent: ₹{amount:.2f}")

    plt.tight_layout()
    fig.show()

def set_budget():
    global total_budget, remaining_budget
    try:
        entry = budget_entry.get().strip()
        total_budget = round(float(entry), 2) if entry else 0.00
        remaining_budget = round(total_budget - df["Amount"].sum(), 2)
        update_summary()
        update_pie_chart()
        messagebox.showinfo("Success", f"Budget set to {total_budget:.2f}.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")

# Expense Entry
tk.Label(root, text="Expense Description:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
desc_entry = tk.Entry(root)
desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

tk.Label(root, text="Expense Amount:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
amount_entry = tk.Entry(root)
amount_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")
amount_entry.bind("<Return>", lambda event: add_expense())


# Add Expense Button
tk.Button(root, text="Add Expense", command=lambda: add_expense()).grid(row=1, column=4, padx=5, pady=5)

# Category Dropdown
tk.Label(root, text="Category:").grid(row=1, column=5, padx=5, pady=5, sticky="e")
category_options = [
    "Food", "Transport", "Utilities", "Entertainment", "Health", "Miscellaneous",
    "Education", "Shopping", "Travel", "Insurance", "Rent", "Savings", "Gifts", "Subscriptions"
]

category_combo = ttk.Combobox(root, values=category_options, state="readonly", height=10)
category_combo.grid(row=1, column=6, padx=5, pady=5, sticky="w")



# Custom Date and Time Section
custom_dt_var = tk.BooleanVar()
tk.Checkbutton(root, text="Custom Date and Time", variable=custom_dt_var, command=lambda: toggle_custom_dt()).grid(row=2, column=0, padx=5, pady=5, sticky="w")

custom_dt_frame = tk.Frame(root)

custom_date_label = tk.Label(custom_dt_frame, text="Date:")
custom_date_label.pack(side=tk.LEFT, padx=2)

custom_date_entry = DateEntry(custom_dt_frame, date_pattern='dd-mm-yyyy', width=10)
custom_date_entry.pack(side=tk.LEFT, padx=2)

custom_hour_label = tk.Label(custom_dt_frame, text="Hour:")
custom_hour_label.pack(side=tk.LEFT, padx=2)

custom_hour_combo = ttk.Combobox(custom_dt_frame, values=[f"{i:02d}" for i in range(24)], width=3)
custom_hour_combo.pack(side=tk.LEFT, padx=2)

custom_minute_label = tk.Label(custom_dt_frame, text="Minute:")
custom_minute_label.pack(side=tk.LEFT, padx=2)

custom_minute_combo = ttk.Combobox(custom_dt_frame, values=[f"{i:02d}" for i in range(60)], width=3)
custom_minute_combo.pack(side=tk.LEFT, padx=2)

def toggle_custom_dt():
    if custom_dt_var.get():
        custom_dt_frame.grid(row=2, column=1, columnspan=6, sticky="w", padx=5, pady=5)
    else:
        custom_dt_frame.grid_remove()


def add_expense():
    global df, total_expense, remaining_budget
    try:
        desc = desc_entry.get()
        amount = round(float(amount_entry.get()), 2)

        if custom_dt_var.get():
            date_str = custom_date_entry.get()
            hour_str = custom_hour_combo.get()
            minute_str = custom_minute_combo.get()
            if not hour_str.isdigit() or not minute_str.isdigit():
                raise ValueError("Invalid time format.")
            hour = int(hour_str)
            minute = int(minute_str)
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Time must be between 00:00 and 23:59.")
            formatted_date = datetime.strptime(date_str, "%d-%m-%Y").strftime("%d %b, %Y")
            now = f"{formatted_date} {hour_str}:{minute_str}"
        else:
            now = datetime.now().strftime("%d %b, %Y %H:%M")

        total_expense += amount
        remaining_budget -= amount
        serial_no = len(df) + 1
        category = category_combo.get() if category_combo.get() else "Miscellaneous"
        new_entry = pd.DataFrame([[serial_no, desc, amount, now, remaining_budget, category]],
                         columns=["S.No", "Description", "Amount", "Date/Time", "Remaining Budget", "Category"])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(excel_file, index=False, engine='openpyxl')
        update_table(hide_dt_var.get())
        update_summary()
        update_pie_chart()
        desc_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)
        category_combo.set('')
        custom_hour_combo.set('')
        custom_minute_combo.set('')
    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Expense Table
columns = ["S.No", "Description", "Amount", "Date/Time", "Remaining Budget", "Category"]
tree = ttk.Treeview(root, columns=columns, show="headings")

def toggle_category_filter():
    if filter_var.get():
        category_filter_combo.grid()
    else:
        category_filter_combo.grid_remove()
        update_table(hide_dt_var.get())  # Reset table
filter_var = tk.BooleanVar()
tk.Checkbutton(root, text="Filter by Category", variable=filter_var, command=lambda: toggle_category_filter()).grid(row=2, column=4, padx=5, pady=5, sticky="e")

category_filter_combo = ttk.Combobox(root, values=category_options, state="readonly", height=10)
category_filter_combo.grid(row=2, column=5, padx=5, pady=5, sticky="e")
category_filter_combo.grid_remove()  # Hide initially

category_filter_combo.bind("<<ComboboxSelected>>", lambda event: 
                           update_table(hide_dt_var.get(), category_filter=category_filter_combo.get()))

# Search Bar
search_frame = tk.Frame(root)
search_frame.grid(row=2, column=6, padx=5, pady=5, sticky="e")

tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)

def on_search(*args):
    query = search_entry.get().lower()
    update_table(hide_dt_var.get(), search_query=query)

search_entry.bind("<KeyRelease>", on_search)
tree.grid(row=3, column=0, columnspan=7, padx=5, pady=5)

# Edit and Delete Buttons
action_frame = tk.Frame(root)
action_frame.grid(row=4, column=0, columnspan=7, pady=5)

tk.Button(action_frame, text="Edit Selected", command=lambda: edit_selected()).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="Delete Selected", command=lambda: delete_selected()).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="Show Daily Spending Histogram", command=lambda: show_histogram()).pack(side=tk.LEFT, padx=10)



# Set column headings and default widths
for col in columns:
    tree.heading(col, text=col)

# Checkbox to hide/show Date and Time column
hide_dt_var = tk.BooleanVar()
tk.Checkbutton(root, text="Hide Date and Time", variable=hide_dt_var, command=lambda: update_table(hide_dt_var.get())).grid(row=4, column=0, sticky="w", padx=5, pady=5)

# Summary Section
summary_frame = tk.Frame(root)
summary_frame.grid(row=5, column=0, columnspan=7, pady=10)

expense_label = tk.Label(summary_frame, text=f"Total Expense: {total_expense:.2f}", font=("Arial", 14))
expense_label.pack(side=tk.LEFT, padx=20)

remaining_label = tk.Label(summary_frame, text=f"Remaining Budget: {remaining_budget:.2f}", font=("Arial", 14))
remaining_label.pack(side=tk.LEFT, padx=20)

def update_summary():
    expense_label.config(text=f"Total Expense: {total_expense:.2f}")
    remaining_label.config(text=f"Remaining Budget: {remaining_budget:.2f}")


def update_table(hide_datetime=False, search_query="", category_filter=None):
    # Clear existing rows
    for row in tree.get_children():
        tree.delete(row)

    # Start with full DataFrame
    filtered_df = df

    # Apply search filter
    if search_query:
        filtered_df = filtered_df[filtered_df.apply(
            lambda row: search_query in str(row["Description"]).lower() or search_query in str(row["Date/Time"]).lower(),
            axis=1
        )]

    # Apply category filter
    if category_filter:
        filtered_df = filtered_df[filtered_df["Category"] == category_filter]

    # Set display columns
    display_columns = [col for col in columns if col != "Date/Time"] if hide_datetime else columns
    tree["displaycolumns"] = display_columns

    # Adjust column widths
    if hide_datetime:
        for col in display_columns:
            if col == "S.No":
                tree.column(col, width=50, anchor="center")
            elif col == "Description":
                tree.column(col, width=250, anchor="w")
            else:
                tree.column(col, width=150, anchor="center")
    else:
        for col in columns:
            if col == "S.No":
                tree.column(col, width=50, anchor="center")
            elif col == "Description":
                tree.column(col, width=200, anchor="w")
            else:
                tree.column(col, width=120, anchor="center")

    # Insert filtered rows
    for _, row in filtered_df.iterrows():
        formatted_row = [
            row["S.No"],
            row["Description"],
            f"{row['Amount']:.2f}",
            row["Date/Time"],
            f"{row['Remaining Budget']:.2f}",
            row["Category"]
        ]
        tree.insert("", tk.END, values=formatted_row)


def edit_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a row to edit.")
        return

    item = tree.item(selected[0])
    values = item["values"]
    index = int(values[0]) - 1  # S.No is 1-based

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Expense")

    tk.Label(edit_win, text="Description:").grid(row=0, column=0, padx=5, pady=5)
    desc_edit = tk.Entry(edit_win)
    desc_edit.insert(0, values[1])
    desc_edit.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(edit_win, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
    amount_edit = tk.Entry(edit_win)
    amount_edit.insert(0, values[2])
    amount_edit.grid(row=1, column=1, padx=5, pady=5)

    def save_changes():
        try:
            new_desc = desc_edit.get()
            new_amount = round(float(amount_edit.get()), 2)
            old_amount = df.at[index, "Amount"]
            df.at[index, "Description"] = new_desc
            df.at[index, "Amount"] = new_amount

            # Adjust remaining budgets
            diff = new_amount - old_amount
            for i in range(index, len(df)):
                df.at[i, "Remaining Budget"] -= diff

            df.to_excel(excel_file, index=False, engine='openpyxl')
            update_table(hide_dt_var.get())
            update_summary()
            update_pie_chart()
            edit_win.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    tk.Button(edit_win, text="Save", command=save_changes).grid(row=2, column=0, columnspan=2, pady=10)

def delete_selected():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No selection", "Please select a row to delete.")
        return

    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected expense?")
    if not confirm:
        return

    item = tree.item(selected[0])
    values = item["values"]
    index = int(values[0]) - 1  # S.No is 1-based

    # Remove the row and update serial numbers and budgets
    amount_removed = df.at[index, "Amount"]
    df.drop(index, inplace=True)
    df.reset_index(drop=True, inplace=True)

    for i in range(len(df)):
        df.at[i, "S.No"] = i + 1
        if i == 0:
            df.at[i, "Remaining Budget"] = total_budget - df.at[i, "Amount"]
        else:
            df.at[i, "Remaining Budget"] = df.at[i - 1, "Remaining Budget"] - df.at[i, "Amount"]

    global total_expense, remaining_budget
    total_expense -= amount_removed
    remaining_budget = total_budget - total_expense

    df.to_excel(excel_file, index=False, engine='openpyxl')
    update_table(hide_dt_var.get())
    update_summary()
    update_pie_chart()


# Initial load
update_table(hide_dt_var.get())
update_summary()
update_pie_chart()

root.mainloop()