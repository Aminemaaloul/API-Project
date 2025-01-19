import os
import sqlite3

# Define the path to the database
db_path = os.path.join('instance', 'flights.db')

# Connect to your SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Step 1: Delete all data from the claims table
    cursor.execute("DELETE FROM claims")

    # Step 2: Commit the changes
    conn.commit()
    print("All data in the claims table has been deleted, but the table structure remains.")

except sqlite3.Error as e:
    # Handle any errors that occur during the operation
    print(f"An error occurred: {e}")

finally:
    # Step 3: Close the connection
    conn.close()