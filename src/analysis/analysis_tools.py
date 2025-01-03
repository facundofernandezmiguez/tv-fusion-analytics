"""
TV Fusion Analysis Tools.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Optional

from .. import utils
from ... import config

class FusionAnalyzer:
    """Analyzer for TV Fusion metrics and penetration data."""
    
    def __init__(self, release: str):
        """
        Initialize Fusion Analyzer.
        
        Args:
            release: Release number
        """
        self.release = release
        self.analysis_path = os.path.join(config.ANALYSIS_PATH, f'R{release}')
        
        # Load reference data
        self.market_codes = pd.read_csv(config.MARKET_CODES_FILE)
        self.categ_names = pd.read_csv(config.CATEGORY_NAMES_FILE)
        
        # Load metrics and penetration data
        self.metrics = pd.read_csv(os.path.join(self.analysis_path, config.METRICS_FILE))
        self.penetration = pd.read_csv(os.path.join(self.analysis_path, config.PENETRATIONS_FILE))
        
        # Preprocess data
        self._preprocess_data()
    
    def _preprocess_data(self) -> None:
        """Preprocess metrics and penetration data."""
        self.metrics = utils.add_market_names(self.metrics, self.market_codes)
        self.penetration = utils.add_market_names(self.penetration, self.market_codes)
    
    def create_metric_pivots(self) -> None:
        """Create pivot tables for metrics data."""
        # Process OutputEval metrics
        outputeval = self.metrics[self.metrics['sec_code'] == 'OutputEval'].copy()
        outputeval = utils.safe_numeric_conversion(outputeval, 'var_val')
        outputeval_pivot = utils.create_pivot_table(
            outputeval,
            index=['market name', 'market'],
            columns='var_name',
            values='var_val',
            round_digits=2
        )
        
        # Process CreateRecipFused metrics
        createrecip = self.metrics[self.metrics['sec_code'] == 'CreateRecipFused'].copy()
        createrecip = utils.safe_numeric_conversion(createrecip, 'var_val')
        createrecip_pivot = utils.create_pivot_table(
            createrecip,
            index=['market name', 'market'],
            columns='var_name',
            values='var_val',
            round_digits=2
        )
        
        # Export to Excel
        output_file = os.path.join(self.analysis_path, f'POV_Fusion_Metrics_Pivots_R{self.release}.xlsx')
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            # Raw metrics
            self.metrics.to_excel(writer, sheet_name='RawMetrics', index=False)
            
            # CreateRecipFused
            createrecip_pivot.to_excel(writer, sheet_name='CreateRecipFused', index=True)
            worksheet = writer.sheets['CreateRecipFused']
            
            column_formats = {
                'C': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'G': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'H': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'I': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']}
            }
            utils.apply_excel_formatting(worksheet, column_formats)
            
            # OutputEval
            outputeval_pivot.to_excel(writer, sheet_name='OutputEval', index=True)
            worksheet = writer.sheets['OutputEval']
            
            column_formats = {
                'C': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'G': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'H': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'I': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'J': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']}
            }
            utils.apply_excel_formatting(worksheet, column_formats)
    
    def create_penetration_pivots(self) -> None:
        """Create pivot tables for penetration data."""
        penetration_pivot = utils.create_pivot_table(
            self.penetration,
            index='market name',
            columns=['fused_var', 'fused_var_code'],
            values='prof_pop_recip',
            round_digits=0
        )
        
        # Add statistics
        penetration_pivot = utils.calculate_statistics(penetration_pivot)
        
        # Export to Excel
        output_file = os.path.join(self.analysis_path, f'POV_Fusion_Penetrations_Pivot_R{self.release}.xlsx')
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            self.penetration.to_excel(writer, sheet_name='Raw_Penetration', index=False)
            penetration_pivot.to_excel(writer, sheet_name='Pivot', index=True)
    
    def plot_evolution(
        self,
        releases: List[str],
        mean_threshold: float = config.MEAN_THRESHOLD,
        std_threshold: float = config.STD_THRESHOLD
    ) -> None:
        """
        Plot evolution of metrics across releases.
        
        Args:
            releases: List of release numbers to compare
            mean_threshold: Threshold for mean change significance
            std_threshold: Threshold for standard deviation change significance
        """
        # Load data from all releases
        dfs = []
        for rel in releases:
            filepath = os.path.join(config.ANALYSIS_PATH, f'R{rel}', config.PENETRATIONS_FILE)
            df = pd.read_csv(filepath)
            df['release'] = rel
            dfs.append(df)
        
        df_final = pd.concat(dfs)
        
        # Calculate statistics
        result = utils.create_pivot_table(
            df_final,
            index=['fused_var', 'fused_var_code'],
            columns='release',
            values='prof_pop_recip',
            aggfunc=['mean', 'std']
        )
        
        # Sort releases
        result = result.reindex(releases, axis=1, level=1)
        
        # Calculate changes
        result = result.assign(
            mean_change=result['mean'].diff(axis=1).iloc[:, 1],
            std_change=result['std'].diff(axis=1).iloc[:, 1]
        )
        
        # Categorize changes
        result = result.assign(
            change1=result['mean_change'].apply(
                lambda x: utils.categorize_change(x, mean_threshold)
            ),
            change2=result['std_change'].apply(
                lambda x: utils.categorize_change(
                    x,
                    std_threshold,
                    increase_label='more variation',
                    decrease_label='less variation'
                )
            )
        )
        
        # Create plots
        plt.figure(figsize=(15, 10))
        
        # Plot mean changes
        plt.subplot(2, 1, 1)
        sns.histplot(data=result['mean_change'].dropna(), bins=30)
        plt.title('Distribution of Mean Changes')
        plt.axvline(mean_threshold, color='r', linestyle='--', label=f'Threshold: {mean_threshold}')
        plt.axvline(-mean_threshold, color='r', linestyle='--')
        plt.legend()
        
        # Plot std changes
        plt.subplot(2, 1, 2)
        sns.histplot(data=result['std_change'].dropna(), bins=30)
        plt.title('Distribution of Standard Deviation Changes')
        plt.axvline(std_threshold, color='r', linestyle='--', label=f'Threshold: {std_threshold}')
        plt.axvline(-std_threshold, color='r', linestyle='--')
        plt.legend()
        
        # Save plot
        plt.tight_layout()
        plt.savefig(os.path.join(config.GRAPHS_PATH, 'evolution_analysis.pdf'))
        plt.close()
