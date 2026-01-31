"""
Pitch profile comparison and aggregate visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import Optional, Tuple, List
from .queries import DataFetcher
from .pitch_movement import PITCH_COLORS


class PitchProfilePlots:
    """Generate pitch profile comparison visualizations."""

    def __init__(self, data_fetcher: Optional[DataFetcher] = None):
        self.fetcher = data_fetcher or DataFetcher()

    def pitch_usage_pie(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        title: str = "Pitch Usage",
        figsize: Tuple[int, int] = (10, 8)
    ) -> plt.Figure:
        """
        Create pie chart of pitch usage.
        """
        if df is None:
            df = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        # Aggregate across platoon splits
        usage = df.groupby(['pitch_type', 'pitch_name']).agg({
            'pitches': 'sum'
        }).reset_index()
        usage['pct'] = usage['pitches'] / usage['pitches'].sum() * 100

        fig, ax = plt.subplots(figsize=figsize)

        colors = [PITCH_COLORS.get(pt, '#808080') for pt in usage['pitch_type']]

        wedges, texts, autotexts = ax.pie(
            usage['pct'],
            labels=usage['pitch_name'],
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.75,
            explode=[0.02] * len(usage)
        )

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        return fig

    def pitch_arsenal_table(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (14, 8)
    ) -> plt.Figure:
        """
        Create a styled table showing pitch arsenal metrics.
        """
        if df is None:
            df = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        # Aggregate metrics
        arsenal = df.groupby(['pitch_type', 'pitch_name']).agg({
            'pitches': 'sum',
            'avg_velo': 'mean',
            'avg_spin': 'mean',
            'avg_hb_in': 'mean',
            'avg_ivb_in': 'mean',
            'whiff_rate': 'mean',
            'csw_rate': 'mean',
            'chase_rate': 'mean',
            'hard_hit_rate': 'mean',
        }).reset_index()

        arsenal['usage_pct'] = arsenal['pitches'] / arsenal['pitches'].sum() * 100

        # Format for display
        display_df = pd.DataFrame({
            'Pitch': arsenal['pitch_name'],
            'Usage%': arsenal['usage_pct'].apply(lambda x: f"{x:.1f}%"),
            'Velo': arsenal['avg_velo'].apply(lambda x: f"{x:.1f}"),
            'Spin': arsenal['avg_spin'].apply(lambda x: f"{x:.0f}"),
            'HB (in)': arsenal['avg_hb_in'].apply(lambda x: f"{x:.1f}"),
            'IVB (in)': arsenal['avg_ivb_in'].apply(lambda x: f"{x:.1f}"),
            'Whiff%': (arsenal['whiff_rate'] * 100).apply(lambda x: f"{x:.1f}%"),
            'CSW%': (arsenal['csw_rate'] * 100).apply(lambda x: f"{x:.1f}%"),
            'Chase%': (arsenal['chase_rate'] * 100).apply(lambda x: f"{x:.1f}%"),
            'HH%': (arsenal['hard_hit_rate'] * 100).apply(lambda x: f"{x:.1f}%"),
        })

        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('off')

        # Create table
        table = ax.table(
            cellText=display_df.values,
            colLabels=display_df.columns,
            cellLoc='center',
            loc='center',
            colColours=['#4472C4'] * len(display_df.columns)
        )

        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.2, 1.8)

        # Color header text white
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(color='white', fontweight='bold')
            else:
                # Color code the pitch type column
                pitch_type = arsenal.iloc[row - 1]['pitch_type']
                if col == 0:
                    cell.set_facecolor(PITCH_COLORS.get(pitch_type, '#808080'))
                    cell.set_text_props(color='white', fontweight='bold')

        ax.set_title('Pitch Arsenal Summary', fontsize=16, fontweight='bold', y=0.95)

        plt.tight_layout()
        return fig

    def platoon_splits_comparison(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (14, 10)
    ) -> plt.Figure:
        """
        Compare pitch metrics by platoon split (same vs opposite hand).
        """
        if df is None:
            df = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        fig, axes = plt.subplots(2, 2, figsize=figsize)

        metrics = [
            ('whiff_rate', 'Whiff Rate', axes[0, 0]),
            ('csw_rate', 'CSW Rate', axes[0, 1]),
            ('chase_rate', 'Chase Rate', axes[1, 0]),
            ('hard_hit_rate', 'Hard Hit Rate Allowed', axes[1, 1]),
        ]

        pitch_types = df['pitch_type'].unique()
        x = np.arange(len(pitch_types))
        width = 0.35

        for metric, title, ax in metrics:
            same_vals = []
            oppo_vals = []

            for pt in pitch_types:
                pt_df = df[df['pitch_type'] == pt]
                same_data = pt_df[pt_df['platoon'] == 'same'][metric]
                oppo_data = pt_df[pt_df['platoon'] == 'opposite'][metric]

                same_vals.append(same_data.mean() * 100 if len(same_data) > 0 else 0)
                oppo_vals.append(oppo_data.mean() * 100 if len(oppo_data) > 0 else 0)

            bars1 = ax.bar(x - width/2, same_vals, width, label='Same Side', color='#4472C4', alpha=0.8)
            bars2 = ax.bar(x + width/2, oppo_vals, width, label='Opposite Side', color='#ED7D31', alpha=0.8)

            ax.set_xlabel('Pitch Type')
            ax.set_ylabel(f'{title} (%)')
            ax.set_title(title, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(pitch_types)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')

        plt.suptitle('Platoon Split Comparison', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig

    def whiff_rate_breakdown(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (12, 8)
    ) -> plt.Figure:
        """
        Stacked bar chart showing zone whiff vs chase whiff contribution.
        """
        if df is None:
            df = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        # Aggregate
        agg = df.groupby(['pitch_type', 'pitch_name']).agg({
            'pitches': 'sum',
            'whiff_rate': 'mean',
            'zone_rate': 'mean',
            'chase_rate': 'mean',
            'zone_whiff_per_zone_swing': 'mean',
            'chase_whiff_per_chase_swing': 'mean',
        }).reset_index()

        agg = agg.sort_values('whiff_rate', ascending=True)

        fig, ax = plt.subplots(figsize=figsize)

        y_pos = range(len(agg))

        # Calculate contributions (simplified)
        zone_whiff_contrib = agg['zone_whiff_per_zone_swing'].fillna(0) * agg['zone_rate'].fillna(0)
        chase_whiff_contrib = agg['chase_whiff_per_chase_swing'].fillna(0) * agg['chase_rate'].fillna(0)

        colors = [PITCH_COLORS.get(pt, '#808080') for pt in agg['pitch_type']]

        # Total whiff rate bar
        bars = ax.barh(y_pos, agg['whiff_rate'] * 100, color=colors, alpha=0.8, edgecolor='white')

        ax.set_yticks(y_pos)
        ax.set_yticklabels(agg['pitch_name'])
        ax.set_xlabel('Whiff Rate (%)', fontsize=12)
        ax.set_title('Whiff Rate by Pitch Type', fontsize=14, fontweight='bold')

        # Add value labels
        for bar, rate in zip(bars, agg['whiff_rate']):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{rate*100:.1f}%', va='center', fontsize=10)

        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        return fig

    def radar_chart(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        pitch_types: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (10, 10)
    ) -> plt.Figure:
        """
        Create radar chart comparing pitch types across multiple metrics.
        """
        if df is None:
            df = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        if pitch_types:
            df = df[df['pitch_type'].isin(pitch_types)]

        # Aggregate by pitch type
        agg = df.groupby(['pitch_type', 'pitch_name']).agg({
            'avg_velo': 'mean',
            'avg_spin': 'mean',
            'avg_movement_in': 'mean',
            'whiff_rate': 'mean',
            'csw_rate': 'mean',
            'chase_rate': 'mean',
        }).reset_index()

        # Normalize metrics to 0-100 scale
        metrics = ['avg_velo', 'avg_spin', 'avg_movement_in', 'whiff_rate', 'csw_rate', 'chase_rate']
        labels = ['Velocity', 'Spin Rate', 'Movement', 'Whiff%', 'CSW%', 'Chase%']

        for col in metrics:
            col_min, col_max = agg[col].min(), agg[col].max()
            if col_max > col_min:
                agg[f'{col}_norm'] = (agg[col] - col_min) / (col_max - col_min) * 100
            else:
                agg[f'{col}_norm'] = 50

        # Set up radar chart
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the loop

        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

        for _, row in agg.iterrows():
            values = [row[f'{m}_norm'] for m in metrics]
            values += values[:1]

            color = PITCH_COLORS.get(row['pitch_type'], '#808080')
            ax.plot(angles, values, 'o-', linewidth=2, color=color, label=row['pitch_name'])
            ax.fill(angles, values, alpha=0.15, color=color)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.set_title('Pitch Profile Radar Chart', fontsize=14, fontweight='bold', y=1.08)

        plt.tight_layout()
        return fig

    def game_by_game_trends(
        self,
        pitcher_id: Optional[int] = None,
        metric: str = 'whiff_rate',
        figsize: Tuple[int, int] = (14, 8)
    ) -> plt.Figure:
        """
        Show trends across games for a given metric.
        """
        df = self.fetcher.get_game_level_profiles(pitcher_id=pitcher_id)

        if df.empty:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
            return fig

        metric_labels = {
            'whiff_rate': 'Whiff Rate (%)',
            'csw_pct': 'CSW Rate (%)',
            'swing_rate': 'Swing Rate (%)',
            'hard_hit_rate_on_bip': 'Hard Hit Rate (%)',
        }

        fig, ax = plt.subplots(figsize=figsize)

        # Get games in order
        games = df['game_pk'].unique()

        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type]
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0]

            # Aggregate by game
            game_data = pitch_df.groupby('game_pk')[metric].mean()

            ax.plot(
                range(len(game_data)),
                game_data.values * 100,
                'o-',
                color=color,
                label=pitch_name,
                alpha=0.8,
                markersize=6
            )

        ax.set_xlabel('Game Number', fontsize=12)
        ax.set_ylabel(metric_labels.get(metric, metric), fontsize=12)
        ax.set_title(f'{metric_labels.get(metric, metric)} by Game', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def league_comparison(
        self,
        pitcher_id: int,
        figsize: Tuple[int, int] = (14, 10)
    ) -> plt.Figure:
        """
        Compare a pitcher's arsenal to league averages.
        """
        # Get pitcher data
        pitcher_df = self.fetcher.get_pitch_type_profiles(pitcher_id=pitcher_id)

        # Get league averages
        league_df = self.fetcher.get_league_averages_by_pitch_type()

        if pitcher_df.empty or league_df.empty:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, 'Insufficient data for comparison', ha='center', va='center')
            return fig

        # Aggregate pitcher data
        pitcher_agg = pitcher_df.groupby(['pitch_type', 'pitch_name']).agg({
            'avg_velo': 'mean',
            'avg_spin': 'mean',
            'avg_hb_in': 'mean',
            'avg_ivb_in': 'mean',
            'whiff_rate': 'mean',
            'csw_rate': 'mean',
        }).reset_index()

        fig, axes = plt.subplots(2, 3, figsize=figsize)
        axes = axes.flatten()

        metrics = [
            ('avg_velo', 'Velocity (mph)'),
            ('avg_spin', 'Spin Rate (RPM)'),
            ('avg_hb', 'Horizontal Break (in)'),
            ('avg_ivb', 'Induced Vertical Break (in)'),
            ('whiff_rate', 'Whiff Rate'),
            ('csw_rate', 'CSW Rate'),
        ]

        for idx, (metric, title) in enumerate(metrics):
            ax = axes[idx]

            pitch_types = pitcher_agg['pitch_type'].tolist()
            x = np.arange(len(pitch_types))
            width = 0.35

            # Get pitcher values
            pitcher_col = 'avg_hb_in' if metric == 'avg_hb' else ('avg_ivb_in' if metric == 'avg_ivb' else metric)
            pitcher_vals = pitcher_agg[pitcher_col].values
            if metric in ['whiff_rate', 'csw_rate']:
                pitcher_vals = pitcher_vals * 100

            # Get league values
            league_vals = []
            for pt in pitch_types:
                league_row = league_df[league_df['pitch_type'] == pt]
                if len(league_row) > 0:
                    val = league_row[metric].values[0]
                    if metric in ['whiff_rate', 'csw_rate']:
                        val = val * 100
                    league_vals.append(val)
                else:
                    league_vals.append(0)

            bars1 = ax.bar(x - width/2, pitcher_vals, width, label='Pitcher', color='#4472C4')
            bars2 = ax.bar(x + width/2, league_vals, width, label='League Avg', color='#A5A5A5')

            ax.set_ylabel(title)
            ax.set_title(title, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(pitch_types)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3, axis='y')

        plt.suptitle('Pitcher vs League Average Comparison', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig
