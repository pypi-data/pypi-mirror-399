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

Create bar charts from pandas DataFrames:

```python
import pandas as pd
import matplotlib.pyplot as plt
from webengage_frontend import ChartVisualizer

# Create sample DataFrame
df = pd.DataFrame({
    'category': ['A', 'B', 'C', 'D'],
    'sales': [100, 150, 120, 180],
    'profit': [20, 30, 25, 40]
})

# Initialize ChartVisualizer
visualizer = ChartVisualizer(df)

# Create bar chart with single y-axis column
fig = visualizer.bar_chart(
    x='category',
    y=['sales'],
    title='Sales by Category',
    xlabel='Category',
    ylabel='Sales'
)
plt.show()

# Create bar chart with multiple y-axis columns
fig = visualizer.bar_chart(
    x='category',
    y=['sales', 'profit'],
    title='Sales and Profit by Category',
    xlabel='Category',
    ylabel='Amount'
)
plt.show()
```

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
