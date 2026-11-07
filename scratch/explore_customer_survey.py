import pandas as pd

survey = pd.read_csv('data files/customer_survey.csv')
print("Columns:", survey.columns.tolist())
print("Shape:", survey.shape)
print("\n=== SURVEY SUMMARY STATS ===")
for col in survey.columns:
    if survey[col].dtype in ['int64', 'float64']:
        print(f"{col}: mean={survey[col].mean():.2f}, min={survey[col].min()}, max={survey[col].max()}")
    elif survey[col].nunique() < 10:
        print(f"\n{col}:\n{survey[col].value_counts()}")

print("\n=== SAMPLE COMMENTS / OPEN TEXT ===")
text_cols = [c for c in survey.columns if survey[c].dtype == 'object' and survey[c].nunique() > 10]
for tc in text_cols:
    print(f"\n--- Column: {tc} ---")
    print(survey[tc].dropna().head(10).tolist())

