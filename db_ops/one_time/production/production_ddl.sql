CREATE TABLE IF NOT EXISTS production.dim_game (
    game_pk     BIGINT PRIMARY KEY,
    game_date   DATE NOT NULL,
    game_type   TEXT,
    home_team   TEXT,
    away_team   TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS production.dim_player(
    player_id       BIGINT PRIMARY KEY,
    player_name     TEXT,
    p_throws        TEXT,
    stand           TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS production.fact_pa(
    pa_id   BIGSERIAL PRIMARY KEY,

    game_pk     BIGINT NOT NULL REFERENCES production.dim_game(game_pk),
    pitcher_id  BIGINT NOT NULL REFERENCES production.dim_player(player_id),
    batter_id   BIGINT NOT NULL REFERENCES production.dim_player(player_id),

    game_counter    INTEGER NOT NULL,

    pitcher_pa_number   INTEGER,
    times_through_order SMALLINT,

    balls       SMALLINT,
    strikes     SMALLINT,
    outs_when_up    SMALLINT,

    inning      INTEGER,
    inning_topbot   TEXT,

    events      TEXT,
    description TEXT,

    bat_score   SMALLINT,
    fld_score   SMALLINT,
    post_bat_score  SMALLINT,
    bat_score_diff  SMALLINT,

    created_at  TIMESTAMPTZ NULL DEFAULT NOW(),

    CONSTRAINT uq_fact_pa_natural UNIQUE(game_pk, game_counter)
);

CREATE TABLE IF NOT EXISTS production.fact_pitch (
    pitch_id    BIGSERIAL PRIMARY KEY,

    pa_id   BIGINT NOT NULL REFERENCES production.fact_pa(pa_id),
    
    game_pk     BIGINT NOT NULL REFERENCES production.dim_game(game_pk),
    pitcher_id  BIGINT NOT NULL REFERENCES production.dim_player(player_id),
    batter_id   BIGINT NOT NULL REFERENCES production.dim_player(player_id),

    game_counter    INTEGER NOT NULL,
    pitch_number    INTEGER NOT NULL,

    pitch_type  TEXT,
    pitch_name  TEXT,
    description TEXT,

    release_speed   REAL,
    effective_speed REAL,
    release_spin_rate   REAL,
    release_extension   REAL,
    spin_axis    REAL,

    pfx_x   REAL,
    pfx_z   REAL,

    zone    SMALLINT,
    plate_x REAL,
    plate_z REAL,

    balls   SMALLINT,
    strikes SMALLINT,
    outs_when_up    SMALLINT,
    bat_score_diff  SMALLINT,

    is_whiff    BOOLEAN,
    is_called_strike    BOOLEAN,
    is_bip  BOOLEAN,
    is_swing    BOOLEAN,
    is_foul     BOOLEAN,

    created_at  TIMESTAMPTZ NULL DEFAULT NOW(),

    CONSTRAINT uq_fact_pitch_natural UNIQUE (game_pk, game_counter, pitch_number)
);

CREATE TABLE IF NOT EXISTS production.sat_batted_balls (
    pitch_id    BIGINT PRIMARY KEY REFERENCES production.fact_pitch(pitch_id),

    bb_type     TEXT,
    events      TEXT,

    launch_speed    REAL,
    launch_angle    REAL,
    hit_distance_sc REAL,

    hc_x    REAL,
    hc_y    REAL,

    is_home_run BOOLEAN,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);