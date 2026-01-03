"""
Chart visualization classes for webengage-frontend package using Apache ECharts.
"""

from typing import List, Optional, Union, Dict
import pandas as pd
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode


class ChartVisualizer:
    """
    A class for creating professional HTML-based visualizations from pandas DataFrames
    using Apache ECharts.
    
    Args:
        dataframe: pandas DataFrame containing the data to visualize
    """
    
    # Professional color palette matching reference style
    COLOR_PALETTE = [
        '#60A5FA',  # Light Blue (current users)
        '#6B7280',  # Dark Gray (previous period)
        '#10B981',  # Green
        '#EF4444',  # Red
        '#8B5CF6',  # Purple
        '#EC4899',  # Pink
        '#06B6D4',  # Cyan
        '#F97316',  # Orange
    ]
    
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
        width: Optional[int] = None,
        height: Optional[int] = None,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        show_legend: bool = True,
        show_values: bool = False,
        color_palette: Optional[List[str]] = None,
        style: str = 'modern',
        aspect_ratio: Optional[float] = None,
        y_format: Optional[str] = None,
        orientation: str = 'v',
        dark_theme: bool = False,
        comparison_data: Optional[Dict[str, List[float]]] = None,
        total_metric: Optional[Union[float, int, str]] = None,
        comparison_percentage: Optional[float] = None,
    ) -> Bar:
        """
        Create a professional HTML-based bar chart from the DataFrame using Apache ECharts.
        Matches reference style with dark theme, comparison data, and modern styling.
        
        Args:
            x: Column name for the x-axis (string)
            y: List of column names for the y-axis (list of strings)
            width: Optional width in pixels (default: None, uses 100% container width)
            height: Optional height in pixels (default: 600)
            title: Optional title for the chart
            xlabel: Optional label for x-axis
            ylabel: Optional label for y-axis
            show_legend: Whether to show the legend (default: True)
            show_values: Whether to show values on top of bars (default: False)
            color_palette: Optional list of hex color codes for bars
            style: Chart style - 'modern' (default) or 'minimal'
            aspect_ratio: Optional width/height ratio
            y_format: Optional format for y-axis labels ('k' for thousands, 'currency', etc.)
            orientation: 'v' for vertical bars (default) or 'h' for horizontal bars
            dark_theme: If True, uses dark blue background matching reference style
            comparison_data: Optional dict with 'previous' key containing comparison values
            total_metric: Optional large number to display at top (e.g., "29,879")
            comparison_percentage: Optional percentage for comparison indicator (e.g., 8.9)
        
        Returns:
            pyecharts.charts.Bar: ECharts Bar chart object
        
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
        
        # Use custom color palette or default
        colors = color_palette if color_palette else self.COLOR_PALETTE
        
        # Calculate dimensions - use container width (100%) for responsive design
        # Height is calculated based on aspect ratio or default
        if height is None:
            if aspect_ratio:
                # Use a base width for aspect ratio calculation
                base_width = 1000
                height = int(base_width / aspect_ratio)
            else:
                height = 600
        
        # Get data
        x_values = self.dataframe[x].tolist()
        
        # Initialize Bar chart with responsive width
        # Use '100%' for container width, or specified width if provided
        chart_width = f"{width}px" if width else "100%"
        
        bar = Bar(
            init_opts=opts.InitOpts(
                width=chart_width,
                height=f"{height}px",
                theme=ThemeType.DARK if dark_theme else ThemeType.WHITE,
                bg_color='#000000' if dark_theme else '#FFFFFF',
            )
        )
        
        # Add x-axis data
        bar.add_xaxis(x_values)
        
        # Add main data series
        for i, col in enumerate(y):
            y_values = self.dataframe[col].tolist()
            color = colors[i % len(colors)]
            
            # Format label if show_values is True
            label_opts = None
            if show_values:
                if y_format == 'currency':
                    formatter = JsCode("function(params) { return '$' + params.value.toLocaleString(); }")
                elif y_format == 'k':
                    formatter = JsCode("function(params) { return (params.value / 1000).toFixed(1) + 'k'; }")
                elif y_format == 'percentage':
                    formatter = JsCode("function(params) { return params.value.toFixed(1) + '%'; }")
                else:
                    formatter = JsCode("function(params) { return params.value.toLocaleString(); }")
                
                label_opts = opts.LabelOpts(
                    is_show=True,
                    position="top" if orientation == 'v' else "right",
                    formatter=formatter,
                    font_size=11,
                    color='#FFFFFF' if dark_theme else '#374151',
                )
            else:
                label_opts = opts.LabelOpts(is_show=False)
            
            # Add rounded corners to bars
            # For vertical bars: round top corners, for horizontal: round right corners
            if orientation == 'v':
                # Rounded top corners for vertical bars
                borderRadius = [4, 4, 0, 0]  # [topLeft, topRight, bottomRight, bottomLeft]
            else:
                # Rounded right corners for horizontal bars
                borderRadius = [0, 4, 4, 0]
            
            bar.add_yaxis(
                series_name=col,
                y_axis=y_values,
                itemstyle_opts=opts.ItemStyleOpts(
                    color=color,
                    border_color='#FFFFFF' if not dark_theme else '#1E3A8A',
                    border_width=1.5,
                    border_radius=borderRadius,
                ),
                label_opts=label_opts,
            )
        
        # Add comparison data if provided
        if comparison_data and 'previous' in comparison_data:
            prev_values = comparison_data['previous']
            prev_label = comparison_data.get('label', 'Previous (Aug 1 - Aug 31)')
            
            # Add rounded corners for comparison data bars
            if orientation == 'v':
                borderRadius = [4, 4, 0, 0]
            else:
                borderRadius = [0, 4, 4, 0]
            
            bar.add_yaxis(
                series_name=prev_label,
                y_axis=prev_values,
                itemstyle_opts=opts.ItemStyleOpts(
                    color='#6B7280',  # Dark gray for previous period
                    border_color='#FFFFFF' if not dark_theme else '#1E3A8A',
                    border_width=1.5,
                    border_radius=borderRadius,
                ),
                label_opts=opts.LabelOpts(is_show=False),
            )
        
        # Configure title with optional total metric and comparison
        title_text = title if title else ''
        if total_metric:
            metric_text = f"{total_metric:,.0f}" if isinstance(total_metric, (int, float)) else str(total_metric)
            metric_color = '#FFFFFF' if dark_theme else '#111827'
            title_text = f"<div style='font-size:32px; font-weight:bold; color:{metric_color}; margin-bottom:10px;'>{metric_text}</div>" + title_text
        
        if comparison_percentage is not None:
            comparison_color = '#10B981' if comparison_percentage >= 0 else '#EF4444'
            arrow = '▲' if comparison_percentage >= 0 else '▼'
            comparison_text = f"<div style='font-size:14px; color:{comparison_color}; margin-top:5px;'>{arrow} {abs(comparison_percentage):.1f}% vs comparison period</div>"
            title_text = title_text + comparison_text
        
        # Set global options
        bar.set_global_opts(
            title_opts=opts.TitleOpts(
                title=title_text if title_text else None,
                title_textstyle_opts=opts.TextStyleOpts(
                    color='#FFFFFF' if dark_theme else '#111827',
                    font_size=16,
                    font_weight='bold',
                ),
                pos_left='center',
                pos_top='top',
            ),
            legend_opts=opts.LegendOpts(
                is_show=show_legend and (len(y) > 1 or comparison_data is not None),
                pos_bottom='bottom',
                pos_left='center',
                orient='horizontal',
                textstyle_opts=opts.TextStyleOpts(
                    color='#FFFFFF' if dark_theme else '#374151',
                    font_size=11,
                ),
                item_gap=20,
            ),
            xaxis_opts=opts.AxisOpts(
                name=xlabel if xlabel else x,
                name_textstyle_opts=opts.TextStyleOpts(
                    color='#FFFFFF' if dark_theme else '#374151',
                    font_size=12,
                ),
                axislabel_opts=opts.LabelOpts(
                    color='#FFFFFF' if dark_theme else '#374151',
                    font_size=11,
                    rotate=45 if orientation == 'v' else 0,
                ),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(
                        color='#3B82F6' if dark_theme else '#E5E7EB',
                        width=1,
                    )
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=False,  # No vertical grid lines
                ),
            ),
            yaxis_opts=opts.AxisOpts(
                name=ylabel if ylabel else (y[0] if len(y) == 1 else 'Value'),
                name_textstyle_opts=opts.TextStyleOpts(
                    color='#FFFFFF' if dark_theme else '#374151',
                    font_size=12,
                ),
                axislabel_opts=opts.LabelOpts(
                    color='#FFFFFF' if dark_theme else '#6B7280',
                    font_size=11,
                    formatter=JsCode("function(value) { return value.toLocaleString(); }") if y_format != 'k' else JsCode("function(value) { return (value / 1000).toFixed(1) + 'k'; }"),
                ),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(
                        color='#3B82F6' if dark_theme else '#E5E7EB',
                        width=1,
                    )
                ),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True,  # Horizontal grid lines
                    linestyle_opts=opts.LineStyleOpts(
                        color='#3B82F6' if dark_theme else '#E5E7EB',
                        width=1,
                        type_='solid',
                        opacity=0.3,
                    )
                ),
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger='axis',
                axis_pointer_type='shadow',
                background_color='rgba(0, 0, 0, 0.8)' if dark_theme else 'rgba(255, 255, 255, 0.95)',
                border_color='#E5E7EB' if not dark_theme else '#6B7280',
                textstyle_opts=opts.TextStyleOpts(
                    color='#FFFFFF' if dark_theme else '#111827',
                    font_size=11,
                ),
            ),
            datazoom_opts=None,
        )
        
        # Set series options for bar spacing
        bar.set_series_opts(
            bar_width='60%' if len(y) == 1 and not comparison_data else None,
            category_gap='20%' if len(y) > 1 or comparison_data else '40%',
        )
        
        return bar
    
    def to_html(
        self,
        chart: Bar,
        filename: Optional[str] = None,
        path: str = "render.html"
    ) -> str:
        """
        Convert an ECharts chart to HTML string with responsive container width.
        
        Args:
            chart: ECharts Bar chart object
            filename: Optional filename to save HTML file (deprecated, use path)
            path: Path to save HTML file (default: "render.html")
        
        Returns:
            str: HTML string representation of the figure with responsive sizing
        """
        if filename:
            path = filename
        
        chart.render(path)
        
        # Read the generated HTML
        with open(path, 'r', encoding='utf-8') as f:
            html_str = f.read()
        
        # Add responsive JavaScript and rounded corners to bars
        resize_script = """
        <script>
        // Make all ECharts instances responsive to container width and add rounded corners
        if (typeof window.addEventListener !== 'undefined') {
            function resizeAllCharts() {
                if (typeof echarts !== 'undefined') {
                    // Find all chart containers and resize them
                    document.querySelectorAll('[id^="chart_"]').forEach(function(div) {
                        var chart = echarts.getInstanceByDom(div);
                        if (chart && typeof chart.resize === 'function') {
                            chart.resize();
                        }
                    });
                }
            }
            
            function addRoundedCorners() {
                if (typeof echarts !== 'undefined') {
                    document.querySelectorAll('[id^="chart_"]').forEach(function(div) {
                        var chart = echarts.getInstanceByDom(div);
                        if (chart) {
                            var option = chart.getOption();
                            // Add borderRadius to all bar series
                            if (option && option.series) {
                                var updated = false;
                                option.series.forEach(function(series) {
                                    if (series.type === 'bar') {
                                        if (!series.itemStyle) {
                                            series.itemStyle = {};
                                        }
                                        // Add rounded corners: [topLeft, topRight, bottomRight, bottomLeft]
                                        // For vertical bars, round top corners (4px radius)
                                        series.itemStyle.borderRadius = [4, 4, 0, 0];
                                        updated = true;
                                    }
                                });
                                if (updated) {
                                    chart.setOption(option, true);
                                }
                            }
                        }
                    });
                }
            }
            
            window.addEventListener('resize', resizeAllCharts);
            window.addEventListener('load', function() {
                setTimeout(function() {
                    resizeAllCharts();
                    addRoundedCorners();
                }, 100);
            });
            
            // Also resize when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    setTimeout(function() {
                        resizeAllCharts();
                        addRoundedCorners();
                    }, 100);
                });
            } else {
                setTimeout(function() {
                    resizeAllCharts();
                    addRoundedCorners();
                }, 100);
            }
        }
        </script>
        """
        
        # Insert the resize script before closing body tag
        if '</body>' in html_str:
            html_str = html_str.replace('</body>', resize_script + '</body>')
        else:
            # If no body tag, append to the end
            html_str = html_str + resize_script
        
        return html_str
