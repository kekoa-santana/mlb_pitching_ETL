INSERT INTO production.dim_game (game_pk, game_date, game_type, home_team, away_team)
SELECT DISTINCT
    game_pk,
    game_date::date,
    game_type,
    home_team,
    away_team
FROM staging.statcast_pitches
WHERE game_pk IS NOT NULL
ON CONFLICT(game_pk) DO UPDATE
SET game_date = EXCLUDED.game_date,
    game_type = COALESCE(EXCLUDED.game_type, production.dim_game.game_type),
    home_team = COALESCE(EXCLUDED.home_team, production.dim_game.home_team),
    away_team = COALESCE(EXCLUDED.away_team, production.dim_game.away_team);


INSERT INTO production.dim_player (player_id, player_name, p_throws, stand)
SELECT DISTINCT pitcher AS player_id, 
    NULL::text AS player_name,
    p_throws,
    stand
FROM staging.statcast_pitches
WHERE pitcher IS NOT NULL
UNION
SELECT DISTINCT batter AS player_id, 
    NULL::text AS player_name,
    p_throws,
    stand
FROM staging.statcast_pitches
WHERE batter IS NOT NULL
ON CONFLICT (player_id) DO NOTHING;