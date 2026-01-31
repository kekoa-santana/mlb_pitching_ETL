"""
Pitch movement visualizations - break plots and movement profiles.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional, Tuple
from .queries import DataFetcher


# Standard pitch type colors (Baseball Savant style)
PITCH_COLORS = {
    'FF': '#D22D49',  # 4-Seam Fastball - Red
    'SI': '#FE9D00',  # Sinker - Orange
    'FC': '#933F2C',  # Cutter - Brown
    'SL': '#EEE716',  # Slider - Yellow
    'CU': '#00D1ED',  # Curveball - Cyan
    'KC': '#00D1ED',  # Knuckle Curve - Cyan
    'CH': '#1DBE3A',  # Changeup - Green
    'FS': '#3BACAC',  # Splitter - Teal
    'ST': '#BE5FA0',  # Sweeper - Pink
    'SV': '#BE5FA0',  # Slurve - Pink
    'KN': '#867A08',  # Knuckleball - Olive
}


class PitchMovementPlots:
    """Generate pitch movement visualizations."""

    def __init__(self, data_fetcher: Optional[DataFetcher] = None):
        self.fetcher = data_fetcher or DataFetcher()

    def movement_plot(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        title: str = "Pitch Movement Profile",
        figsize: Tuple[int, int] = (10, 10),
        show_legend: bool = True,
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Create a horizontal vs vertical break scatter plot.

        Args:
            df: DataFrame with pitch data (if None, fetches from database)
            pitcher_id: Filter to specific pitcher
            title: Plot title
            figsize: Figure size tuple
            show_legend: Whether to show pitch type legend
            ax: Existing axes to plot on

        Returns:
            matplotlib Figure
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.get_figure()

        # Plot each pitch type
        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type]
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0] if len(pitch_df) > 0 else pitch_type

            ax.scatter(
                pitch_df['horizontal_break_inches'],
                pitch_df['induced_vertical_break_inches'],
                c=color,
                alpha=0.5,
                s=30,
                label=f"{pitch_name} ({len(pitch_df)})",
                edgecolors='none'
            )

        # Add reference lines
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)

        # Labels and formatting
        ax.set_xlabel('Horizontal Break (inches)', fontsize=12)
        ax.set_ylabel('Induced Vertical Break (inches)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Set equal aspect and reasonable limits
        max_val = max(
            abs(df['horizontal_break_inches'].quantile(0.99)),
            abs(df['horizontal_break_inches'].quantile(0.01)),
            abs(df['induced_vertical_break_inches'].quantile(0.99)),
            abs(df['induced_vertical_break_inches'].quantile(0.01))
        ) + 5
        ax.set_xlim(-max_val, max_val)
        ax.set_ylim(-max_val, max_val)
        ax.set_aspect('equal')

        # Add arm-side reference
        ax.annotate('Arm Side', xy=(max_val - 3, -max_val + 2), fontsize=10, alpha=0.6)
        ax.annotate('Glove Side', xy=(-max_val + 1, -max_val + 2), fontsize=10, alpha=0.6)

        if show_legend:
            ax.legend(loc='upper right', fontsize=9)

        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return fig

    def movement_by_platoon(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (16, 8)
    ) -> plt.Figure:
        """
        Create side-by-side movement plots split by batter handedness.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # Same-side matchups
        same_df = df[df['platoon'] == 'same']
        self.movement_plot(df=same_df, ax=ax1, title="vs Same-Side Batters", show_legend=True)

        # Opposite-side matchups
        oppo_df = df[df['platoon'] == 'opposite']
        self.movement_plot(df=oppo_df, ax=ax2, title="vs Opposite-Side Batters", show_legend=True)

        plt.suptitle("Pitch Movement by Platoon Split", fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        return fig

    def release_point_plot(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        title: str = "Release Point",
        figsize: Tuple[int, int] = (8, 10),
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Create a release point visualization from catcher's perspective.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.get_figure()

        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type]
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0] if len(pitch_df) > 0 else pitch_type

            ax.scatter(
                pitch_df['release_pos_x'],
                pitch_df['release_pos_z'],
                c=color,
                alpha=0.4,
                s=20,
                label=f"{pitch_name}",
                edgecolors='none'
            )

        # Add rubber reference
        ax.axhline(y=0, color='brown', linewidth=4, alpha=0.7)
        ax.text(0, -0.3, 'Rubber', ha='center', fontsize=10, alpha=0.7)

        ax.set_xlabel('Horizontal Release Point (ft from center)', fontsize=12)
        ax.set_ylabel('Vertical Release Point (ft)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')

        ax.set_xlim(-4, 4)
        ax.set_ylim(0, 8)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def velo_movement_scatter(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        metric: str = 'induced_vertical_break_inches',
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8)
    ) -> plt.Figure:
        """
        Create velocity vs movement scatter plot.

        Args:
            metric: 'induced_vertical_break_inches', 'horizontal_break_inches', or 'movement_mag_inches'
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        fig, ax = plt.subplots(figsize=figsize)

        metric_labels = {
            'induced_vertical_break_inches': 'Induced Vertical Break (in)',
            'horizontal_break_inches': 'Horizontal Break (in)',
            'movement_mag_inches': 'Total Movement (in)'
        }

        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type]
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0] if len(pitch_df) > 0 else pitch_type

            ax.scatter(
                pitch_df['release_speed'],
                pitch_df[metric],
                c=color,
                alpha=0.4,
                s=25,
                label=f"{pitch_name}",
                edgecolors='none'
            )

        ax.set_xlabel('Velocity (mph)', fontsize=12)
        ax.set_ylabel(metric_labels.get(metric, metric), fontsize=12)
        ax.set_title(title or f"Velocity vs {metric_labels.get(metric, metric)}",
                     fontsize=14, fontweight='bold')

        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig
