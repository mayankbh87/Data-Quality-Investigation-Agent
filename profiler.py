import pandas as pd, numpy as np

MISSING = {"", "na", "n/a", "null", "none", "nan", "-", "?"}

def profile_csv(path: str) -> dict:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)  # raw text so we can detect mixed types
    out = {"rows": len(df), "columns": len(df.columns),
           "exact_duplicate_rows": int(df.duplicated().sum()), "column_profiles": {}}

    for col in df.columns:
        s = df[col]
        is_missing = s.str.strip().str.lower().isin(MISSING)
        v = s[~is_missing]
        p = {"missing_count": int(is_missing.sum()),
             "missing_pct": round(100 * is_missing.mean(), 2),
             "distinct": int(v.nunique())}

        # numeric / date parse ratios -> mixed-type detection
        num = pd.to_numeric(v, errors="coerce")
        num_ratio = num.notna().mean() if len(v) else 0
        if num_ratio == 1:
            p["inferred_type"] = "numeric"
        elif num_ratio > 0.5:
            p["inferred_type"] = "mixed_numeric"
            p["non_numeric_examples"] = v[num.isna()].unique()[:5].tolist()
        else:
            dt = pd.to_datetime(v, errors="coerce", format="mixed")
            dt_ratio = dt.notna().mean() if len(v) else 0
            if dt_ratio > 0.5:
                p["inferred_type"] = "date" if dt_ratio == 1 else "mixed_date"
                if dt_ratio < 1:
                    p["unparseable_examples"] = v[dt.isna()].unique()[:5].tolist()
                # formats check: values not matching ISO yyyy-mm-dd
                non_iso = v[~v.str.match(r"^\d{4}-\d{2}-\d{2}$")]
                if len(non_iso):
                    p["non_iso_date_examples"] = non_iso.unique()[:5].tolist()
            else:
                p["inferred_type"] = "text"

        if num_ratio > 0.5:
            x = num.dropna()
            q1, q3 = x.quantile([.25, .75]); iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            out_vals = x[(x < lo) | (x > hi)]
            p.update({"min": float(x.min()), "max": float(x.max()),
                      "mean": round(float(x.mean()), 2),
                      "negative_count": int((x < 0).sum()),
                      "iqr_outlier_count": int(len(out_vals)),
                      "iqr_outlier_examples": out_vals.head(5).tolist()})

        if p["inferred_type"] == "text" and 1 < p["distinct"] <= 50:
            norm = v.str.strip().str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
            groups = v.groupby(norm).agg(lambda g: sorted(set(g)))
            variants = [g for g in groups if len(g) > 1]
            if variants:
                p["inconsistent_category_variants"] = variants[:5]

        if "id" in col.lower() and len(v):
            p["duplicate_key_values"] = int(v.duplicated().sum())

        out["column_profiles"][col] = p
    return out