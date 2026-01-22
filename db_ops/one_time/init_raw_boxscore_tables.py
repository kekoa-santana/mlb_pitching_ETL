from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://kekoa:goatez@localhost:5433/dodgers_pitching")

raw_boxscores_init = """
    CREATE TABLE IF NOT EXISTS raw.pitching_boxscores (
        row_num                         int,
        pitcher_id                      bigint NOT NULL,
        pitcher_name                    text,
        team_id                         bigint NOT NULL,
        game_pk                         bigint NOT NULL,
        team_name                       text,
        is_starter_text                 text,
        fly_outs_text                   text,
        ground_outs_text                text,
        air_outs_text                   text,
        runs_text                       text,
        doubles_text                    text,
        triples_text                    text,
        home_runs_text                  text,
        strike_outs_text                text,
        walks_text                      text,
        intentional_walks_text          text,
        hits_text                       text,
        hit_by_pitch_text               text,
        at_bats_text                    text,
        caught_stealing_text            text,
        stolen_bases_text               text,
        stolen_base_percentage_text     text,
        number_of_pitches_text          text,
        innings_pitched_text            text,
        wins_text                       text,
        losses_text                     text,
        saves_text                      text,
        save_opportunities_text         text,
        holds_text                      text,
        blown_saves_text                text,
        earned_runs_text                text,
        batters_faced_text              text,
        outs_text                       text,
        complete_game_text              text,
        shutout_text                    text,
        pitches_thrown_text             text,
        balls_text                      text,
        strikes_text                    text,
        strike_percentage_text          text,
        hit_batsmen_text                text,
        balks_text                      text,
        wild_pitches_text               text,
        pickoffs_text                   text,
        rbi_text                        text,
        games_finished_text             text,
        runs_scored_per_9_text          text,
        home_runs_per_9_text            text,
        inherited_runners_text          text,
        inherited_runners_scored_text   text,
        catchers_interference_text      text,
        sac_bunts_text                  text,
        sac_flies_text                  text,
        passed_ball_text                text,
        pop_outs_text                   text,
        line_outs_text                  text,
        source                          text,
        load_id                         uuid DEFAULT gen_random_uuid(),
        ingested_at                     timestamptz DEFAULT now(),
        PRIMARY KEY (pitcher_id, team_id, game_pk)
    );
"""

landing_boxscores_init = """
    CREATE TABLE IF NOT EXISTS raw.landing_boxscores (
        load_id             uuid DEFAULT gen_random_uuid(),
        ingested_at         timestamptz DEFAULT now(),
        source              text NOT NULL,
        game_pk             bigint,
        payload             jsonb NOT NULL
    );
"""

def main():
    with engine.begin() as conn:
        conn.execute(text(raw_boxscores_init))
        conn.execute(text(landing_boxscores_init))

if __name__ == "__main__":
    main()