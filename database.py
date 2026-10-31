
import sqlite3
import pandas as pd

DB_NAME = "merchantmind.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                Day TEXT,
                Revenue REAL,
                Orders REAL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                Product TEXT,
                Stock REAL,
                "Minimum Stock" REAL
            )
        """)


def save_data(df, table_name):
    if table_name not in ["sales", "inventory"]:
        raise ValueError("Invalid table name")

    with sqlite3.connect(DB_NAME) as conn:
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )


def load_data(table_name):
    if table_name not in ["sales", "inventory"]:
        raise ValueError("Invalid table name")

    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            f"SELECT * FROM {table_name}",
            conn
        )


def clear_data(table_name):
    if table_name not in ["sales", "inventory"]:
        raise ValueError("Invalid table name")

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(f"DELETE FROM {table_name}")
