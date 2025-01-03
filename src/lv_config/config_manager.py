"""
LV Configuration Manager for TV Fusion.
"""

import os
import shutil
import pandas as pd
import numpy as np
from typing import Optional

from .. import utils
from ... import config

class LVConfigManager:
    """Manages TV Fusion linking variable configurations."""
    
    def __init__(self, release: int):
        """
        Initialize LV Configuration Manager.
        
        Args:
            release: Release number
        """
        self.release = release
        self.lv_config_path = os.path.join(config.LV_CONFIG_PATH, f'R{release}')
        
        # Create release folder if missing
        if not os.path.exists(self.lv_config_path):
            os.makedirs(self.lv_config_path)
            
        # Load reference data
        self.dma_mapping = pd.read_csv(os.path.join(config.LV_REFERENCES_PATH, 'dma_mapping.csv'))
        
    def _copy_excel_templates(self) -> None:
        """Copy excel templates from References to release folder."""
        for mkt_type in config.MARKET_TYPES:
            file_name = f"LV_config Prod - {mkt_type}.xlsx"
            shutil.copy(
                os.path.join(config.LV_REFERENCES_PATH, file_name),
                os.path.join(self.lv_config_path, file_name)
            )
    
    def _load_fusion_files(self) -> None:
        """Load and preprocess fusion files."""
        fusion_file = os.path.join(self.lv_config_path, f'R{self.release} Files for Fusion2.xlsx')
        excel_file = pd.ExcelFile(fusion_file)
        
        self.stations = excel_file.parse("Scarborough network mappings")
        self.buckets = excel_file.parse("Scarborough network buckets map")
        
        # Rename columns
        self.buckets = self.buckets.rename(columns={
            'market': 'DMA_CODE',
            'Scarb_Network_Key': 'SCARB_KEY'
        })
        
        # Clean spaces from keys
        self.stations['SCARB_KEY'] = self.stations['SCARB_KEY'].str.replace(' ', '')
        self.buckets['SCARB_KEY'] = self.buckets['SCARB_KEY'].str.replace(' ', '')
    
    def _process_cable_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process cable data in DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with processed cable data
        """
        # Filter cable rows
        cable_rows = df[df["DMA_CODE"] == "Cable"]
        
        # Get unique DMA values
        unique_values = df["DMA_CODE"].unique()
        unique_values = unique_values[unique_values != "Cable"]
        
        # Duplicate cable rows
        cable_rows = cable_rows.loc[cable_rows.index.repeat(len(unique_values))]
        cable_rows["DMA_CODE"] = np.tile(unique_values, len(cable_rows) // len(unique_values))
        
        # Combine and filter
        df = pd.concat([df, cable_rows], ignore_index=True)
        df = df[df["DMA_CODE"].isin(self.dma_mapping["name"])]
        df = df.sort_values(by="DMA_CODE")
        
        # Merge with DMA mapping
        merged = pd.merge(df, self.dma_mapping, how='left', left_on='DMA_CODE', right_on='name')
        
        # Add required columns
        merged = merged.rename(columns={
            'dma': 'PROCESSING_DMA_CODE',
            'LV_NAME': 'LINKING_VARIABLE_NAME'
        })
        merged['IS_IN_CC'] = 'X'
        merged['TRIM_SIDE'] = 'E'
        merged['PCA_FLAG'] = 'Y'
        merged['SE_FLAG'] = 'Y'
        merged['OE_FLAG'] = 'Y'
        
        return merged
    
    def _process_hispanic_stations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process hispanic stations data.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with hispanic stations
        """
        hisp_codes = df['PROCESSING_DMA_CODE'].astype(str).str.len() == 4
        no_hisp_codes = df.loc[hisp_codes, 'PROCESSING_DMA_CODE'].astype(str).str[:-1]
        mask = df['PROCESSING_DMA_CODE'].astype(str).isin(no_hisp_codes)
        mask2 = df['CONFIG_CATEGORY'].isin(['TVNETW', 'BUCKETS'])
        mask3 = mask & mask2
        
        dup_rows = df.loc[mask3].copy()
        dup_rows['PROCESSING_DMA_CODE'] = dup_rows['PROCESSING_DMA_CODE'].astype(str) + '0'
        
        return pd.concat([df, dup_rows], ignore_index=True)
    
    def _create_qc_file(self, df: pd.DataFrame) -> None:
        """
        Create QC file with market statistics.
        
        Args:
            df: Input DataFrame
        """
        # Group by market and calculate statistics
        market_stats = df.groupby('PROCESSING_DMA_CODE').agg({
            'LINKING_VARIABLE_NAME': ['count', 'nunique']
        }).round(2)
        
        # Export to Excel
        output_file = os.path.join(self.lv_config_path, f'QC - TV Fusion R{self.release}.xlsx')
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            market_stats.to_excel(writer, sheet_name='Market Stats')
            
            # Add conditional formatting
            worksheet = writer.sheets['Market Stats']
            column_formats = {
                'B': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']},
                'C': {'type': '2_color_scale', 'min_color': config.EXCEL_COLORS['bad'], 'max_color': config.EXCEL_COLORS['good']}
            }
            utils.apply_excel_formatting(worksheet, column_formats)
    
    def process(self) -> pd.DataFrame:
        """
        Process all configurations.
        
        Returns:
            Final processed DataFrame
        """
        # Copy excel templates
        self._copy_excel_templates()
        
        # Load fusion files
        self._load_fusion_files()
        
        # Process stations and buckets
        self.stations = self._process_cable_data(self.stations)
        self.buckets = self._process_cable_data(self.buckets)
        
        # Add categories
        self.stations['CONFIG_CATEGORY'] = 'TVNETW'
        self.buckets['CONFIG_CATEGORY'] = 'BUCKETS'
        
        # Process buckets
        self.buckets = self.buckets.drop_duplicates(["SCARB_KEY", "name"])
        self.buckets = self.buckets.merge(
            self.stations[['SCARB_KEY', 'name', 'LINKING_VARIABLE_NAME']],
            on=['SCARB_KEY', 'name']
        )
        self.buckets['LINKING_VARIABLE_NAME'] = self.buckets['LINKING_VARIABLE_NAME'] + '_B'
        
        # Keep required columns
        cols = ['type', 'PROCESSING_DMA_CODE', 'LINKING_VARIABLE_NAME', 'CONFIG_CATEGORY',
                'IS_IN_CC', 'TRIM_SIDE', 'PCA_FLAG', 'SE_FLAG', 'OE_FLAG']
        self.stations = self.stations[cols]
        self.buckets = self.buckets[cols]
        
        # Create final DataFrame
        self.df = pd.concat([self.buckets, self.stations], ignore_index=True)
        self.df = self.df.drop_duplicates(subset=['PROCESSING_DMA_CODE', 'LINKING_VARIABLE_NAME'])
        
        # Process hispanic stations
        self.df = self._process_hispanic_stations(self.df)
        
        # Create QC file
        self._create_qc_file(self.df)
        
        return self.df
