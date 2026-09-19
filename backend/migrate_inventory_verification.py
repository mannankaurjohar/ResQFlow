from sqlalchemy import text
from app.database import engine


def column_exists(connection, table_name, column_name):
    result = connection.execute(
        text(f"PRAGMA table_info({table_name})")
    )

    columns = result.fetchall()

    return any(
        column[1] == column_name
        for column in columns
    )


def add_column(connection, column_name, definition):
    if not column_exists(
        connection,
        "inventory",
        column_name
    ):
        connection.execute(
            text(
                f"ALTER TABLE inventory "
                f"ADD COLUMN {column_name} {definition}"
            )
        )
        print(f"Added column: {column_name}")
    else:
        print(f"Already exists: {column_name}")


with engine.begin() as connection:

    add_column(
        connection,
        "verification_status",
        "VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN'"
    )

    add_column(
        connection,
        "verification_source",
        "VARCHAR(255)"
    )

    add_column(
        connection,
        "verified_by_id",
        "INTEGER"
    )

    add_column(
        connection,
        "verified_at",
        "DATETIME"
    )

    print()
    print("Inventory verification migration complete.")