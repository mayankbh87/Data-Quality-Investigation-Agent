import pandas as pd, numpy as np, os
np.random.seed(11)
os.makedirs("data", exist_ok=True)
n = 300
df = pd.DataFrame({
    "txn_id": [f"T{i:05d}" for i in range(n)],
    "account_id": [f"A{np.random.randint(1, 80):04d}" for _ in range(n)],
    "amount": np.round(np.random.normal(250, 60, n), 2).astype(object),
    "currency": np.random.choice(["USD", "usd", "US$", "INR", "inr"], n),
    "txn_date": pd.date_range("2025-01-01", periods=n).strftime("%Y-%m-%d").astype(object),
    "status": np.random.choice(["completed", "Completed", "COMPLETE", "failed"], n),
})
df.loc[:89, "account_id"] = ""            # 30% orphan transactions
df.loc[100:114, "amount"] = "1,250.00"    # numbers stored as text
df.loc[120:124, "amount"] = 9999999.0    # extreme outliers
df.loc[130:149, "amount"] = -250.0       # negative amounts
df.loc[160:174, "txn_date"] = "2031-06-30"  # future dates
df.loc[180:184, "txn_date"] = "30/06/2025"  # mixed date format
df.loc[250:259, "txn_id"] = "T00001"     # duplicate primary key
df = pd.concat([df, df.iloc[200:225]])   # 25 exact duplicate rows
df.to_csv("data/transactions.csv", index=False)
print("Created data/transactions.csv")