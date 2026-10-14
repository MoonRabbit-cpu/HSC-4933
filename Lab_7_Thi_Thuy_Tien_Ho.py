# LINEAR REGRESSION LAB # LAB.7, 2026 (C)  #
# Thi Thuy Tien Ho # thithuytienho@usf.edu #
# ------------------------------------------#

# imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

# prompt user for dataset
CSV_PATH = input("Enter the dataset filename: ").strip()

# load csv
df = pd.read_csv(CSV_PATH)

# Clean column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

for column in df.columns:
    if df[column].name == "rownames":
        df.drop(column, axis=1, inplace=True)

# List available column names
print(f"\nAvailable column names:")
for column in df.columns:
    print(column)

# Prompt user for X and Y variables
X_COL = input("\nEnter the X variable:").strip().lower()
Y_COL = input("Enter the Y variable:").strip().lower()

# Make sure the column exist
if X_COL not in df.columns or Y_COL not in df.columns:
    print("Error: One of both column names were not found.")
    raise SystemExit

# Select The X and Y columns
data = df[[X_COL, Y_COL]].copy()

# Remove commas from numeric values
data[X_COL] = data[X_COL].astype(str).str.replace(",", "", regex=False)
data[Y_COL] = data[Y_COL].astype(str).str.replace(",", "", regex=False)

# Convert the selected columns to numeric values
data[X_COL] = pd.to_numeric(data[X_COL], errors="coerce")
data[Y_COL] = pd.to_numeric(data[Y_COL], errors="coerce")

# Remove rows missing for X and Y variables
data = data.dropna()

# Display available rows
print(f"\nRows available for regrission: {len(data)}")

# Create scatterplot
fig, ax = plt.subplots(figsize=(8, 6))

ax.scatter(data[X_COL], data[Y_COL], alpha=0.6, edgecolor="k", linewidth=0.3)

ax.set_xlabel(X_COL)
ax.set_ylabel(Y_COL)
ax.set_title(f"{Y_COL} vs {X_COL} (n ={len(data)})")
ax.grid(alpha=0.3)

fig.tight_layout()

# Ask user if they want to save the scatterplot
save_scatter = input("\nWould you like to save the scatterplot? (yes/no):").strip().lower()
if save_scatter == "yes":
    scatter_file = f"{X_COL}vs_{Y_COL}.png"

    fig.savefig(scatter_file, dpi=300)
    print(f"saved scatterplot -> {scatter_file}")

# perform linear regression
X = sm.add_constant(data[X_COL])
model = sm.OLS(data[Y_COL], X).fit()

# print regression summary
print("\nOLS Regression Summary: ")
print(model.summary())

# Print regression values
print(f"Beta O (intercept): {model.params['const']:.4f}")
print(f"Beta 1(slope): {model.params[X_COL]:.4f}")
print(f"R²: {model.rsquared:.4f}")

# Create a separate scatterplot with OLS line
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(data[X_COL], data[Y_COL], alpha=0.6, edgecolor="k", linewidth=0.3)

# make new scatterplot with regression line
x_line = np.linspace(data[X_COL].min(), data[X_COL].max(), 100)
y_line = model.params["const"] + model.params[X_COL] * x_line
ax.plot(x_line, y_line, color="crimson", linewidth=2, label=f"OLS line (R² = {model.rsquared:.3f})")
ax.set_title(f"{Y_COL} vs. {X_COL} with OLS line (n= {len(data)})")
ax.legend()

# Ask user if they want to save OLS scatterplot
save_ols = input("\nWould you like to save the scatterplot with the OLS line? (yes/no):").strip().lower()
if save_ols == "yes":
    ols_file = input("Enter a custom filename for the OLS scatterplot:").strip()
    if not ols_file.endswith(".png"):
        ols_file += ".png"

    fig.savefig(ols_file, dpi=300)
    print(f"saved scatterplot with OLS line -> {ols_file}")

# display OLS regression
plt.show()