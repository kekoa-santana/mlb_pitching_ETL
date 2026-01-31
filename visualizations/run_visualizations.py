#!/usr/bin/env python3
"""
Main script for generating MLB pitching visualizations.

Usage:
    python run_visualizations.py --pitcher-id 592789 --output-dir ./charts
    python run_visualizations.py --all-pitchers --min-pitches 500
    python run_visualizations.py --league-wide
"""

import argparse
import logging
import os
from pathlib import Path

import matplotlib.pyplot as plt

from queries import DataFetcher
from pitch_movement import PitchMovementPlots
from velocity_spin import VelocitySpinPlots
from strike_zone import StrikeZonePlots
from batted_balls import BattedBallPlots
from pitch_profiles import PitchProfilePlots


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class VisualizationRunner:
    """Orchestrates visualization generation."""

    def __init__(self, output_dir: str = "./charts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.fetcher = DataFetcher()
        self.movement_plots = PitchMovementPlots(self.fetcher)
        self.velo_spin_plots = VelocitySpinPlots(self.fetcher)
        self.zone_plots = StrikeZonePlots(self.fetcher)
        self.batted_ball_plots = BattedBallPlots(self.fetcher)
        self.profile_plots = PitchProfilePlots(self.fetcher)

    def save_figure(self, fig: plt.Figure, name: str, subdir: str = ""):
        """Save figure to output directory."""
        if subdir:
            save_dir = self.output_dir / subdir
            save_dir.mkdir(parents=True, exist_ok=True)
        else:
            save_dir = self.output_dir

        filepath = save_dir / f"{name}.png"
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        logger.info(f"Saved: {filepath}")

    def generate_pitcher_report(self, pitcher_id: int, pitcher_name: str = None):
        """Generate full visualization report for a specific pitcher."""
        subdir = f"pitcher_{pitcher_id}"
        if pitcher_name:
            subdir = f"{pitcher_name.replace(' ', '_')}_{pitcher_id}"

        logger.info(f"Generating visualizations for pitcher {pitcher_id}...")

        # Fetch data once
        pitch_data = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)
        batted_ball_data = self.fetcher.get_batted_ball_data(pitcher_id=pitcher_id)
        profile_data = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        if pitch_data.empty:
            logger.warning(f"No pitch data found for pitcher {pitcher_id}")
            return

        # 1. Pitch Movement
        fig = self.movement_plots.movement_plot(
            df=pitch_data,
            title=f"Pitch Movement - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "movement_plot", subdir)

        fig = self.movement_plots.release_point_plot(
            df=pitch_data,
            title=f"Release Point - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "release_point", subdir)

        fig = self.movement_plots.movement_by_platoon(df=pitch_data)
        self.save_figure(fig, "movement_by_platoon", subdir)

        # 2. Velocity & Spin
        fig = self.velo_spin_plots.velocity_distribution(
            df=pitch_data,
            title=f"Velocity Distribution - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "velocity_distribution", subdir)

        fig = self.velo_spin_plots.spin_rate_distribution(
            df=pitch_data,
            title=f"Spin Rate Distribution - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "spin_distribution", subdir)

        fig = self.velo_spin_plots.velo_spin_scatter(
            df=pitch_data,
            title=f"Velocity vs Spin - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "velo_spin_scatter", subdir)

        fig = self.velo_spin_plots.pitch_metrics_summary(df=pitch_data)
        self.save_figure(fig, "pitch_metrics_summary", subdir)

        # 3. Strike Zone
        fig = self.zone_plots.pitch_location_scatter(
            df=pitch_data,
            title=f"Pitch Locations - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "pitch_locations", subdir)

        fig = self.zone_plots.location_heatmap(
            df=pitch_data,
            metric='count',
            title=f"Pitch Location Density - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "location_heatmap", subdir)

        fig = self.zone_plots.location_heatmap(
            df=pitch_data,
            metric='whiff_rate',
            title=f"Whiff Rate by Location - {pitcher_name or pitcher_id}"
        )
        self.save_figure(fig, "whiff_heatmap", subdir)

        fig = self.zone_plots.pitch_type_zones(df=pitch_data)
        self.save_figure(fig, "pitch_type_zones", subdir)

        # 4. Batted Balls
        if not batted_ball_data.empty:
            fig = self.batted_ball_plots.spray_chart(
                df=batted_ball_data,
                title=f"Spray Chart - {pitcher_name or pitcher_id}"
            )
            self.save_figure(fig, "spray_chart", subdir)

            fig = self.batted_ball_plots.exit_velo_launch_angle(
                df=batted_ball_data,
                title=f"Exit Velo vs Launch Angle - {pitcher_name or pitcher_id}"
            )
            self.save_figure(fig, "ev_la_scatter", subdir)

            fig = self.batted_ball_plots.batted_ball_outcomes(df=batted_ball_data)
            self.save_figure(fig, "batted_ball_dashboard", subdir)

            fig = self.batted_ball_plots.spray_by_pitch_type(df=batted_ball_data)
            self.save_figure(fig, "spray_by_pitch_type", subdir)

        # 5. Pitch Profiles
        if not profile_data.empty:
            fig = self.profile_plots.pitch_usage_pie(
                df=profile_data,
                title=f"Pitch Usage - {pitcher_name or pitcher_id}"
            )
            self.save_figure(fig, "pitch_usage", subdir)

            fig = self.profile_plots.pitch_arsenal_table(df=profile_data)
            self.save_figure(fig, "arsenal_table", subdir)

            fig = self.profile_plots.platoon_splits_comparison(df=profile_data)
            self.save_figure(fig, "platoon_splits", subdir)

            fig = self.profile_plots.whiff_rate_breakdown(df=profile_data)
            self.save_figure(fig, "whiff_breakdown", subdir)

            fig = self.profile_plots.radar_chart(df=profile_data)
            self.save_figure(fig, "radar_chart", subdir)

        logger.info(f"Completed visualizations for pitcher {pitcher_id}")

    def generate_league_wide_report(self):
        """Generate league-wide visualization summaries."""
        subdir = "league_wide"
        logger.info("Generating league-wide visualizations...")

        # League movement plot
        pitch_data = self.fetcher.get_pitch_shape_data(limit=100000)

        if not pitch_data.empty:
            fig = self.movement_plots.movement_plot(
                df=pitch_data,
                title="League-Wide Pitch Movement"
            )
            self.save_figure(fig, "league_movement", subdir)

            fig = self.zone_plots.location_heatmap(
                df=pitch_data,
                metric='count',
                title="League-Wide Pitch Location Density"
            )
            self.save_figure(fig, "league_location_heatmap", subdir)

        # League averages by pitch type
        league_avgs = self.fetcher.get_league_averages_by_pitch_type()
        if not league_avgs.empty:
            fig, ax = plt.subplots(figsize=(12, 8))

            pitch_types = league_avgs.sort_values('avg_velo', ascending=False)
            colors = ['#D22D49', '#FE9D00', '#933F2C', '#EEE716', '#00D1ED', '#1DBE3A', '#3BACAC', '#BE5FA0']

            ax.barh(
                pitch_types['pitch_name'],
                pitch_types['avg_velo'],
                color=colors[:len(pitch_types)],
                alpha=0.8
            )
            ax.set_xlabel('Average Velocity (mph)')
            ax.set_title('League Average Velocity by Pitch Type', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')

            self.save_figure(fig, "league_velo_by_pitch", subdir)

        logger.info("Completed league-wide visualizations")

    def generate_top_pitchers_report(self, min_pitches: int = 500, top_n: int = 10):
        """Generate reports for top pitchers by volume."""
        pitchers = self.fetcher.get_pitcher_list(min_pitches=min_pitches)

        if pitchers.empty:
            logger.warning("No pitchers found with sufficient data")
            return

        top_pitchers = pitchers.head(top_n)
        logger.info(f"Generating reports for top {len(top_pitchers)} pitchers...")

        for _, row in top_pitchers.iterrows():
            self.generate_pitcher_report(
                pitcher_id=row['pitcher_id'],
                pitcher_name=row['player_name']
            )


def main():
    parser = argparse.ArgumentParser(description='Generate MLB Pitching Visualizations')

    # Pitcher selection
    parser.add_argument('--pitcher-id', type=int, help='Generate report for specific pitcher ID')
    parser.add_argument('--pitcher-name', type=str, help='Pitcher name (for labeling)')
    parser.add_argument('--all-pitchers', action='store_true', help='Generate reports for all top pitchers')
    parser.add_argument('--league-wide', action='store_true', help='Generate league-wide visualizations')

    # Options
    parser.add_argument('--output-dir', type=str, default='./charts', help='Output directory for charts')
    parser.add_argument('--min-pitches', type=int, default=500, help='Minimum pitches for pitcher selection')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top pitchers to process')

    args = parser.parse_args()

    runner = VisualizationRunner(output_dir=args.output_dir)

    if args.pitcher_id:
        runner.generate_pitcher_report(
            pitcher_id=args.pitcher_id,
            pitcher_name=args.pitcher_name
        )
    elif args.all_pitchers:
        runner.generate_top_pitchers_report(
            min_pitches=args.min_pitches,
            top_n=args.top_n
        )
    elif args.league_wide:
        runner.generate_league_wide_report()
    else:
        # Default: generate league-wide and top 5 pitchers
        runner.generate_league_wide_report()
        runner.generate_top_pitchers_report(min_pitches=args.min_pitches, top_n=5)


if __name__ == "__main__":
    main()
