"""
Velocity and spin rate distribution visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
from .queries import DataFetcher
from .pitch_movement import PITCH_COLORS


class VelocitySpinPlots:
    """Generate velocity and spin rate visualizations."""

    def __init__(self, data_fetcher: Optional[DataFetcher] = None):
        self.fetcher = data_fetcher or DataFetcher()

    def velocity_distribution(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        pitch_types: Optional[List[str]] = None,
        title: str = "Velocity Distribution by Pitch Type",
        figsize: Tuple[int, int] = (12, 6)
    ) -> plt.Figure:
        """
        Create violin/box plots showing velocity distribution by pitch type.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        if pitch_types:
            df = df[df['pitch_type'].isin(pitch_types)]

        df = df.dropna(subset=['release_speed', 'pitch_type'])

        # Order pitch types by median velocity
        pitch_order = df.groupby('pitch_type')['release_speed'].median().sort_values(ascending=False).index

        fig, ax = plt.subplots(figsize=figsize)

        positions = range(len(pitch_order))
        for i, pitch_type in enumerate(pitch_order):
            data = df[df['pitch_type'] == pitch_type]['release_speed']
            color = PITCH_COLORS.get(pitch_type, '#808080')

            # Violin plot
            parts = ax.violinplot([data], positions=[i], showmeans=True, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor(color)
                pc.set_alpha(0.7)

            # Add pitch name label
            pitch_name = df[df['pitch_type'] == pitch_type]['pitch_name'].iloc[0]
            ax.annotate(
                f"{pitch_name}\n({len(data)})",
                xy=(i, data.min() - 2),
                ha='center',
                fontsize=9
            )

        ax.set_xticks(positions)
        ax.set_xticklabels(pitch_order)
        ax.set_xlabel('Pitch Type', fontsize=12)
        ax.set_ylabel('Velocity (mph)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return fig

    def spin_rate_distribution(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        title: str = "Spin Rate Distribution by Pitch Type",
        figsize: Tuple[int, int] = (12, 6)
    ) -> plt.Figure:
        """
        Create spin rate distribution plot by pitch type.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        df = df.dropna(subset=['release_spin_rate', 'pitch_type'])

        # Order by median spin rate
        pitch_order = df.groupby('pitch_type')['release_spin_rate'].median().sort_values(ascending=False).index

        fig, ax = plt.subplots(figsize=figsize)

        for i, pitch_type in enumerate(pitch_order):
            data = df[df['pitch_type'] == pitch_type]['release_spin_rate']
            color = PITCH_COLORS.get(pitch_type, '#808080')

            parts = ax.violinplot([data], positions=[i], showmeans=True, showmedians=True)
            for pc in parts['bodies']:
                pc.set_facecolor(color)
                pc.set_alpha(0.7)

            pitch_name = df[df['pitch_type'] == pitch_type]['pitch_name'].iloc[0]
            ax.annotate(f"{pitch_name}", xy=(i, data.min() - 100), ha='center', fontsize=9)

        ax.set_xticks(range(len(pitch_order)))
        ax.set_xticklabels(pitch_order)
        ax.set_xlabel('Pitch Type', fontsize=12)
        ax.set_ylabel('Spin Rate (RPM)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        return fig

    def velo_over_game(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        pitch_types: Optional[List[str]] = None,
        title: str = "Velocity Throughout Game",
        figsize: Tuple[int, int] = (14, 6)
    ) -> plt.Figure:
        """
        Show velocity trends throughout a game (by pitch number).
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        if pitch_types:
            df = df[df['pitch_type'].isin(pitch_types)]

        fig, ax = plt.subplots(figsize=figsize)

        # Group by pitch type
        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type].copy()
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0]

            # Rolling average
            pitch_df = pitch_df.sort_values('pitch_number')
            rolling_velo = pitch_df['release_speed'].rolling(window=10, min_periods=5).mean()

            ax.scatter(
                pitch_df['pitch_number'],
                pitch_df['release_speed'],
                c=color,
                alpha=0.3,
                s=15
            )
            ax.plot(
                pitch_df['pitch_number'],
                rolling_velo,
                c=color,
                linewidth=2,
                label=pitch_name
            )

        ax.set_xlabel('Pitch Number', fontsize=12)
        ax.set_ylabel('Velocity (mph)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def velo_spin_scatter(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        title: str = "Velocity vs Spin Rate",
        figsize: Tuple[int, int] = (12, 8)
    ) -> plt.Figure:
        """
        Scatter plot of velocity vs spin rate by pitch type.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        fig, ax = plt.subplots(figsize=figsize)

        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type]
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0] if len(pitch_df) > 0 else pitch_type

            ax.scatter(
                pitch_df['release_speed'],
                pitch_df['release_spin_rate'],
                c=color,
                alpha=0.4,
                s=25,
                label=pitch_name,
                edgecolors='none'
            )

        ax.set_xlabel('Velocity (mph)', fontsize=12)
        ax.set_ylabel('Spin Rate (RPM)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def pitch_metrics_summary(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (14, 10)
    ) -> plt.Figure:
        """
        Create a summary dashboard with velo, spin, and extension by pitch type.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # Velocity
        ax = axes[0, 0]
        pitch_summary = df.groupby('pitch_type').agg({
            'release_speed': ['mean', 'std'],
            'pitch_name': 'first'
        }).round(1)
        pitch_summary.columns = ['avg_velo', 'std_velo', 'name']
        pitch_summary = pitch_summary.sort_values('avg_velo', ascending=False)

        colors = [PITCH_COLORS.get(pt, '#808080') for pt in pitch_summary.index]
        bars = ax.barh(pitch_summary['name'], pitch_summary['avg_velo'], color=colors, alpha=0.8)
        ax.errorbar(
            pitch_summary['avg_velo'], pitch_summary['name'],
            xerr=pitch_summary['std_velo'], fmt='none', color='black', capsize=3
        )
        ax.set_xlabel('Average Velocity (mph)')
        ax.set_title('Velocity by Pitch Type', fontweight='bold')

        # Spin Rate
        ax = axes[0, 1]
        pitch_summary = df.groupby('pitch_type').agg({
            'release_spin_rate': ['mean', 'std'],
            'pitch_name': 'first'
        }).round(0)
        pitch_summary.columns = ['avg_spin', 'std_spin', 'name']
        pitch_summary = pitch_summary.sort_values('avg_spin', ascending=False)

        colors = [PITCH_COLORS.get(pt, '#808080') for pt in pitch_summary.index]
        ax.barh(pitch_summary['name'], pitch_summary['avg_spin'], color=colors, alpha=0.8)
        ax.errorbar(
            pitch_summary['avg_spin'], pitch_summary['name'],
            xerr=pitch_summary['std_spin'], fmt='none', color='black', capsize=3
        )
        ax.set_xlabel('Average Spin Rate (RPM)')
        ax.set_title('Spin Rate by Pitch Type', fontweight='bold')

        # Extension
        ax = axes[1, 0]
        pitch_summary = df.groupby('pitch_type').agg({
            'release_extension': ['mean', 'std'],
            'pitch_name': 'first'
        }).round(2)
        pitch_summary.columns = ['avg_ext', 'std_ext', 'name']
        pitch_summary = pitch_summary.sort_values('avg_ext', ascending=False)

        colors = [PITCH_COLORS.get(pt, '#808080') for pt in pitch_summary.index]
        ax.barh(pitch_summary['name'], pitch_summary['avg_ext'], color=colors, alpha=0.8)
        ax.set_xlabel('Average Extension (ft)')
        ax.set_title('Release Extension by Pitch Type', fontweight='bold')

        # Whiff Rate
        ax = axes[1, 1]
        pitch_summary = df.groupby('pitch_type').agg({
            'is_whiff': 'mean',
            'pitch_name': 'first'
        })
        pitch_summary.columns = ['whiff_rate', 'name']
        pitch_summary['whiff_rate'] = (pitch_summary['whiff_rate'] * 100).round(1)
        pitch_summary = pitch_summary.sort_values('whiff_rate', ascending=False)

        colors = [PITCH_COLORS.get(pt, '#808080') for pt in pitch_summary.index]
        ax.barh(pitch_summary['name'], pitch_summary['whiff_rate'], color=colors, alpha=0.8)
        ax.set_xlabel('Whiff Rate (%)')
        ax.set_title('Whiff Rate by Pitch Type', fontweight='bold')

        plt.suptitle('Pitch Metrics Summary', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig
