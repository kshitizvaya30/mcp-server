from fastmcp import FastMCP
import os
import psycopg

DB_PATH = os.path.join(os.path.dirname(__file__), "expenseTracker.db")

mcp = FastMCP("Expense Tracker")
 
def initialize_database():
    with conn.connection() as connection:
        connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses 
            (id SERIAL PRIMARY KEY, description TEXT,
            category TEXT NOT NULL, 
            subcategory TEXT NOT NULL,
            note TEXT DEFAULT '', 
            amount DECIMAL(10, 2) NOT NULL, 
            date DATE NOT NULL);
        """) 
        connection.commit()
    print("Database initialized successfully")


initialize_database()


# // Add a new expense to the database 
@mcp.tool
def add_expense(description: str, category: str, subcategory: str, note: str, amount: float, date: str):
    with conn.connection() as connection:
        connection.execute("INSERT INTO expenses (description, category, subcategory, note, amount, date) VALUES (%s, %s, %s, %s, %s, %s)", (description, category, subcategory, note, amount, date))
        connection.commit()
    print("Expense added successfully")


@mcp.tool
# // Get all expenses from the database
def get_all_expenses():
    with conn.connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM expenses")
        return cursor.fetchall()
    print("All expenses fetched successfully")

@mcp.tool
def get_expense_by_id(id: int):
    with conn.connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = %s", (id,))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]    
    print("Expense fetched successfully")
    

mcp.run()


conn = psycopg.connect(
    host="admin",
    port=5432,
    dbname="expenseTracker",
    user="postgres",
    password=""
)