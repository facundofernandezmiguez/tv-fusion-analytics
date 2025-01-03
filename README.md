# TVFusion Analytics

A comprehensive analytics suite for TV Fusion data, providing powerful tools for data analysis, visualization, and linking variable configuration. This package streamlines the process of analyzing TV Fusion metrics and managing market configurations.

## Features

- **Analytics & Visualization**
  - Metric pivot tables with customizable formatting
  - Penetration analysis across markets
  - Evolution analysis across releases
  - Statistical visualizations
  - Market performance insights

- **LV Configuration Manager**
  - Automated cable data processing
  - Hispanic market handling
  - QC file generation with market statistics
  - Excel output with conditional formatting

## Project Structure
```
tvfusion-analytics/
├── src/
│   ├── lv_config/
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── analysis_tools.py
│   └── utils.py
├── config.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/tvfusion-analytics.git
cd tvfusion-analytics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Analysis
```python
from src.analysis import FusionAnalyzer

# Initialize analyzer
analyzer = FusionAnalyzer(release='123')

# Generate insights
analyzer.create_metric_pivots()
analyzer.create_penetration_pivots()
analyzer.plot_evolution(['222', '123'])
```

### LV Configuration
```python
from src.lv_config import LVConfigManager

# Initialize and process configurations
config = LVConfigManager(release=223)
config.process()
```

## Configuration

The project uses a central configuration file (`config.py`) that contains all paths and settings. Modify this file to match your environment:

```python
# Example config.py customization
FUSION_BASE = '/path/to/your/fusion/data'
SCARBOROUGH_BASE = '/path/to/scarborough/data'
```

## Utilities

Common functions are available in the `src/utils.py` module, providing shared functionality for:
- Data preprocessing and cleaning
- Excel formatting and styling
- Statistical calculations
- Change analysis and categorization

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Your Name - *Initial work* - [YourGitHub](https://github.com/yourusername)
