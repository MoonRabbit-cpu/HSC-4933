#####################################################
# Bryan Hernandez Rodriguez -----------             #
# IC5.py:Blood Pressure OLS Regression              #
# Creates scatterplot and performs linear           #
# regression for a given dataset, saving outputs as #
# png files and returning regression stats.         #
#####################################################

#imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

#environment variables
CSV_PATH = "Blood_Pressure_clean.csv"
X_COL = "sys_mmhg"
Y_COL = "dias_mmhg"



#load csv and perform sanity check
df = pd.read_csv(CSV_PATH)
data = df[[X_COL, Y_COL]].dropna()



#create scatterplot
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(data[X_COL], data[Y_COL], alpha=0.6, edgecolors='k', linewidths=0.3)
ax.set_xlabel(X_COL)
ax.set_ylabel(Y_COL)
ax.set_title(f"{Y_COL} vs {X_COL} (n = {len(data)})")
ax.grid(alpha=0.3)
fig.tight_layout()



#saving scatterplot
scatter_file = f"{X_COL}_vs_{Y_COL}_scatter.png"
fig.savefig(scatter_file, dpi=300)
print(f"Saved scatterplot -> {scatter_file}")


#preform linear regression
X = sm.add_constant(data[X_COL])
model = sm.OLS(data[Y_COL], X).fit()


#print regression
print("OLS Regression Summary: ")
print(model.summary())

#make new scatterplot with regression line
x_line = np.linspace(data[X_COL].min(), data[X_COL].max(), 100)
y_line = model.params["const"] + model.params[X_COL] * x_line
ax.plot(x_line, y_line, color="crimson", linewidth=2, label=f"OLS line(R² = {model.rsquared:.3f})")
ax.set_title(f"{Y_COL} vs. {X_COL} with OLS line (n = {len(data)})")
ax.legend()


#save new scatterplot
ols_file = f"{X_COL}_vs_{Y_COL}_ols.png"
fig.savefig(ols_file, dpi=300)
print(f"Saved scatterplot with OLS line -> {ols_file}")


#display OLS regression
plt.show()