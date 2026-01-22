from sqlalchemy import create_engine, text
from utils.utils import build_db_url

engine = create_engine(build_db_url(), pool_pre_ping=False)

query = """
    CREATE TABLE IF NOT EXISTS raw.landing_statcast_files (
        run_id          uuid            PRIMARY KEY DEFAULT gen_random_uuid(),
        pulled_at       timestamptz     NOT NULL DEFAULT now(),
        start_date      date            NOT NULL,
        end_date        date            NOT NULL,
        row_count       int             NOT NULL,
        schema_hash     text            NOT NULL,
        file_path       text            NOT NULL,
        query_params    jsonb           NOT NULL
    );
"""



def main():
    with engine.begin() as conn:
        conn.execute(text(query))


if __name__ == "__main__":
    main()