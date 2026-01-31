"""
Batted ball visualizations - spray charts, exit velocity, launch angle.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from typing import Optional, Tuple, List
from .queries import DataFetcher


# Exit velocity color scale (Baseball Savant style)
EV_CMAP = LinearSegmentedColormap.from_list(
    'ev_cmap',
    ['#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#fee08b', '#fdae61', '#f46d43', '#d53e4f'],
    N=256
)


class BattedBallPlots:
    """Generate batted ball visualizations."""

    def __init__(self, data_fetcher: Optional[DataFetcher] = None):
        self.fetcher = data_fetcher or DataFetcher()

    def _draw_field(self, ax: plt.Axes, show_distances: bool = True):
        """Draw a baseball field outline."""
        # Home plate at origin
        home_plate = patches.RegularPolygon(
            (0, 0), numVertices=5, radius=2,
            orientation=np.pi, facecolor='white', edgecolor='black', linewidth=1
        )
        ax.add_patch(home_plate)

        # Foul lines (approximately 330 ft = 100m at corners)
        ax.plot([0, -100], [0, 100], 'k-', linewidth=1.5, alpha=0.7)  # Left field line
        ax.plot([0, 100], [0, 100], 'k-', linewidth=1.5, alpha=0.7)   # Right field line

        # Outfield arc
        theta = np.linspace(-np.pi/4, np.pi/4 + np.pi/2, 100)
        for distance, label in [(90, '300ft'), (120, '400ft')]:
            x = distance * np.sin(theta)
            y = distance * np.cos(theta)
            ax.plot(x, y, 'k--', linewidth=0.5, alpha=0.4)
            if show_distances:
                ax.text(0, distance + 5, label, ha='center', fontsize=8, alpha=0.5)

        # Infield diamond
        infield_dist = 27.4  # 90ft in plot units
        diamond = patches.RegularPolygon(
            (0, infield_dist/np.sqrt(2)), numVertices=4, radius=infield_dist,
            orientation=np.pi/4, facecolor='none', edgecolor='brown',
            linewidth=1.5, alpha=0.5
        )
        ax.add_patch(diamond)

    def spray_chart(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        color_by: str = 'launch_speed',
        title: str = "Spray Chart",
        figsize: Tuple[int, int] = (10, 10),
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Create spray chart of batted balls.

        Args:
            color_by: 'launch_speed', 'xwoba', 'launch_angle', 'bb_type'
        """
        if df is None:
            df = self.fetcher.get_batted_ball_data(pitcher_id=pitcher_id)

        df = df.dropna(subset=['hc_x', 'hc_y'])

        # Convert hit coordinates to field coordinates
        # hc_x: 0-250 (125 = center), hc_y: 0-250 (0 = home plate area)
        df['field_x'] = df['hc_x'] - 125
        df['field_y'] = 200 - df['hc_y']  # Flip y-axis

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.get_figure()

        self._draw_field(ax)

        if color_by == 'bb_type':
            # Categorical coloring
            bb_colors = {
                'ground_ball': '#8B4513',
                'line_drive': '#228B22',
                'fly_ball': '#4169E1',
                'popup': '#9370DB'
            }
            for bb_type, color in bb_colors.items():
                bb_df = df[df['bb_type'] == bb_type]
                if len(bb_df) > 0:
                    ax.scatter(
                        bb_df['field_x'], bb_df['field_y'],
                        c=color, alpha=0.6, s=30,
                        label=bb_type.replace('_', ' ').title(),
                        edgecolors='none'
                    )
            ax.legend(loc='upper right')
        else:
            # Continuous coloring
            if color_by == 'launch_speed':
                vmin, vmax = 60, 115
                cmap = EV_CMAP
                cbar_label = 'Exit Velocity (mph)'
            elif color_by == 'xwoba':
                vmin, vmax = 0, 1.5
                cmap = 'RdYlGn'
                cbar_label = 'xwOBA'
            else:  # launch_angle
                vmin, vmax = -30, 60
                cmap = 'coolwarm'
                cbar_label = 'Launch Angle (°)'

            sc = ax.scatter(
                df['field_x'], df['field_y'],
                c=df[color_by], cmap=cmap,
                vmin=vmin, vmax=vmax,
                alpha=0.6, s=30, edgecolors='none'
            )
            cbar = plt.colorbar(sc, ax=ax, shrink=0.7)
            cbar.set_label(cbar_label, fontsize=11)

        ax.set_xlim(-150, 150)
        ax.set_ylim(-20, 180)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('off')

        plt.tight_layout()
        return fig

    def exit_velo_launch_angle(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        title: str = "Exit Velocity vs Launch Angle",
        figsize: Tuple[int, int] = (12, 8)
    ) -> plt.Figure:
        """
        Create scatter plot of exit velocity vs launch angle with outcome zones.
        """
        if df is None:
            df = self.fetcher.get_batted_ball_data(pitcher_id=pitcher_id)

        df = df.dropna(subset=['launch_speed', 'launch_angle'])

        fig, ax = plt.subplots(figsize=figsize)

        # Define quality zones
        # Sweet spot: 8-32 degrees LA, 95+ EV
        sweet_spot = patches.Rectangle(
            (8, 95), 24, 25,
            linewidth=2, edgecolor='green', facecolor='green',
            alpha=0.1, label='Sweet Spot Zone'
        )
        ax.add_patch(sweet_spot)

        # Barrel zone (Baseball Savant definition - simplified)
        barrel_x = [8, 32, 50, 50, 8]
        barrel_y = [98, 95, 98, 120, 120]
        ax.fill(barrel_x, barrel_y, alpha=0.1, color='red', label='Barrel Zone')

        # Color by xwOBA
        sc = ax.scatter(
            df['launch_angle'],
            df['launch_speed'],
            c=df['xwoba'],
            cmap='RdYlGn',
            vmin=0, vmax=1.5,
            alpha=0.5, s=25,
            edgecolors='none'
        )

        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label('xwOBA', fontsize=11)

        # Add reference lines
        ax.axhline(y=95, color='gray', linestyle='--', alpha=0.5, label='Hard Hit (95 mph)')
        ax.axvline(x=8, color='gray', linestyle=':', alpha=0.5)
        ax.axvline(x=32, color='gray', linestyle=':', alpha=0.5)

        ax.set_xlabel('Launch Angle (°)', fontsize=12)
        ax.set_ylabel('Exit Velocity (mph)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlim(-40, 80)
        ax.set_ylim(40, 120)
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def batted_ball_outcomes(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (14, 10)
    ) -> plt.Figure:
        """
        Create dashboard of batted ball outcomes.
        """
        if df is None:
            df = self.fetcher.get_batted_ball_data(pitcher_id=pitcher_id)

        fig, axes = plt.subplots(2, 2, figsize=figsize)

        # 1. Exit Velocity Distribution
        ax = axes[0, 0]
        df['launch_speed'].hist(ax=ax, bins=30, color='steelblue', edgecolor='white', alpha=0.7)
        ax.axvline(df['launch_speed'].mean(), color='red', linestyle='--', label=f"Mean: {df['launch_speed'].mean():.1f}")
        ax.axvline(95, color='green', linestyle='--', alpha=0.7, label='Hard Hit (95)')
        ax.set_xlabel('Exit Velocity (mph)')
        ax.set_ylabel('Count')
        ax.set_title('Exit Velocity Distribution', fontweight='bold')
        ax.legend()

        # 2. Launch Angle Distribution
        ax = axes[0, 1]
        df['launch_angle'].hist(ax=ax, bins=30, color='coral', edgecolor='white', alpha=0.7)
        ax.axvline(df['launch_angle'].mean(), color='red', linestyle='--', label=f"Mean: {df['launch_angle'].mean():.1f}")
        ax.axvspan(8, 32, alpha=0.2, color='green', label='Sweet Spot (8-32°)')
        ax.set_xlabel('Launch Angle (°)')
        ax.set_ylabel('Count')
        ax.set_title('Launch Angle Distribution', fontweight='bold')
        ax.legend()

        # 3. Batted Ball Type Breakdown
        ax = axes[1, 0]
        if 'la_band' in df.columns:
            bb_counts = df['la_band'].value_counts()
            colors = ['#8B4513', '#228B22', '#4169E1', '#9370DB']  # GB, LD, FB, PU
            order = ['GB', 'LD', 'FB', 'PU']
            bb_counts = bb_counts.reindex([o for o in order if o in bb_counts.index])
            ax.pie(bb_counts.values, labels=bb_counts.index, colors=colors[:len(bb_counts)],
                   autopct='%1.1f%%', startangle=90)
            ax.set_title('Batted Ball Type Distribution', fontweight='bold')

        # 4. Quality Metrics
        ax = axes[1, 1]
        metrics = {
            'Hard Hit %': (df['hard_hit'] == True).mean() * 100 if 'hard_hit' in df.columns else 0,
            'Sweet Spot %': (df['sweet_spot'] == True).mean() * 100 if 'sweet_spot' in df.columns else 0,
            'Barrel %': (df['ideal_contact'] == True).mean() * 100 if 'ideal_contact' in df.columns else 0,
            'Avg xwOBA': df['xwoba'].mean() if 'xwoba' in df.columns else 0,
            'Avg xBA': df['xba'].mean() if 'xba' in df.columns else 0,
        }

        bars = ax.barh(list(metrics.keys()), list(metrics.values()), color='steelblue', alpha=0.7)
        ax.set_xlabel('Value')
        ax.set_title('Quality of Contact Metrics', fontweight='bold')

        # Add value labels
        for bar, val in zip(bars, metrics.values()):
            fmt = f'{val:.3f}' if val < 1 else f'{val:.1f}%'
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    fmt, va='center', fontsize=10)

        plt.suptitle('Batted Ball Analysis Dashboard', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig

    def spray_by_pitch_type(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (16, 12)
    ) -> plt.Figure:
        """
        Create spray charts split by pitch type.
        """
        if df is None:
            df = self.fetcher.get_batted_ball_data(pitcher_id=pitcher_id)

        df = df.dropna(subset=['hc_x', 'hc_y', 'pitch_type'])

        # Get top pitch types with batted balls
        top_pitches = df['pitch_type'].value_counts().head(6).index.tolist()

        n_cols = min(3, len(top_pitches))
        n_rows = (len(top_pitches) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if len(top_pitches) > 1 else [axes]

        df['field_x'] = df['hc_x'] - 125
        df['field_y'] = 200 - df['hc_y']

        for idx, pitch_type in enumerate(top_pitches):
            ax = axes[idx]
            pitch_df = df[df['pitch_type'] == pitch_type]

            self._draw_field(ax, show_distances=False)

            sc = ax.scatter(
                pitch_df['field_x'], pitch_df['field_y'],
                c=pitch_df['launch_speed'], cmap=EV_CMAP,
                vmin=60, vmax=115,
                alpha=0.6, s=25, edgecolors='none'
            )

            # Stats
            hard_hit_pct = (pitch_df['hard_hit'] == True).mean() * 100 if 'hard_hit' in pitch_df.columns else 0
            avg_ev = pitch_df['launch_speed'].mean()

            ax.set_xlim(-150, 150)
            ax.set_ylim(-20, 180)
            ax.set_aspect('equal')
            ax.set_title(f"{pitch_type}\n(n={len(pitch_df)}, Avg EV: {avg_ev:.1f}, HH%: {hard_hit_pct:.1f})",
                         fontsize=11, fontweight='bold')
            ax.axis('off')

        # Hide empty subplots
        for idx in range(len(top_pitches), len(axes)):
            axes[idx].set_visible(False)

        # Add colorbar
        cbar = fig.colorbar(sc, ax=axes, shrink=0.6, pad=0.02)
        cbar.set_label('Exit Velocity (mph)', fontsize=11)

        plt.suptitle('Spray Charts by Pitch Type', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig
