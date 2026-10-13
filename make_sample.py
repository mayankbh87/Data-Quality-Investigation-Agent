import pandas as pd, numpy as np, os
np.random.seed(7)
os.makedirs("data", exist_ok=True)
n = 200
df = pd.DataFrame({
    "customer_id": range(1, n + 1),
    "name": [f"Customer {i}" for i in range(n)],
    "email": [f"user{i}@example.com" for i in range(n)],
    "country": np.random.choice(["India", "india ", "USA", "U.S.A", "UK"], n),
    "age": np.random.randint(18, 70, n).astype(object),
    "signup_date": pd.date_range("2023-01-01", periods=n).strftime("%Y-%m-%d").astype(object),
    "order_value": np.round(np.random.normal(100, 25, n), 2).astype(object),
})
df.loc[5:14, "email"] = ""                 # missing
df.loc[20, "age"] = "twenty-five"          # type inconsistency
df.loc[21, "age"] = 250                    # impossible value
df.loc[30, "order_value"] = 99999.0        # outlier
df.loc[31, "order_value"] = -50            # negative
df.loc[40, "signup_date"] = "15/03/2023"   # mixed date format
df = pd.concat([df, df.iloc[[0, 1, 2]]])   # exact duplicates
df.loc[50, "customer_id"] = 51             # duplicate key
df.to_csv("data/customers.csv", index=False)
print("Created data/customers.csv")