query_users = f"""
        CREATE TABLE IF NOT EXISTS users (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TG_ID INT,
        TRELLO_API TEXT,
        TRELLO_TOKEN,
        STATUS TEXT,
        NAME TEXT
        )
        """

query_tables = f"""
        CREATE TABLE IF NOT EXISTS tables (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        TG_ID INT,
        TRELLO_BOARD_ID
        )
        """