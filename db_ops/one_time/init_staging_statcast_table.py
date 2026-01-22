from sqlalchemy import create_engine, text
from utils.utils import build_db_url

statcast_pitches_query = """
    CREATE TABLE IF NOT EXISTS staging.statcast_pitches (
        game_pk                             BIGINT          NOT NULL,
        pitcher_id                          BIGINT          NOT NULL,
        batter_id                           BIGINT          NOT NULL,
        pitch_number                        SMALLINT        NOT NULL,
        pitch_type                          VARCHAR(5),
        at_bat_number                       SMALLINT,
        pitch_name                          VARCHAR(50),
        events                              VARCHAR(30),
        description                         VARCHAR(28),
        pitch_result_type                   VARCHAR(20),
        release_speed                       NUMERIC(4, 1),
        release_pos_x                       NUMERIC(3, 2),
        release_pos_y                       NUMERIC(3, 2),
        release_pos_z                       NUMERIC(3, 2),
        release_spin_rate                   NUMERIC(5, 1),
        release_extension                   NUMERIC(2, 1),
        spin_axis                           NUMERIC(4, 1),
        effective_speed                     NUMERIC(4, 1),
        pfx_x                               DOUBLE PRECISION,
        pfx_z                               DOUBLE PRECISION,
        vx0                                 DOUBLE PRECISION,
        vy0                                 DOUBLE PRECISION,
        vz0                                 DOUBLE PRECISION,
        ax                                  DOUBLE PRECISION,
        ay                                  DOUBLE PRECISION,
        az                                  DOUBLE PRECISION,
        zone                                SMALLINT,
        plate_x                             DOUBLE PRECISION,
        plate_z                             DOUBLE PRECISION,
        sz_top                              DOUBLE PRECISION,
        sz_bot                              DOUBLE PRECISION,
        p_throws                            CHAR(1),
        stand                               CHAR(1),
        balls                               SMALLINT,
        strikes                             SMALLINT,
        inning                              SMALLINT,
        on_3b                               BIGINT,
        on_2b                               BIGINT,
        on_1b                               BIGINT,
        outs_when_up                        SMALLINT,
        home_score                          SMALLINT,
        away_score                          SMALLINT,
        bat_score                           SMALLINT,
        fld_score                           SMALLINT,
        home_score_diff                     SMALLINT,
        bat_score_diff                      SMALLINT,
        if_fielding_alignment               VARCHAR(20),
        of_fielding_alignment               VARCHAR(20),
        is_bip                              BOOLEAN,
        is_whiff                            BOOLEAN,
        is_called_strike                    BOOLEAN,
        is_ball                             BOOLEAN,
        api_break_z_with_gravity            DOUBLE PRECISION,
        api_break_x_arm                     DOUBLE PRECISION,
        api_break_x_batter_in               DOUBLE PRECISION,
        arm_angle                           DOUBLE PRECISION,
        attack_angle                        DOUBLE PRECISION,
        attack_direction                    DOUBLE PRECISION,
        swing_path_tilt                     DOUBLE PRECISION,
        PRIMARY KEY (game_pk, at_bat_number, pitch_number)
    )
"""
statcast_batted_balls_query = """
    CREATE TABLE IF NOT EXISTS staging.statcast_batted_balls (
        game_pk                             BIGINT          NOT NULL,
        pitcher_id                          BIGINT          NOT NULL,
        batter_id                           BIGINT          NOT NULL,
        pitch_number                        SMALLINT        NOT NULL,
        pitch_type                          VARCHAR(5),
        at_bat_number                       SMALLINT,
        launch_speed                        NUMERIC(4, 1),
        launch_angle                        NUMERIC(3, 1),
        hit_distance_sc                     NUMERIC(4, 1),
        estimated_ba_using_speedangle       NUMERIC(4, 3),
        estimated_woba_using_speedangle     NUMERIC(4, 3),
        estimated_slg_using_speedangle      NUMERIC(4, 3),
        babip_value                         NUMERIC(4, 2),
        iso_value                           NUMERIC(4, 2),
        woba_value                          NUMERIC(4, 3),
        bb_type                             VARCHAR(15),
        hit_location                        SMALLINT,
        hc_x                                NUMERIC(5, 2),
        hc_y                                NUMERIC(5, 2),
        bat_speed                           NUMERIC(3, 1),
        swing_length                        NUMERIC(3, 1),
        hyper_speed                         NUMERIC(4, 1),
        if_fielding_alignment               VARCHAR(20),
        of_fielding_alignment               VARCHAR(20),
        PRIMARY KEY (game_pk, at_bat_number, pitch_number)
    )
"""

statcast_at_bats_query = """
    CREATE TABLE IF NOT EXISTS staging.statcast_at_bats (
        game_pk                             BIGINT          NOT NULL,
        at_bat_number                       SMALLINT        NOT NULL,
        pitcher_id                          BIGINT          NOT NULL,
        batter_id                           BIGINT          NOT NULL,
        inning                              SMALLINT,
        inning_topbot                       CHAR(3),
        events                              VARCHAR(30),
        rbi                                 SMALLINT,
        is_bip                              BOOLEAN,
        is_strikeout                        BOOLEAN,
        is_walk                             BOOLEAN,
        start_balls                         SMALLINT,
        start_strikes                       SMALLINT,
        PRIMARY KEY (game_pk, at_bat_number)
    )
"""

def main():
    engine = create_engine(build_db_url())

    with engine.begin() as conn:
        for query in [statcast_pitches_query, statcast_batted_balls_query, statcast_at_bats_query]:
            conn.execute(text(query))

if __name__ == "__main__":
    main()