import sqlite3
import os

class SQLAdapter:
    def __init__(self, connection_string):
        """
        Initializes the SQL Adapter.
        Expects connection_string format: "sqlite:///path/to/db"
        """
        self.db_path = connection_string.replace("sqlite:///", "")
        
    def fetch_data(self, table_name, fields=None):
        """
        Fetches data from the specified table.
        If fields are provided, constructs a specific SELECT query.
        Otherwise, selects all columns.
        """
        if not os.path.exists(self.db_path):
             return {"error": f"Database file not found: {self.db_path}"}

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row # To access columns by name
            cursor = conn.cursor()
            
            if fields:
                # Sanitize fields to prevent injection (basic)
                safe_fields = [f.strip() for f in fields if f.isalnum() or f == "*"]
                fields_str = ", ".join(safe_fields)
            else:
                fields_str = "*"
                
            query = f"SELECT {fields_str} FROM {table_name}"
            cursor.execute(query)
            
            rows = cursor.fetchall()
            
            # Convert rows to list of dicts
            result = [dict(row) for row in rows]
            
            conn.close()
            return result
            
        except Exception as e:
            return {"error": str(e)}
