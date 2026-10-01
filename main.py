from fastmcp import FastMCP
import os
import psycopg

mcp = FastMCP("Expense Tracker")

_initialized = False


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "expenseTracker"),
        user=os.getenv("POSTGRES_USER", "apple"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )


def initialize_database():
    global _initialized
    if _initialized:
        return
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                description TEXT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                note TEXT DEFAULT '',
                amount DECIMAL(10, 2) NOT NULL,
                date DATE NOT NULL
            )
        """)
        connection.commit()
    _initialized = True


@mcp.tool
def add_expense(
    description: str,
    category: str,
    subcategory: str,
    note: str,
    amount: float,
    date: str,
):
    initialize_database()
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO expenses (description, category, subcategory, note, amount, date)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (description, category, subcategory, note, amount, date),
        )
        connection.commit()
    return "Expense added successfully"


@mcp.tool
def get_all_expenses():
    initialize_database()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM expenses")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


@mcp.tool
def get_expense_by_id(id: int):
    initialize_database()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM expenses WHERE id = %s", (id,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

@mcp.resource("info://server")
def server_info():
    return {
        "name": "Expense Tracker",
        "version": "1.0.0",
        "description": "A simple expense tracker",
        "author": "Apple",
        "license": "MIT",
        "tools": [
            {
                "name": "add_expense",
                "description": "Add a new expense",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "The description of the expense"
                        },
                        "category": {
                            "type": "string",
                            "description": "The category of the expense"
                        },
                        "subcategory": {
                            "type": "string",
                            "description": "The subcategory of the expense"
                        },
                        "note": {
                            "type": "string",
                            "description": "The note of the expense"
                        },
                        "amount": {
                            "type": "number",
                            "description": "The amount of the expense"
                        },
                        "date": {
                            "type": "string",
                            "description": "The date of the expense"
                        }
                    }
                }
            },
            {
                "name": "get_all_expenses",
                "description": "Get all expenses",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "The id of the expense"
                        }
                    }
                }
            },
            {
                "name": "get_expense_by_id",
                "description": "Get an expense by id",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "The id of the expense"
                        }   
                    }
                }
            }
        ]
    }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
