"""
Configuration settings for TV Fusion Analysis Tools.
"""

import os

# Base paths
FUSION_BASE = 'C:/Fusion/POV'
SCARBOROUGH_BASE = 'C:/SCARBOROUGH/TV_Fusion'

# Analysis paths
ANALYSIS_PATH = os.path.join(FUSION_BASE, 'Analysis')
REFERENCES_PATH = os.path.join(FUSION_BASE, 'References')
GRAPHS_PATH = os.path.join(ANALYSIS_PATH, 'graphs')

# Reference files
MARKET_CODES_FILE = os.path.join(REFERENCES_PATH, 'market_codes.csv')
CATEGORY_NAMES_FILE = os.path.join(REFERENCES_PATH, 'mapping_category_codes_to_names.csv')

# Data files
METRICS_FILE = 'POV_Fusion_Metrics.csv'
PENETRATIONS_FILE = 'POV_Fusion_Penetrations.csv'

# LV Config paths
LV_CONFIG_PATH = os.path.join(SCARBOROUGH_BASE, 'lv_config')
LV_REFERENCES_PATH = os.path.join(LV_CONFIG_PATH, 'References')

# Excel formatting
EXCEL_COLORS = {
    'good': '#8BC34A',
    'bad': '#F5A623'
}

# Analysis parameters
MEAN_THRESHOLD = 2
STD_THRESHOLD = 0.5

# Market types
MARKET_TYPES = ['LPM', 'CR', 'SM']

# Ensure directories exist
for path in [ANALYSIS_PATH, REFERENCES_PATH, GRAPHS_PATH, LV_CONFIG_PATH, LV_REFERENCES_PATH]:
    os.makedirs(path, exist_ok=True)
