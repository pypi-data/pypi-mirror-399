# webengage-frontend

A Python package for frontend-related functionality.

## Description

`webengage-frontend` is a Python package designed to provide frontend-related utilities and tools for WebEngage projects. It includes chart visualization capabilities for creating bar charts from pandas DataFrames.

## Installation

### From Source

```bash
# Clone the repository
git clone https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo.git
cd data-science-consulting-master-repo/webengage-fe

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Using pip

```bash
pip install webengage-frontend
```

## Requirements

- Python >= 3.8

## Development Setup

1. Clone the repository:
```bash
git clone https://repo.webengage.com/data-consultancy/data-science-consulting-master-repo.git
cd data-science-consulting-master-repo/webengage-fe
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install the package in development mode:
```bash
pip install -e .
```

## Usage

### Chart Visualization

Create professional, interactive HTML-based bar charts from pandas DataFrames with optimal aspect ratios:

```python
import pandas as pd
from webengage_frontend import ChartVisualizer

# Create sample DataFrame
df = pd.DataFrame({
    'category': ['Q1', 'Q2', 'Q3', 'Q4'],
    'sales': [100000, 150000, 120000, 180000],
    'profit': [20000, 30000, 25000, 40000],
    'expenses': [80000, 120000, 95000, 140000]
})

# Initialize ChartVisualizer
visualizer = ChartVisualizer(df)

# Create bar chart with single y-axis column (optimal aspect ratio)
# Matches reference style: clean, minimal, no value labels by default
fig = visualizer.bar_chart(
    x='category',
    y=['sales'],
    title='Sales by Category',
    xlabel='Category',
    ylabel='Sales ($)',
    show_values=False,  # No value labels (matching reference style)
    aspect_ratio=1.8    # Optimal width-to-height ratio
)
fig.show()  # Display interactive HTML chart

# Create grouped bar chart with multiple y-axis columns
# Clean style with horizontal grid lines only
fig = visualizer.bar_chart(
    x='category',
    y=['sales', 'profit', 'expenses'],
    title='Financial Overview by Quarter',
    xlabel='Quarter',
    ylabel='Amount ($)',
    width=1200,         # Custom width in pixels
    height=600,         # Custom height in pixels
    show_values=False,  # Clean look without value labels
    show_legend=True,
    y_format='k'        # Format y-axis as thousands (1.0k, 2.5k)
)
fig.show()

# Export to HTML file
html_str = visualizer.to_html(fig, filename='chart.html')
print("Chart saved to chart.html")

# Custom color palette
custom_colors = ['#1E40AF', '#059669', '#DC2626']
fig = visualizer.bar_chart(
    x='category',
    y=['sales', 'profit'],
    title='Sales vs Profit',
    color_palette=custom_colors,
    style='modern',
    aspect_ratio=2.0  # Wider chart
)
fig.show()

# For Jupyter Notebooks or Streamlit
# fig.show() works directly
# For web applications, use: visualizer.to_html(fig)
```

#### Bar Chart Features

- **Reference-Style Design**: Clean, minimal bar charts matching professional reference style
- **HTML/JavaScript Based**: Interactive charts using Plotly.js for web compatibility
- **Optimal Aspect Ratios**: Automatic calculation of width-to-height ratios (default 1.8:1)
- **Clean Styling**: 
  - White background (no grey backgrounds)
  - Horizontal grid lines only (no vertical grid lines)
  - Thin bars with clear spacing between groups
  - No value labels by default (clean, minimal look)
- **Interactive**: Hover tooltips, zoom, pan, and export capabilities
- **Professional Design**: Modern, crisp visualization with clean styling
- **Value Labels**: Optional value labels (disabled by default to match reference)
- **Custom Dimensions**: Specify exact width/height in pixels or use aspect ratios
- **Custom Colors**: Use your own color palette or choose from the default professional palette
- **Multiple Series**: Support for grouped bar charts with multiple data series
- **Y-Axis Formatting**: Format y-axis labels (thousands, currency, etc.)
- **Flexible Styling**: Choose between 'modern' and 'minimal' styles
- **Web Ready**: Perfect for dashboards, web applications, and HTML reports
- **Export Options**: Save charts as standalone HTML files or embed in web pages

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

### Type Checking

```bash
mypy src/
```

## Project Structure

```
webengage-fe/
├── src/
│   └── webengage_frontend/     # Main package directory
│       ├── __init__.py
│       ├── charts.py           # Chart visualization classes
│       └── utils.py            # Utility functions
├── tests/                      # Test files
│   ├── __init__.py
│   └── test_utils.py
├── setup.py                    # Setup script
├── pyproject.toml             # Modern Python packaging configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── MANIFEST.in                # Package manifest
├── LICENSE                    # MIT License
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Merge Request

## License

This project is licensed under the MIT License.

## Authors

- WebEngage

## Project Status

Active development.
