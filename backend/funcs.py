import sqlite3
import pandas as pd

def run_sql(db='test_db.db'):

    # Connect to the database
    with sqlite3.connect(db) as conn:

        # SQL query to join Customers and Sales
        query = """
        SELECT 
            s.sale_id,
            c.name AS customer_name,
            c.email,
            s.product,
            s.quantity,
            s.sale_date
        FROM Sales s
        JOIN Customers c ON s.customer_id = c.customer_id
        LIMIT 10
        """

        # Read query directly into a pandas DataFrame
        df = pd.read_sql_query(query, conn)

    return df

