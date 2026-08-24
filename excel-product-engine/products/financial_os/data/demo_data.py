"""Realistic Financial OS demo data.

Section 20 of the original spec: no meaningless "Test 1 / Test 2"
placeholders — every row here is something a real Indian household's
tracker would actually contain.
"""

from __future__ import annotations

from datetime import date

INCOME_ROWS: list[dict[str, object]] = [
    {"Date": date(2026, 7, 1), "Source": "Acme Corp", "Category": "Salary",
     "Amount": 85000, "Notes": "Monthly salary"},
    {"Date": date(2026, 7, 15), "Source": "Freelance — Website Redesign", "Category": "Freelance",
     "Amount": 25000, "Notes": ""},
    {"Date": date(2026, 8, 1), "Source": "Acme Corp", "Category": "Salary",
     "Amount": 85000, "Notes": "Monthly salary"},
    {"Date": date(2026, 8, 10), "Source": "Freelance — API Integration", "Category": "Freelance",
     "Amount": 18000, "Notes": ""},
]

EXPENSE_ROWS: list[dict[str, object]] = [
    {"Date": date(2026, 7, 1), "Category": "Rent", "Description": "Monthly rent",
     "Amount": 22000, "Payment Method": "Net Banking", "Notes": ""},
    {"Date": date(2026, 7, 5), "Category": "Groceries", "Description": "BigBasket order",
     "Amount": 6500, "Payment Method": "UPI", "Notes": ""},
    {"Date": date(2026, 7, 10), "Category": "Utilities", "Description": "Electricity bill",
     "Amount": 2200, "Payment Method": "UPI", "Notes": ""},
    {"Date": date(2026, 7, 18), "Category": "Transport", "Description": "Fuel + cab rides",
     "Amount": 3500, "Payment Method": "UPI", "Notes": ""},
    {"Date": date(2026, 8, 1), "Category": "Rent", "Description": "Monthly rent",
     "Amount": 22000, "Payment Method": "Net Banking", "Notes": ""},
    {"Date": date(2026, 8, 6), "Category": "Groceries", "Description": "Monthly groceries",
     "Amount": 7200, "Payment Method": "UPI", "Notes": ""},
    {"Date": date(2026, 8, 12), "Category": "Entertainment", "Description": "Movies + dining out",
     "Amount": 2800, "Payment Method": "Credit Card", "Notes": ""},
]

BILLS_ROWS: list[dict[str, object]] = [
    {"Bill": "Electricity Bill", "Category": "Utilities", "Due Date": date(2026, 8, 20),
     "Amount": 2200, "Status": "Pending", "Recurring": "Monthly", "Notes": ""},
    {"Bill": "Jio Fiber Internet", "Category": "Subscriptions", "Due Date": date(2026, 8, 15),
     "Amount": 999, "Status": "Paid", "Recurring": "Monthly", "Notes": ""},
    {"Bill": "Health Insurance Premium", "Category": "Insurance", "Due Date": date(2026, 9, 1),
     "Amount": 18000, "Status": "Pending", "Recurring": "Yearly", "Notes": ""},
    {"Bill": "Car Loan EMI", "Category": "Loan EMI", "Due Date": date(2026, 8, 5),
     "Amount": 12500, "Status": "Paid", "Recurring": "Monthly", "Notes": ""},
    {"Bill": "Netflix + Prime", "Category": "Subscriptions", "Due Date": date(2026, 8, 10),
     "Amount": 649, "Status": "Paid", "Recurring": "Monthly", "Notes": ""},
]

INVESTMENT_ROWS: list[dict[str, object]] = [
    {"Date": date(2025, 1, 15), "Asset": "HDFC Flexicap Fund", "Asset Type": "Mutual Fund",
     "Quantity": 500, "Purchase Price": 45, "Current Value": 27500},
    {"Date": date(2025, 6, 1), "Asset": "Reliance Industries", "Asset Type": "Stock",
     "Quantity": 20, "Purchase Price": 2400, "Current Value": 51000},
    {"Date": date(2024, 4, 1), "Asset": "PPF Account", "Asset Type": "PPF",
     "Quantity": 1, "Purchase Price": 150000, "Current Value": 165000},
    {"Date": date(2023, 1, 1), "Asset": "Emergency Fund FD", "Asset Type": "Fixed Deposit",
     "Quantity": 1, "Purchase Price": 200000, "Current Value": 212000},
]

NET_WORTH_ROWS: list[dict[str, object]] = [
    {"Date": date(2026, 7, 1), "Item": "Savings Account", "Type": "Asset",
     "Category": "Bank Account", "Value": 165000},
    {"Date": date(2026, 7, 1), "Item": "Mutual Funds & Stocks", "Type": "Asset",
     "Category": "Investment", "Value": 74000},
    {"Date": date(2026, 7, 1), "Item": "PPF + FD", "Type": "Asset",
     "Category": "Investment", "Value": 372000},
    {"Date": date(2026, 7, 1), "Item": "Car", "Type": "Asset",
     "Category": "Vehicle", "Value": 460000},
    {"Date": date(2026, 7, 1), "Item": "Home Loan", "Type": "Liability",
     "Category": "Loan", "Value": 2210000},
    {"Date": date(2026, 7, 1), "Item": "Credit Card Outstanding", "Type": "Liability",
     "Category": "Credit Card", "Value": 8000},
    {"Date": date(2026, 8, 1), "Item": "Savings Account", "Type": "Asset",
     "Category": "Bank Account", "Value": 180000},
    {"Date": date(2026, 8, 1), "Item": "Mutual Funds & Stocks", "Type": "Asset",
     "Category": "Investment", "Value": 78500},
    {"Date": date(2026, 8, 1), "Item": "PPF + FD", "Type": "Asset",
     "Category": "Investment", "Value": 377000},
    {"Date": date(2026, 8, 1), "Item": "Car", "Type": "Asset",
     "Category": "Vehicle", "Value": 450000},
    {"Date": date(2026, 8, 1), "Item": "Home Loan", "Type": "Liability",
     "Category": "Loan", "Value": 2200000},
    {"Date": date(2026, 8, 1), "Item": "Credit Card Outstanding", "Type": "Liability",
     "Category": "Credit Card", "Value": 15000},
]

GOALS_ROWS: list[dict[str, object]] = [
    {"Goal": "Emergency Fund", "Target Amount": 300000, "Current Amount": 212000,
     "Target Date": date(2026, 12, 31)},
    {"Goal": "Goa Vacation", "Target Amount": 80000, "Current Amount": 35000,
     "Target Date": date(2026, 11, 1)},
    {"Goal": "New Laptop", "Target Amount": 120000, "Current Amount": 120000,
     "Target Date": date(2026, 6, 1)},
]
