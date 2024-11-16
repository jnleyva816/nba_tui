import sqlite3

def read_database():
    """
    Reads and displays the contents of the SQLite database.

    Returns:
        dict: A dictionary containing the data from the 'state' and 'urls' tables.
    """
    data = {
        "state": [],
        "urls": []
    }
    try:
        conn = sqlite3.connect("url_generator.db")
        cursor = conn.cursor()

        # Read from the 'state' table
        cursor.execute("SELECT * FROM state ORDER BY id DESC")
        data["state"] = cursor.fetchall()

        # Read from the 'urls' table
        cursor.execute("SELECT * FROM urls ORDER BY id DESC")
        data["urls"] = cursor.fetchall()

        conn.close()
        return data

    except sqlite3.Error as e:
        print(f"Error reading from the database: {e}")
        return data


def main():
    # Read data from the database
    db_data = read_database()

    # Display state table data
    print("\nState Table:")
    for row in db_data["state"]:
        print(row)

    # Display URLs table data
    print("\nURLs Table:")
    for row in db_data["urls"]:
        print(row)

if __name__ == "__main__":
    main()
