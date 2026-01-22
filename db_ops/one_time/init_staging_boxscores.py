from sqlalchemy import text, create_engine
from utils.utils import build_db_url

engine = create_engine(build_db_url())

query = """
    CREATE TABLE IF NOT EXISTS staging.pitching_boxscores (
        game_pk                     BIGINT NOT NULL,
        pitcher_id                  BIGINT NOT NULL,
        team_id                     BIGINT NOT NULL,
        team_name                   VARCHAR(50),
        pitcher_name                VARCHAR(80),
        is_starter                  BOOLEAN,
        fly_outs                    SMALLINT,
        ground_outs                 SMALLINT,
        air_outs                    SMALLINT,
        runs                        SMALLINT,
        doubles                     SMALLINT,
        triples                     SMALLINT,
        home_runs                   SMALLINT,
        strike_outs                 SMALLINT,
        walks                       SMALLINT,
        intentional_walks           SMALLINT,
        hits                        SMALLINT,
        hit_by_pitch                SMALLINT,
        at_bats                     SMALLINT,
        caught_stealing             SMALLINT,
        stolen_bases                SMALLINT,
        stolen_base_pct             NUMERIC(1, 3),
        number_of_pitches           SMALLINT,
        innings_pitched             NUMERIC(4, 1),
        wins                        SMALLINT,
        losses                      SMALLINT,
        saves                       SMALLINT,
        save_opportunities          SMALLINT,
        holds                       SMALLINT,
        blown_saves                 SMALLINT,
        earned_runs                 SMALLINT,
        batters_faced               SMALLINT,
        outs                        SMALLINT,
        complete_game               BOOLEAN,
        shutout                     BOOLEAN,
        balls                       SMALLINT,
        strikes                     SMALLINT,
        strike_pct                  NUMERIC(1, 3),
        hit_batsmen                 SMALLINT,
        balks                       SMALLINT,
        wild_pitches                SMALLINT,
        pickoffs                    SMALLINT,
        rbi                         SMALLINT,
        games_finished              BOOLEAN,
        runs_scored_per_9           NUMERIC(4, 2),
        home_runs_per_9             NUMERIC(4, 2),
        inherited_runners           SMALLINT,
        inherited_runners_scored    SMALLINT,
        catchers_interference       SMALLINT,
        sac_bunts                   SMALLINT,
        sac_flies                   SMALLINT,
        passed_ball                 SMALLINT,
        pop_outs                    SMALLINT,
        line_outs                   SMALLINT,
        source                      VARCHAR(50),
        ingested_at                 timestamptz,
        load_id                     uuid,
        PRIMARY KEY (game_pk, pitcher_id, team_id)
    )
"""

def main():
    with engine.begin() as conn:
        conn.execute(text(query))

    
if __name__ == "__main__":
    main()