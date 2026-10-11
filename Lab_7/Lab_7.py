#####################################################
# Bryan Hernandez Rodriguez                         #
# Lab_7.py: Interactive OLS Regression              #
# Prompts for a dataset, cleans column names,       #
# lets the user pick X and Y, plots a scatterplot,  #
# fits an OLS line, and optionally saves both plots.#
#####################################################




#imports
import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm



#converts columns in to snake_case and camel_Case and removed non_alphnumerics
def to_snake_case(name):
    name = str(name).strip()
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)  # camelCase -> camel_Case
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)            # non-alphanumerics -> _
    return name.strip("_").lower()




#Yes/no Prompt
def ask_yes_no(prompt):
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")




#prompts the user for which columns they would like
def ask_column(prompt, columns):
    while True:
        choice = to_snake_case(input(prompt).strip())
        if choice in columns:
            return choice
        print(f"'{choice}' is not a column. Please choose from the list above.")





#file save
def save_figure(fig, default_name):
    name = input(f"Enter a file name (default: {default_name}): ").strip()
    if not name:
        name = default_name
    if not name.lower().endswith(".png"):
        name += ".png"
    fig.savefig(name, dpi=300)
    print(f"Saved -> {name}")






def main():
    # 1. Prompt for dataset and load it
    while True:
        path = input("Enter the dataset file path (CSV): ").strip().strip('"').strip("'")
        try:
            df = pd.read_csv(path)
            break
        except FileNotFoundError:
            print(f"File '{path}' not found. Try again.")
        except Exception as e:
            print(f"Could not read file: {e}")
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns.")




    # 2. Clean column names to snake_case
    df.columns = [to_snake_case(c) for c in df.columns]





    # 3. List available columns
    print("\nAvailable columns:")
    for col in df.columns:
        print(f"  - {col}")
    print()






    # 4. Prompt for X and Y
    x_col = ask_column("Enter the column name for the X variable: ", df.columns)
    y_col = ask_column("Enter the column name for the Y variable: ", df.columns)



    # 5. Remove rows missing either value (non-numeric entries are treated as missing)
    data = df[[x_col, y_col]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        print("Not enough valid numeric rows to run a regression.")
        return
    print(f"{len(data)} rows remain after removing missing/non-numeric values.")




    # 6. Scatterplot without regression line
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(data[x_col], data[y_col], alpha=0.6, edgecolors="k", linewidths=0.3)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_title(f"{y_col} vs {x_col} (n = {len(data)})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    plt.show(block=False)
    plt.pause(0.5)





    # 7. Optionally save scatterplot
    if ask_yes_no("Save the scatterplot (no regression line)?"):
        save_figure(fig, f"{x_col}_vs_{y_col}_scatter.png")




    # 8. OLS regression
    X = sm.add_constant(data[x_col])
    model = sm.OLS(data[y_col], X).fit()
    print("\nOLS Regression Summary:")
    print(model.summary())




    # 9. Add regression line to the scatterplot
    x_line = np.linspace(data[x_col].min(), data[x_col].max(), 100)
    y_line = model.params["const"] + model.params[x_col] * x_line
    ax.plot(x_line, y_line, color="crimson", linewidth=2,
            label=f"OLS line (R² = {model.rsquared:.3f})")
    ax.set_title(f"{y_col} vs {x_col} with OLS line (n = {len(data)})")
    ax.legend()
    fig.canvas.draw_idle()
    plt.pause(0.5)




    # 10. Optionally save scatterplot with OLS line
    if ask_yes_no("Save the scatterplot with the OLS regression line?"):
        save_figure(fig, f"{x_col}_vs_{y_col}_ols.png")

    plt.show()





if __name__ == "__main__":
    main()