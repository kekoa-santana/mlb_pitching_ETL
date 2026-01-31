"""
SQL queries and data fetching utilities for visualizations.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
_PARENT_DIR = Path(__file__).resolve().parent.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

from utils.utils import build_db_url


class DataFetcher:
    """Fetches data from production views for visualizations."""

    def __init__(self, engine=None):
        if engine is None:
            self.engine = create_engine(build_db_url())
        else:
            self.engine = engine

    def get_pitch_shape_data(
        self,
        pitcher_id: Optional[int] = None,
        pitch_types: Optional[list] = None,
        limit: int = 50000
    ) -> pd.DataFrame:
        """
        Fetch pitch shape features for movement and release point analysis.
        """
        query = """
        SELECT
            pitch_id, pitcher_id, batter_id, pitch_type, pitch_name,
            pitcher_throws, batter_stand, platoon,
            release_speed, release_spin_rate, release_extension,
            release_pos_x, release_pos_z,
            horizontal_break_inches, induced_vertical_break_inches,
            movement_mag_inches, movement_per_1000rpm,
            plate_x, plate_z, sz_top, sz_bot,
            is_swing, is_whiff, is_csw, is_contact, is_bip
        FROM production.v_pitch_shape_features
        WHERE pitch_type IS NOT NULL
        """

        params = {}
        if pitcher_id:
            query += " AND pitcher_id = :pitcher_id"
            params['pitcher_id'] = pitcher_id
        if pitch_types:
            query += " AND pitch_type = ANY(:pitch_types)"
            params['pitch_types'] = pitch_types

        query += f" LIMIT {limit}"

        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_game_level_profiles(
        self,
        pitcher_id: Optional[int] = None,
        game_pk: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch game-level pitch type profiles.
        """
        query = """
        SELECT
            game_pk, pitcher_id, pitch_type, pitch_name, batter_stand,
            pitches, usage_pct, total_pitches,
            avg_move_in, avg_ivb_in,
            swing_rate, whiff_rate, csw_pct, bat_contact_rate,
            avg_xwoba_on_bip, hard_hit_rate_on_bip
        FROM production.v_game_level_pitch_type_profile
        WHERE pitch_type IS NOT NULL
        """

        params = {}
        if pitcher_id:
            query += " AND pitcher_id = :pitcher_id"
            params['pitcher_id'] = pitcher_id
        if game_pk:
            query += " AND game_pk = :game_pk"
            params['game_pk'] = game_pk

        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_pitch_type_profiles(
        self,
        pitcher_id: Optional[int] = None,
        min_pitches: int = 50
    ) -> pd.DataFrame:
        """
        Fetch season/career-level pitch type profiles.
        """
        query = """
        SELECT
            pitcher_id, pitch_type, pitch_name, platoon,
            pitches, usage_pct,
            avg_velo, avg_spin, avg_extension,
            avg_hb_in, avg_ivb_in, avg_movement_in,
            avg_release_side, avg_release_height,
            swing_rate, whiff_rate, csw_rate, contact_rate,
            zone_rate, chase_rate,
            zone_whiff_per_zone_swing, chase_whiff_per_chase_swing,
            hard_hit_rate, avg_xwoba_on_bip
        FROM production.v_pitch_type_profile
        WHERE pitch_type IS NOT NULL
          AND pitches >= :min_pitches
        """

        params = {'min_pitches': min_pitches}
        if pitcher_id:
            query += " AND pitcher_id = :pitcher_id"
            params['pitcher_id'] = pitcher_id

        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_batted_ball_data(
        self,
        pitcher_id: Optional[int] = None,
        limit: int = 50000
    ) -> pd.DataFrame:
        """
        Fetch batted ball data for spray charts and exit velocity analysis.
        """
        query = """
        SELECT
            bb.pitch_id, bb.pa_id, bb.bb_type, bb.events,
            bb.launch_speed, bb.launch_angle, bb.hit_distance_sc,
            bb.hc_x, bb.hc_y, bb.hc_x_centered,
            bb.xba, bb.xslg, bb.xwoba,
            bb.hard_hit, bb.sweet_spot, bb.ideal_contact,
            bb.la_band, bb.ev_band, bb.spray_bucket,
            p.pitcher_id, p.batter_id, p.pitch_type
        FROM production.sat_batted_balls bb
        JOIN production.fact_pitch p ON bb.pitch_id = p.pitch_id
        WHERE bb.launch_speed IS NOT NULL
        """

        params = {}
        if pitcher_id:
            query += " AND p.pitcher_id = :pitcher_id"
            params['pitcher_id'] = pitcher_id

        query += f" LIMIT {limit}"

        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params=params)

    def get_pitcher_list(self, min_pitches: int = 100) -> pd.DataFrame:
        """
        Get list of pitchers with sufficient data.
        """
        query = """
        SELECT
            p.pitcher_id,
            dp.player_name,
            dp.pitch_hand as throws,
            COUNT(*) as total_pitches
        FROM production.fact_pitch p
        JOIN production.dim_player dp ON p.pitcher_id = dp.player_id
        GROUP BY p.pitcher_id, dp.player_name, dp.pitch_hand
        HAVING COUNT(*) >= :min_pitches
        ORDER BY total_pitches DESC
        """

        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn, params={'min_pitches': min_pitches})

    def get_league_averages_by_pitch_type(self) -> pd.DataFrame:
        """
        Get league average metrics by pitch type for comparison.
        """
        query = """
        SELECT
            pitch_type,
            pitch_name,
            COUNT(*) as pitches,
            AVG(release_speed) as avg_velo,
            AVG(release_spin_rate) as avg_spin,
            AVG(horizontal_break_inches) as avg_hb,
            AVG(induced_vertical_break_inches) as avg_ivb,
            AVG(is_whiff::int) as whiff_rate,
            AVG(is_csw::int) as csw_rate
        FROM production.v_pitch_shape_features
        WHERE pitch_type IS NOT NULL
        GROUP BY pitch_type, pitch_name
        HAVING COUNT(*) >= 1000
        ORDER BY pitches DESC
        """

        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn)
