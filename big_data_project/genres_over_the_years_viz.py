import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Sparql_csv_query_genres_by_year.csv")
df.columns = ["genre", "year", "count"]

pivot = df.groupby(["year", "genre"])["count"].sum().unstack(fill_value=0)

# Smooth with a 5-year rolling average
pivot_smooth = pivot.rolling(window=5, center=True, min_periods=1).mean()

pivot_smooth.plot(figsize=(14, 6))
plt.title("BnF -Genre Evolution, 1800-2025")
plt.xlabel("Year")
plt.ylabel("Edition / year")
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig("bnf_genres.png", dpi=150)
plt.show()