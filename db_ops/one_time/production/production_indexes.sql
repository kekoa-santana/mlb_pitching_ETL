CREATE INDEX IF NOT EXISTS idx_dim_game_date
    ON production.dim_game (game_date);

CREATE INDEX IF NOT EXISTS idx_fact_pitcher_game
    on production.fact_pa (pitcher_id, game_pk);

CREATE INDEX IF NOT EXISTS idx_fact_pa_game
    ON production.fact_pa (game_pk);

CREATE INDEX IF NOT EXISTS idx_fact_pitch_pa_id
    ON production.fact_pitch (pa_id);

CREATE INDEX IF NOT EXISTS idx_fact_pitch_pitcher_game
    ON production.fact_pitch (pitcher_id, game_pk);

CREATE INDEX IF NOT EXISTS idx_fact_pitch_game
    ON production.fact_pitch (game_pk);

CREATE INDEX IF NOT EXISTS idx_fact_pitch_type
    ON production.fact_pitch (pitch_type);

CREATE INDEX IF NOT EXISTS idx_sat_bb_type
    ON production.sat_batted_balls (bb_type);