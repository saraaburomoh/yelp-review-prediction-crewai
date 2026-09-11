# Yelp Dataset — Field Interpretation & Agent Strategy Guide

## What We Know From The Schema

### User Data (user_subset.json)
- `average_stars`: The user's lifetime average rating (1.0-5.0).
  Use this as the baseline anchor for prediction.
  A user with average_stars=3.96 (like Carlos) is a balanced reviewer.
- `review_count`: Active users in this subset have unusually HIGH review counts.
  High review count = experienced reviewer = more reliable rating signal.
- `elite`: Multi-year elite status signals a quality-focused, detail-oriented reviewer.
  Elite users tend to write longer, more structured reviews.
- `useful` votes: High useful count = reviews are informative, not emotional.
  These users tend toward moderate, well-reasoned ratings.
- `funny` votes: High funny count = expressive, narrative writing style.
- `fans`: High fan count = influential user, likely sets community standards.
- `yelping_since`: Veteran users (early join date) tend to have stable rating patterns.

### Business Data (item_subset.json)
- `stars` (item-level): The business's overall reputation score.
  A business with stars=3.0 (like Double Decker) is considered average/below average.
- `categories`: Critical signal for matching user preferences to business type.
  e.g. "Bars, Nightlife" attracts a different reviewer profile than "Family Dining".
- `attributes.NoiseLevel`: Loud noise level is a strong differentiator —
  users who prefer quiet dining will rate loud venues lower.
- `attributes.GoodForKids=False`: Signals adult-oriented venue.
  Family-oriented users are likely to rate these venues lower.
- `attributes.HappyHour=True`: Attracts price-sensitive reviewers.
- `attributes.RestaurantsPriceRange2`: Scale 1-4. Higher price = higher expectations.
- `attributes.Ambience`: casual/upscale/divey signals strongly predict user fit.
- `is_open`: Only predict for open businesses (is_open=1).

### Review Data (review_subset.json)
- `stars` (review-level): Ground truth label for prediction.
- `text`: Most valuable signal — use for style mimicry and sentiment calibration.
- `useful` votes on reviews: High useful = more representative review.
  Prioritize high-useful reviews when building user/item profiles.
- `date`: Recent reviews are more reliable than old ones for current business state.

## Agent Strategy Rules (Derived From Schema)

### For User Profiler:
1. Always anchor prediction on user's `average_stars` first.
2. Check if user is elite — if yes, expect balanced, quality-focused reviews.
3. Read actual review text to understand the user's writing style and vocabulary.
4. High `useful` count → user writes informative, moderate reviews.
5. High `funny` count → user writes expressive, story-driven reviews.

### For Item Analyst:
1. Item's own `stars` rating is a strong prior — predictions rarely deviate
   more than 1.5 stars from the venue's overall average.
2. `categories` determines the type of experience expected.
3. `attributes` fields (noise, ambience, parking, kids) determine user fit.
4. Check `hours` — a bar open until 3AM attracts a specific crowd.

### For Prediction Modeler:
1. Start from user's `average_stars` as the base prediction.
2. Adjust based on fit between user preferences and business attributes.
3. Use similar reviews to calibrate the adjustment direction and magnitude.
4. Final prediction should rarely be more than 1.5 stars away from
   the business's overall star rating unless strong user-specific signals exist.
5. Review text should match the user's established writing style and vocabulary.

## Observed Finding From Live Run
- User Carlos (nnImk681KaRqUVHlSfZjGQ): average_stars=3.96, 1107 reviews, elite since 2006
- Business Double Decker (-7GjicSH_rM8JeZGCXGcUg): stars=3.0, loud bar, Tampa FL
- Predicted: 3.5 stars — reasonable given user's balanced nature vs loud atmosphere mismatch