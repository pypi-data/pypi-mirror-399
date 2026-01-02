###############################################################################
# artpack/circle_data.py
###############################################################################
from numpy import linspace, pi, cos, sin
import polars as pl
from artpack._utils import (
    _check_type,
    _is_positive_number,
    _is_valid_color,
    _check_min_points,
)


def circle_data(
    x: float | int,
    y: float | int,
    radius: float | int,
    color: str = None,
    fill: str = None,
    n_points: int = 100,
    group_var: bool = False,
    group_value: str = "circle_",
) -> pl.DataFrame:
    """
    Generate data for plotting a circle as a DataFrame.

    Creates a data frame of (x, y) coordinates representing a circle with a specified center and radius.

    Notes
    -----
    The output is designed for use with `geom_path` and `geom_polygon` geoms in `plotnine` for generative art.

    Parameters
    ----------
    x : float or int
        The center x-coordinate of the circle.
    y : float or int
        The center y-coordinate of the circle.
    radius : float or int
        The radius of the circle. Must be greater than 0.
    color : str, optional, default None
        The outline color of the circle. Default None.
    fill : str, optional, default None
        The fill color of the circle. Default None.
    n_points : int, default 100
        Number of points to generate along the circle's perimeter. Must be an integer >= 10 for a reasonable approximation of a circle.
    group_var : bool, default False
        Whether to include a grouping variable in the output.
    group_value : str, default "circle_"
        Prefix for the grouping variable name. Required if `group_var` is True.

    Returns
    -------
    data : pl.DataFrame
        A DataFrame containing the circle's coordinates with columns:

        - x: x-coordinates of points along the circle's perimeter

        - y: y-coordinates of points along the circle's perimeter

        - color: outline color (if specified)

        - fill: fill color (if specified)

        - group: grouping variable (if group_var is True)

    Examples
    --------
    ```python
    from artpack.circles import circle_data
    from plotnine import ggplot, aes, geom_path, coord_equal

    one_circle = circle_data(x=0, y=0, radius=5)
    (ggplot(one_circle, aes("x", "y")) + geom_path(color="green") + coord_equal())
    ```
    ![](../assets/img/circle_data-ex.png){fig-cap="" fig-alt="A green outline of a circle"}
    """

    ###############################################################################
    # Input Checks
    ###############################################################################
    # Numeric Checks
    _check_type("x", x, (float, int))
    _check_type("y", y, (float, int))
    _check_type("radius", radius, (float, int))
    _check_type("n_points", n_points, int)
    _is_positive_number("radius", radius)
    _check_min_points(n_points, 100, "circle")

    # Color Checks
    if color is not None:
        _is_valid_color("color", color)

    if fill is not None:
        _is_valid_color("fill", fill)

    # Grouping Checks
    if group_var:
        _check_type("group_value", group_value, str)

    ###############################################################################
    # Data Generation
    ###############################################################################
    # Create Theta
    theta = linspace(0, 2 * pi, n_points)
    x_vals = cos(theta) * radius + x
    y_vals = sin(theta) * radius + y

    # Create circle schema
    circle_schema = {"x": pl.Float32, "y": pl.Float32}
    circle_data_dict = {"x": x_vals, "y": y_vals}

    # Conditional checks to add extra vars
    if color is not None:
        circle_data_dict["color"] = color
        circle_schema["color"] = pl.Utf8

    if fill is not None:
        circle_data_dict["fill"] = fill
        circle_schema["fill"] = pl.Utf8

    if group_var:
        circle_data_dict["group"] = group_value
        circle_schema["group"] = pl.Utf8

    df = pl.DataFrame(circle_data_dict, schema=circle_schema)
    return df
