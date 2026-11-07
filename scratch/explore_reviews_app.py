import pandas as pd

rev = pd.read_csv('data files/customer_reviews.csv')
rev['review_date'] = pd.to_datetime(rev['review_date'])
rev['month'] = rev['review_date'].dt.to_period('M')

print("=== MONTHLY REVIEW RATINGS ===")
monthly = rev.groupby('month')['rating'].agg(['count', 'mean'])
print(monthly)

rev['text_clean'] = rev['review_text'].fillna('').str.lower()
keywords = ['app', 'oat', 'milk', 'queue', 'wait', 'clean', 'dirty', 'price', 'slow']
print("\n=== KEYWORD FREQUENCY AND AVERAGE RATING ===")
for kw in keywords:
    matches = rev['text_clean'].str.contains(kw)
    print(f"Keyword '{kw}': count={matches.sum()}, avg_rating={rev[matches]['rating'].mean():.2f}")

rev['has_app'] = rev['text_clean'].str.contains('app')
rev['has_oat'] = rev['text_clean'].str.contains('oat')

print("\n=== REVIEWS MENTIONING 'APP' BY MONTH ===")
app_m = rev[rev['has_app']].groupby('month')['rating'].agg(['count', 'mean'])
print(app_m)

print("\n=== REVIEWS MENTIONING 'OAT' BY MONTH ===")
oat_m = rev[rev['has_oat']].groupby('month')['rating'].agg(['count', 'mean'])
print(oat_m)

print("\n=== SAMPLE 'APP' REVIEWS AFTER MARCH 2, 2026 ===")
app_sample = rev[(rev['review_date'] >= '2026-03-02') & rev['has_app']].sort_values('rating').head(6)
for _, r in app_sample.iterrows():
    print(f"[{r['review_date'].strftime('%Y-%m-%d')}] Rating: {r['rating']} - {r['review_text']}")

print("\n=== SAMPLE 'OAT' REVIEWS AFTER JAN 12, 2026 ===")
oat_sample = rev[(rev['review_date'] >= '2026-01-12') & rev['has_oat']].sort_values('rating').head(6)
for _, r in oat_sample.iterrows():
    print(f"[{r['review_date'].strftime('%Y-%m-%d')}] Rating: {r['rating']} - {r['review_text']}")

