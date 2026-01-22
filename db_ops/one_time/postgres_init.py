from sqlalchemy import create_engine, text

def main():
    engine = create_engine('postgresql+psycopg2://kekoa:goatez@localhost:5433/dodgers_pitching')

    sql = """
        CREATE SCHEMA IF NOT EXISTS raw;
        CREATE SCHEMA IF NOT EXISTS staging;
        CREATE SCHEMA IF NOT EXISTS production;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

if __name__ == "__main__":
    main()