"""
Strike zone heatmap visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from typing import Optional, Tuple, List
from .queries import DataFetcher
from .pitch_movement import PITCH_COLORS


class StrikeZonePlots:
    """Generate strike zone visualizations."""

    def __init__(self, data_fetcher: Optional[DataFetcher] = None):
        self.fetcher = data_fetcher or DataFetcher()

    def _draw_strike_zone(
        self,
        ax: plt.Axes,
        sz_top: float = 3.5,
        sz_bot: float = 1.5
    ):
        """Draw the strike zone rectangle on given axes."""
        # Strike zone (17 inches = 0.708 ft on each side)
        zone_width = 17 / 12 / 2  # Half width in feet
        zone = patches.Rectangle(
            (-zone_width, sz_bot),
            zone_width * 2,
            sz_top - sz_bot,
            linewidth=2,
            edgecolor='black',
            facecolor='none',
            zorder=10
        )
        ax.add_patch(zone)

        # Home plate
        plate_vertices = [
            (-zone_width, 0),
            (zone_width, 0),
            (zone_width, 0.1),
            (0, 0.25),
            (-zone_width, 0.1),
        ]
        plate = patches.Polygon(
            plate_vertices,
            closed=True,
            linewidth=1,
            edgecolor='black',
            facecolor='white',
            zorder=5
        )
        ax.add_patch(plate)

    def pitch_location_scatter(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        pitch_types: Optional[List[str]] = None,
        title: str = "Pitch Locations",
        figsize: Tuple[int, int] = (8, 10),
        ax: Optional[plt.Axes] = None
    ) -> plt.Figure:
        """
        Create scatter plot of pitch locations from catcher's view.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        if pitch_types:
            df = df[df['pitch_type'].isin(pitch_types)]

        df = df.dropna(subset=['plate_x', 'plate_z'])

        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.get_figure()

        # Get average strike zone dimensions
        avg_sz_top = df['sz_top'].mean() if 'sz_top' in df.columns else 3.5
        avg_sz_bot = df['sz_bot'].mean() if 'sz_bot' in df.columns else 1.5

        # Draw strike zone
        self._draw_strike_zone(ax, avg_sz_top, avg_sz_bot)

        # Plot pitches by type
        for pitch_type in df['pitch_type'].dropna().unique():
            pitch_df = df[df['pitch_type'] == pitch_type]
            color = PITCH_COLORS.get(pitch_type, '#808080')
            pitch_name = pitch_df['pitch_name'].iloc[0] if len(pitch_df) > 0 else pitch_type

            ax.scatter(
                pitch_df['plate_x'],
                pitch_df['plate_z'],
                c=color,
                alpha=0.5,
                s=30,
                label=f"{pitch_name} ({len(pitch_df)})",
                edgecolors='none'
            )

        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(0, 5)
        ax.set_aspect('equal')
        ax.set_xlabel('Horizontal Position (ft)', fontsize=12)
        ax.set_ylabel('Vertical Position (ft)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right', fontsize=9)

        # Add catcher's perspective label
        ax.text(0, -0.3, "Catcher's View", ha='center', fontsize=10, alpha=0.7)

        plt.tight_layout()
        return fig

    def location_heatmap(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        pitch_types: Optional[List[str]] = None,
        metric: str = 'count',
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (8, 10),
        bins: int = 20
    ) -> plt.Figure:
        """
        Create heatmap of pitch locations.

        Args:
            metric: 'count', 'whiff_rate', 'csw_rate', 'contact_rate'
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        if pitch_types:
            df = df[df['pitch_type'].isin(pitch_types)]

        df = df.dropna(subset=['plate_x', 'plate_z'])

        fig, ax = plt.subplots(figsize=figsize)

        # Get average strike zone
        avg_sz_top = df['sz_top'].mean() if 'sz_top' in df.columns else 3.5
        avg_sz_bot = df['sz_bot'].mean() if 'sz_bot' in df.columns else 1.5

        x_edges = np.linspace(-2, 2, bins + 1)
        y_edges = np.linspace(0, 5, bins + 1)

        if metric == 'count':
            heatmap, _, _ = np.histogram2d(df['plate_x'], df['plate_z'], bins=[x_edges, y_edges])
            cmap = 'YlOrRd'
            cbar_label = 'Pitch Count'
        else:
            # Calculate metric in each bin
            heatmap = np.zeros((bins, bins))
            metric_col = {
                'whiff_rate': 'is_whiff',
                'csw_rate': 'is_csw',
                'contact_rate': 'is_contact'
            }.get(metric, 'is_whiff')

            for i in range(bins):
                for j in range(bins):
                    mask = (
                        (df['plate_x'] >= x_edges[i]) &
                        (df['plate_x'] < x_edges[i + 1]) &
                        (df['plate_z'] >= y_edges[j]) &
                        (df['plate_z'] < y_edges[j + 1])
                    )
                    bin_data = df[mask]
                    if len(bin_data) >= 5:  # Minimum sample size
                        heatmap[i, j] = bin_data[metric_col].mean() * 100
                    else:
                        heatmap[i, j] = np.nan

            cmap = 'RdYlGn_r' if metric == 'contact_rate' else 'RdYlGn'
            cbar_label = f'{metric.replace("_", " ").title()} (%)'

        # Plot heatmap
        im = ax.imshow(
            heatmap.T,
            origin='lower',
            extent=[-2, 2, 0, 5],
            aspect='auto',
            cmap=cmap,
            alpha=0.8
        )

        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label(cbar_label, fontsize=11)

        # Draw strike zone on top
        self._draw_strike_zone(ax, avg_sz_top, avg_sz_bot)

        ax.set_xlim(-2, 2)
        ax.set_ylim(0, 5)
        ax.set_xlabel('Horizontal Position (ft)', fontsize=12)
        ax.set_ylabel('Vertical Position (ft)', fontsize=12)
        ax.set_title(title or f"Pitch Location {metric.replace('_', ' ').title()} Heatmap",
                     fontsize=14, fontweight='bold')

        plt.tight_layout()
        return fig

    def pitch_type_zones(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (16, 12)
    ) -> plt.Figure:
        """
        Create grid of pitch locations by pitch type.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        df = df.dropna(subset=['plate_x', 'plate_z', 'pitch_type'])
        pitch_types = df['pitch_type'].value_counts().head(6).index.tolist()

        n_cols = min(3, len(pitch_types))
        n_rows = (len(pitch_types) + n_cols - 1) // n_cols

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        axes = axes.flatten() if len(pitch_types) > 1 else [axes]

        avg_sz_top = df['sz_top'].mean() if 'sz_top' in df.columns else 3.5
        avg_sz_bot = df['sz_bot'].mean() if 'sz_bot' in df.columns else 1.5

        for idx, pitch_type in enumerate(pitch_types):
            ax = axes[idx]
            pitch_df = df[df['pitch_type'] == pitch_type]
            pitch_name = pitch_df['pitch_name'].iloc[0]
            color = PITCH_COLORS.get(pitch_type, '#808080')

            self._draw_strike_zone(ax, avg_sz_top, avg_sz_bot)

            ax.scatter(
                pitch_df['plate_x'],
                pitch_df['plate_z'],
                c=color,
                alpha=0.4,
                s=15,
                edgecolors='none'
            )

            # Add stats
            zone_rate = ((pitch_df['plate_x'].between(-0.83, 0.83)) &
                         (pitch_df['plate_z'].between(avg_sz_bot, avg_sz_top))).mean() * 100

            ax.set_xlim(-2.5, 2.5)
            ax.set_ylim(0, 5)
            ax.set_aspect('equal')
            ax.set_title(f"{pitch_name}\n(n={len(pitch_df)}, Zone: {zone_rate:.1f}%)",
                         fontsize=11, fontweight='bold')

        # Hide empty subplots
        for idx in range(len(pitch_types), len(axes)):
            axes[idx].set_visible(False)

        plt.suptitle("Pitch Locations by Pitch Type", fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig

    def zone_whiff_comparison(
        self,
        df: Optional[pd.DataFrame] = None,
        pitcher_id: Optional[int] = None,
        figsize: Tuple[int, int] = (16, 6)
    ) -> plt.Figure:
        """
        Side-by-side heatmaps: In-Zone Whiff vs Out-of-Zone (Chase) Whiff.
        """
        if df is None:
            df = self.fetcher.get_pitch_shape_data(pitcher_id=pitcher_id)

        df = df.dropna(subset=['plate_x', 'plate_z'])

        avg_sz_top = df['sz_top'].mean() if 'sz_top' in df.columns else 3.5
        avg_sz_bot = df['sz_bot'].mean() if 'sz_bot' in df.columns else 1.5

        # Determine in-zone
        df['in_zone'] = (
            df['plate_x'].between(-0.83, 0.83) &
            df['plate_z'].between(avg_sz_bot, avg_sz_top)
        )

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        bins = 15
        x_edges = np.linspace(-2, 2, bins + 1)
        y_edges = np.linspace(0, 5, bins + 1)

        for ax, zone_filter, title in [
            (ax1, True, "In-Zone Whiff Rate"),
            (ax2, False, "Out-of-Zone (Chase) Whiff Rate")
        ]:
            zone_df = df[df['in_zone'] == zone_filter]

            heatmap = np.zeros((bins, bins))
            for i in range(bins):
                for j in range(bins):
                    mask = (
                        (zone_df['plate_x'] >= x_edges[i]) &
                        (zone_df['plate_x'] < x_edges[i + 1]) &
                        (zone_df['plate_z'] >= y_edges[j]) &
                        (zone_df['plate_z'] < y_edges[j + 1])
                    )
                    bin_data = zone_df[mask]
                    if len(bin_data) >= 3:
                        heatmap[i, j] = bin_data['is_whiff'].mean() * 100
                    else:
                        heatmap[i, j] = np.nan

            im = ax.imshow(
                heatmap.T,
                origin='lower',
                extent=[-2, 2, 0, 5],
                aspect='auto',
                cmap='RdYlGn',
                alpha=0.8,
                vmin=0,
                vmax=50
            )

            self._draw_strike_zone(ax, avg_sz_top, avg_sz_bot)
            ax.set_xlim(-2, 2)
            ax.set_ylim(0, 5)
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xlabel('Horizontal Position (ft)')
            ax.set_ylabel('Vertical Position (ft)')

        cbar = fig.colorbar(im, ax=[ax1, ax2], shrink=0.8, pad=0.02)
        cbar.set_label('Whiff Rate (%)', fontsize=11)

        plt.tight_layout()
        return fig
