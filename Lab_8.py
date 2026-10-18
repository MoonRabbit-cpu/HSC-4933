#####################################################
# Bryan Hernandez Rodriguez                         #
# Lab_8.py: Interactive OLS Regression UPDATE       #
# Prompts for a dataset, cleans column names,       #
# lets the user pick X and Y, plots a scatterplot,  #
# fits an OLS line, and optionally saves both plots.#
#####################################################
# LINEAR REGRESSION LAB # LAB.7, 2026 (C)  #
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
# ------------------------------------------#
# Updated: CLI plot-formatting menu + two dependent variables on one plot

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.colors import is_color_like


# ----------------------------------------------------------------------
# Input helpers
# ----------------------------------------------------------------------

#Ask a yes/no question. Accepts y/yes/n/no.
def ask_yes_no(prompt, default=None):
    suffix = " (yes/no): " if default is None else f" (yes/no) [{'yes' if default else 'no'}]: "
    while True:
        ans = input(prompt + suffix).strip().lower()
        if ans == "" and default is not None:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  Please answer yes or no.")

#Ask for a matplotlib color (name like 'red', hex like '#1f77b4', or single letter).
def ask_color(prompt, current):
    while True:
        ans = input(f"{prompt} [{current}]: ").strip()
        if ans == "":
            return current
        if is_color_like(ans):
            return ans
        print("  Not a valid color. Try a name (red, navy, teal), a hex code (#1f77b4), or b/g/r/c/m/y/k.")



#Ask for a number within an optional range.
def ask_float(prompt, current, low=None, high=None):
    while True:
        ans = input(f"{prompt} [{current}]: ").strip()
        if ans == "":
            return current
        try:
            val = float(ans)
        except ValueError:
            print("  Please enter a number.")
            continue
        if (low is not None and val < low) or (high is not None and val > high):
            print(f"  Value must be between {low} and {high}.")
            continue
        return val

#Ask the user to pick from a list of options (by name or number).
def ask_choice(prompt, options, current):
    print(f"{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        ans = input(f"Choice [{current}]: ").strip()
        if ans == "":
            return current
        if ans.isdigit() and 1 <= int(ans) <= len(options):
            return options[int(ans) - 1]
        if ans in options:
            return ans
        print("  Invalid choice.")

#Ask for a column name that exists in the dataset.
def ask_column(prompt, columns, exclude=()):
    while True:
        ans = input(prompt).strip().lower().replace(" ", "_")
        if ans in columns and ans not in exclude:
            return ans
        if ans in exclude:
            print("  That column is already selected. Pick a different one.")
        else:
            print("  Column not found. Choose from the list above.")


# ----------------------------------------------------------------------
# Data helpers
# ----------------------------------------------------------------------
#Strip commas and convert to numbers (bad values become NaN).
def to_numeric_series(series):
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


#Return a clean two-column DataFrame (x, y) with no missing values.
def prepare_pair(df, x_col, y_col):
    data = df[[x_col, y_col]].copy()
    data[x_col] = to_numeric_series(data[x_col])
    data[y_col] = to_numeric_series(data[y_col])
    return data.dropna()

#Fit y = b0 + b1*x with statsmodels.
def fit_ols(data, x_col, y_col):
    X = sm.add_constant(data[x_col])
    return sm.OLS(data[y_col], X).fit()


# ----------------------------------------------------------------------
# Plot settings + CLI menu
# ----------------------------------------------------------------------
MARKERS = ["o", "s", "^", "v", "D", "x", "+", "*", "."]
LINESTYLES = ["-", "--", "-.", ":"]
GRID_STYLES = ["-", "--", "-.", ":"]
LEGEND_LOCS = ["best", "upper left", "upper right", "lower left", "lower right",
               "center left", "center right", "upper center", "lower center", "center"]
THEMES = ["default", "ggplot", "seaborn-v0_8", "bmh", "fivethirtyeight", "dark_background"]

#default setting for scatterplot
def default_settings(x_col, y1_col, y2_col):
    return {
        "title": f"{y1_col} and {y2_col} vs. {x_col}",
        "x_label": x_col,
        "y1_label": y1_col,
        "y2_label": y2_col,
        "y1_color": "tab:blue",
        "y2_color": "tab:orange",
        "marker1": "o",
        "marker2": "s",
        "marker_size": 40.0,
        "alpha": 0.6,
        "show_line": True,
        "line_width": 2.0,
        "line_style": "-",
        "show_grid": True,
        "grid_style": "--",
        "grid_alpha": 0.3,
        "show_legend": True,
        "legend_loc": "best",
        "secondary_axis": False,
        "fig_w": 8.0,
        "fig_h": 6.0,
        "theme": "default",
    }


def yn(value):
    return "on" if value else "off"

#Print menu
def print_menu(s):
    print("\n" + "=" * 52)
    print(" PLOT FORMAT MENU")
    print("=" * 52)
    print(f"  1. Title ................ {s['title']}")
    print(f"  2. X-axis label ......... {s['x_label']}")
    print(f"  3. Y1 label ............. {s['y1_label']}")
    print(f"  4. Y2 label ............. {s['y2_label']}")
    print(f"  5. Y1 color ............. {s['y1_color']}")
    print(f"  6. Y2 color ............. {s['y2_color']}")
    print(f"  7. Marker styles ........ Y1 '{s['marker1']}' / Y2 '{s['marker2']}'")
    print(f"  8. Marker size .......... {s['marker_size']}")
    print(f"  9. Point transparency ... {s['alpha']}")
    print(f" 10. OLS lines ............ {yn(s['show_line'])}")
    print(f" 11. Line width ........... {s['line_width']}")
    print(f" 12. Line style ........... {s['line_style']}")
    print(f" 13. Gridlines ............ {yn(s['show_grid'])}")
    print(f" 14. Grid style / alpha ... {s['grid_style']} / {s['grid_alpha']}")
    print(f" 15. Legend ............... {yn(s['show_legend'])} ({s['legend_loc']})")
    print(f" 16. Separate Y2 axis ..... {yn(s['secondary_axis'])}")
    print(f" 17. Figure size (in) ..... {s['fig_w']} x {s['fig_h']}")
    print(f" 18. Theme ................ {s['theme']}")
    print("  p. Preview plot")
    print("  r. Reset to defaults")
    print("  d. Done (continue)")

#Format menu. Interactive loop that lets the user tweak plot settings.
def format_menu(settings, defaults, build_fn):
    while True:
        print_menu(settings)
        choice = input("\nSelect an option: ").strip().lower()

        if choice == "1":
            val = input(f"Title [{settings['title']}]: ").strip()
            settings["title"] = val or settings["title"]
        elif choice == "2":
            val = input(f"X-axis label [{settings['x_label']}]: ").strip()
            settings["x_label"] = val or settings["x_label"]
        elif choice == "3":
            val = input(f"Y1 label [{settings['y1_label']}]: ").strip()
            settings["y1_label"] = val or settings["y1_label"]
        elif choice == "4":
            val = input(f"Y2 label [{settings['y2_label']}]: ").strip()
            settings["y2_label"] = val or settings["y2_label"]
        elif choice == "5":
            settings["y1_color"] = ask_color("Y1 color", settings["y1_color"])
        elif choice == "6":
            settings["y2_color"] = ask_color("Y2 color", settings["y2_color"])
        elif choice == "7":
            settings["marker1"] = ask_choice("Marker for Y1:", MARKERS, settings["marker1"])
            settings["marker2"] = ask_choice("Marker for Y2:", MARKERS, settings["marker2"])
        elif choice == "8":
            settings["marker_size"] = ask_float("Marker size", settings["marker_size"], 1, 500)
        elif choice == "9":
            settings["alpha"] = ask_float("Point transparency (0-1)", settings["alpha"], 0.05, 1)
        elif choice == "10":
            settings["show_line"] = ask_yes_no("Show OLS regression lines?", settings["show_line"])
        elif choice == "11":
            settings["line_width"] = ask_float("Line width", settings["line_width"], 0.5, 10)
        elif choice == "12":
            settings["line_style"] = ask_choice("Line style:", LINESTYLES, settings["line_style"])
        elif choice == "13":
            settings["show_grid"] = ask_yes_no("Show gridlines?", settings["show_grid"])
        elif choice == "14":
            settings["grid_style"] = ask_choice("Grid style:", GRID_STYLES, settings["grid_style"])
            settings["grid_alpha"] = ask_float("Grid transparency (0-1)", settings["grid_alpha"], 0.05, 1)
        elif choice == "15":
            settings["show_legend"] = ask_yes_no("Show legend?", settings["show_legend"])
            if settings["show_legend"]:
                settings["legend_loc"] = ask_choice("Legend location:", LEGEND_LOCS, settings["legend_loc"])
        elif choice == "16":
            print("A separate right-hand Y axis helps when Y1 and Y2 are on very different scales.")
            settings["secondary_axis"] = ask_yes_no("Use a separate Y2 axis?", settings["secondary_axis"])
        elif choice == "17":
            settings["fig_w"] = ask_float("Figure width (inches)", settings["fig_w"], 3, 25)
            settings["fig_h"] = ask_float("Figure height (inches)", settings["fig_h"], 3, 25)
        elif choice == "18":
            settings["theme"] = ask_choice("Theme:", THEMES, settings["theme"])
        elif choice == "p":
            fig = build_fn(settings)
            plt.show()
            plt.close(fig)
        elif choice == "r":
            settings.clear()
            settings.update(defaults())
            print("Settings reset to defaults.")
        elif choice == "d":
            return settings
        else:
            print("Invalid option. Try again.")


# ----------------------------------------------------------------------
# Plot builder
# ----------------------------------------------------------------------
#Create the figure: both Y variables against the same X variable.
def build_plot(settings, x_col, y1_col, y2_col, data1, data2, model1, model2):

    # Theme is applied through a context so it doesn't leak between redraws
    with plt.style.context(settings["theme"]):
        fig, ax1 = plt.subplots(figsize=(settings["fig_w"], settings["fig_h"]))
        ax2 = ax1.twinx() if settings["secondary_axis"] else ax1

        # Scatter points
        ax1.scatter(data1[x_col], data1[y1_col], s=settings["marker_size"],
                    c=settings["y1_color"], marker=settings["marker1"],
                    alpha=settings["alpha"], edgecolor="k", linewidth=0.3,
                    label=settings["y1_label"])
        ax2.scatter(data2[x_col], data2[y2_col], s=settings["marker_size"],
                    c=settings["y2_color"], marker=settings["marker2"],
                    alpha=settings["alpha"], edgecolor="k", linewidth=0.3,
                    label=settings["y2_label"])

        # OLS lines (each drawn over its own x-range)
        if settings["show_line"]:
            for ax, data, model, y_col, color, label in (
                    (ax1, data1, model1, y1_col, settings["y1_color"], settings["y1_label"]),
                    (ax2, data2, model2, y2_col, settings["y2_color"], settings["y2_label"]),
            ):
                x_line = np.linspace(data[x_col].min(), data[x_col].max(), 100)
                y_line = model.params["const"] + model.params[x_col] * x_line
                ax.plot(x_line, y_line, color=color, linewidth=settings["line_width"],
                        linestyle=settings["line_style"],
                        label=f"{label} OLS (R² = {model.rsquared:.3f})")

        # Labels, title
        ax1.set_xlabel(settings["x_label"])
        if settings["secondary_axis"]:
            ax1.set_ylabel(settings["y1_label"], color=settings["y1_color"])
            ax2.set_ylabel(settings["y2_label"], color=settings["y2_color"])
        else:
            ax1.set_ylabel(f"{settings['y1_label']} / {settings['y2_label']}")
        ax1.set_title(settings["title"])

        # Gridlines
        if settings["show_grid"]:
            ax1.grid(True, linestyle=settings["grid_style"], alpha=settings["grid_alpha"])
        else:
            ax1.grid(False)

        # Combined legend (handles both axes when twinx is used)
        if settings["show_legend"]:
            handles, labels = ax1.get_legend_handles_labels()
            if ax2 is not ax1:
                h2, l2 = ax2.get_legend_handles_labels()
                handles += h2
                labels += l2
            ax1.legend(handles, labels, loc=settings["legend_loc"])

        fig.tight_layout()
    return fig


# ----------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------
def main():
    # prompt user for dataset
    csv_path = input("Enter the dataset filename: ").strip()
    try:
        df = pd.read_csv(csv_path)
    except (FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError) as err:
        print(f"Error: could not read '{csv_path}' ({err}).")
        raise SystemExit

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    if "rownames" in df.columns:
        df = df.drop(columns="rownames")

    # List available column names
    print("\nAvailable column names:")
    for column in df.columns:
        print(f"  {column}")

    # Prompt user for one X and two Y variables
    x_col = ask_column("\nEnter the X (independent) variable: ", df.columns)
    y1_col = ask_column("Enter the first Y (dependent) variable: ", df.columns, exclude=(x_col,))
    y2_col = ask_column("Enter the second Y (dependent) variable: ", df.columns, exclude=(x_col, y1_col))

    # Clean each X/Y pair separately so one variable's missing values
    # don't throw away rows for the other
    data1 = prepare_pair(df, x_col, y1_col)
    data2 = prepare_pair(df, x_col, y2_col)
    print(f"\nRows available for regression: {y1_col}: {len(data1)}, {y2_col}: {len(data2)}")

    if len(data1) < 3 or len(data2) < 3:
        print("Error: need at least 3 valid rows for each regression.")
        raise SystemExit

    # Perform both regressions
    model1 = fit_ols(data1, x_col, y1_col)
    model2 = fit_ols(data2, x_col, y2_col)

    for y_col, model in ((y1_col, model1), (y2_col, model2)):
        print(f"\n{'=' * 60}\nOLS Regression Summary: {y_col} ~ {x_col}\n{'=' * 60}")
        print(model.summary())
        print(f"Beta 0 (intercept): {model.params['const']:.4f}")
        print(f"Beta 1 (slope):     {model.params[x_col]:.4f}")
        print(f"R²:                 {model.rsquared:.4f}")

    # Formatting menu
    def defaults():
        return default_settings(x_col, y1_col, y2_col)

    def build(settings):
        return build_plot(settings, x_col, y1_col, y2_col, data1, data2, model1, model2)

    settings = defaults()
    if ask_yes_no("\nWould you like to customize the plot format?", default=True):
        format_menu(settings, defaults, build)

    # Build final figure
    fig = build(settings)

    # Save
    if ask_yes_no("\nWould you like to save the plot?"):
        filename = input("Enter a filename (without extension for .png): ").strip()
        if not filename:
            filename = f"{x_col}_vs_{y1_col}_{y2_col}"
        if "." not in filename:
            filename += ".png"
        dpi = int(ask_float("DPI", 300, 50, 1200))
        fig.savefig(filename, dpi=dpi)
        print(f"Saved plot -> {filename}")

    # Display
    plt.show()


if __name__ == "__main__":
    main()
