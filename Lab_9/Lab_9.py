#####################################################
#Bryan Hernandez Rodriguez                          #
# Lab_8.py: Interactive Logistic / Count Regression #
# Prompts for a dataset, cleans column names,       #
# lets the user pick predictors and a response,     #
# fits a logistic or Poisson model, and optionally  #
# saves the output to a .txt file.                  #
#####################################################


# imports
import re
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


# converts column names to snake_case (lowercase, non-alphanumerics -> _)
# e.g. "CSMOKING_CrudePrev" -> "csmoking_crudeprev", "Age Years" -> "age_years"
def to_snake_case(name):
    name = str(name).strip().lower()
    name = re.sub(r"[^0-9a-z]+", "_", name)  # non-alphanumerics -> _
    return name.strip("_")


# Yes/no prompt
def ask_yes_no(prompt):
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


# prompts for the model type
def ask_model_type():
    while True:
        choice = input("Which model would you like to run? "
                       "(1 = logistic, 2 = Poisson/count): ").strip().lower()
        if choice in ("1", "logistic", "l"):
            return "logistic"
        if choice in ("2", "poisson", "count", "p", "c"):
            return "poisson"
        print("Please enter 1 (logistic) or 2 (Poisson/count).")


# prompts for a single column (the response variable)
def ask_column(prompt, columns):
    while True:
        choice = to_snake_case(input(prompt).strip())
        if choice in columns:
            return choice
        print(f"'{choice}' is not a column. Please choose from the list above.")


# prompts for several columns (the predictors), separated by commas
def ask_columns(prompt, columns, exclude):
    while True:
        raw = input(prompt).strip()
        choices = [to_snake_case(c) for c in raw.split(",") if c.strip()]
        choices = list(dict.fromkeys(choices))  # drop duplicates, keep order
        bad = [c for c in choices if c not in columns]
        if not choices:
            print("Please enter at least one column.")
        elif bad:
            print(f"Not a column: {', '.join(bad)}. Please choose from the list above.")
        elif exclude in choices:
            print(f"'{exclude}' is the response variable and can't also be a predictor.")
        else:
            return choices


# builds a confusion matrix (rows = actual, columns = predicted) and accuracy
def confusion_matrix_text(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    cm = pd.crosstab(pd.Series(y_true.values, name="Actual", index=y_true.index),
                     pd.Series(y_pred.values, name="Predicted", index=y_true.index),
                     dropna=False)
    cm = cm.reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    accuracy = (y_true.values == y_pred.values).mean()
    return (f"Confusion matrix (threshold = {threshold}):\n{cm.to_string()}\n\n"
            f"Accuracy: {accuracy:.4f}")


# variance inflation factors for the predictors (constant included in the design matrix)
def vif_text(X):
    vif = pd.DataFrame({
        "variable": X.columns,
        "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
    })
    vif = vif[vif["variable"] != "const"]
    return "Variance Inflation Factors (VIF):\n" + vif.to_string(index=False)


# file save
def save_text(text, default_name="regression_output.txt"):
    name = input(f"Enter a file name (default: {default_name}): ").strip()
    if not name:
        name = default_name
    if not name.lower().endswith(".txt"):
        name += ".txt"
    with open(name, "w", encoding="utf-8") as f:
        f.write(text)
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

    # 4. Prompt for model type, response, and predictors
    model_type = ask_model_type()
    if model_type == "logistic":
        print("\nThe response must be binary (only 0 or 1).")
    else:
        print("\nThe response must be a count (non-negative whole numbers).")
    y_col = ask_column("Enter the column name for the response (Y) variable: ", df.columns)
    x_cols = ask_columns("Enter the predictor (X) column names, separated by commas: ",
                         df.columns, exclude=y_col)

    # 5. Remove rows missing any value used (non-numeric entries are treated as missing)
    used = [y_col] + x_cols
    data = df[used].apply(pd.to_numeric, errors="coerce").dropna()
    print(f"{len(data)} of {len(df)} rows remain after removing missing/non-numeric values.")
    if len(data) <= len(x_cols) + 1:
        print("Not enough valid rows to fit this model.")
        return

    y = data[y_col]
    # validate the response for the chosen model
    if model_type == "logistic":
        if not y.isin([0, 1]).all():
            print(f"'{y_col}' has values other than 0 and 1, so logistic regression can't be used.")
            return
        if y.nunique() < 2:
            print(f"'{y_col}' only contains one value, so the model can't be fit.")
            return
    else:
        if (y < 0).any():
            print(f"'{y_col}' has negative values, so Poisson regression can't be used.")
            return
        if not np.allclose(y, y.round()):
            print(f"Note: '{y_col}' has non-whole values (e.g., prevalence rates); "
                  "fitting the Poisson model to them as given.")

    X = sm.add_constant(data[x_cols])

    # 6. Fit the model
    try:
        if model_type == "logistic":
            model = sm.GLM(y, X, family=sm.families.Binomial()).fit()
            title = "Logistic Regression"
        else:
            model = sm.GLM(y, X, family=sm.families.Poisson()).fit()
            title = "Poisson (Count-Variable) Regression"
    except Exception as e:
        print(f"Model could not be fit: {e}")
        return

    # build the report text
    parts = [
        f"{title}",
        f"Response: {y_col}",
        f"Predictors: {', '.join(x_cols)}",
        f"Rows used: {len(data)}",
        "",
        str(model.summary()),
        "",
    ]
    exp_name = "Odds ratios" if model_type == "logistic" else "Incidence rate ratios"
    parts.append(f"{exp_name} (exp of coefficients):\n{np.exp(model.params).to_string()}\n")

    if model_type == "logistic":
        parts.append(confusion_matrix_text(y, model.predict(X)))
    else:
        parts.append(vif_text(X))

    report = "\n".join(parts)
    print("\n" + report)

    # 7. Optionally save output to a .txt file
    if ask_yes_no("\nSave the output to a .txt file?"):
        save_text(report)


if __name__ == "__main__":
    main()