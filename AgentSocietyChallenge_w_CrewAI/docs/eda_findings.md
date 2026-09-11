# Exploratory Data Analysis (EDA) - Yelp Context

EDA is the process of performing initial investigations on data so as to discover patterns, spot anomalies, and test hypotheses.

## Yelp Specific EDA Patterns
- **Rating Distribution**: Often shows a bi-modal distribution (many 1s and 5s).
- **Review Sparsity**: Most users only review 1 or 2 restaurants; identifying "power users" is key.
- **Seasonal Influence**: Dining habits change during holidays or specific seasons.
- **Geospatial Concentration**: Restaurants in specific clusters (like "Strip" in Las Vegas) behave differently from rural ones.
- **Sentiment-Star Gap**: Sometimes a user writes a positive review but gives 3 stars; identifying this nuance helps in prediction.

## Analytical Checklist:
1. Check for missing values in business attributes.
2. Correlate "Useful" votes with review length.
3. Compare User's `average_stars` with the business's `stars`.
