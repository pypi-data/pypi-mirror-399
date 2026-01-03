"""
Chart visualization classes for webengage-frontend package.
"""

from typing import List, Optional
import pandas as pd
import matplotlib.pyplot as plt


class ChartVisualizer:
    """
    A class for creating visualizations from pandas DataFrames.
    
    Args:
        dataframe: pandas DataFrame containing the data to visualize
    """
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize the ChartVisualizer with a DataFrame.
        
        Args:
            dataframe: pandas DataFrame containing the data
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        self.dataframe = dataframe.copy()
    
    def bar_chart(
        self,
        x: str,
        y: List[str],
        figsize: Optional[tuple] = None,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        show_legend: bool = True,
    ):
        """
        Create a bar chart from the DataFrame.
        
        Args:
            x: Column name for the x-axis (string)
            y: List of column names for the y-axis (list of strings)
            figsize: Optional tuple (width, height) for figure size
            title: Optional title for the chart
            xlabel: Optional label for x-axis
            ylabel: Optional label for y-axis
            show_legend: Whether to show the legend (default: True)
        
        Returns:
            matplotlib.figure.Figure: The figure object
        
        Raises:
            ValueError: If x or y columns don't exist in the DataFrame
        """
        # Validate x column exists
        if x not in self.dataframe.columns:
            raise ValueError(f"Column '{x}' not found in DataFrame")
        
        # Validate y columns exist
        for col in y:
            if col not in self.dataframe.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame")
        
        # Set default figure size if not provided
        if figsize is None:
            figsize = (10, 6)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get x-axis values
        x_values = self.dataframe[x]
        
        # Set up bar positions
        num_bars = len(y)
        bar_width = 0.8 / num_bars if num_bars > 1 else 0.8
        positions = range(len(x_values))
        
        # Plot bars for each y column
        for i, col in enumerate(y):
            y_values = self.dataframe[col]
            offset = (i - (num_bars - 1) / 2) * bar_width if num_bars > 1 else 0
            ax.bar(
                [p + offset for p in positions],
                y_values,
                width=bar_width,
                label=col
            )
        
        # Set x-axis labels
        ax.set_xticks(positions)
        ax.set_xticklabels(x_values, rotation=45, ha='right')
        
        # Set labels and title
        if xlabel:
            ax.set_xlabel(xlabel)
        else:
            ax.set_xlabel(x)
        
        if ylabel:
            ax.set_ylabel(ylabel)
        
        if title:
            ax.set_title(title)
        
        # Show legend if multiple y columns
        if show_legend and len(y) > 1:
            ax.legend()
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        return fig

