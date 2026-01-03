## 🚀 Quick Start
```python
import pandas as pd
from histopca import prep_histogram, ridit_score_centered, histogram_pca_r_compatible

# Load your data
data = pd.read_csv("your_data.csv")

# Create histograms from your variables
Hist1 = prep_histogram(X=data['price'].values, Z=data['category'].values, k=5)['Vhistogram']
Hist2 = prep_histogram(X=data['size'].values, Z=data['category'].values, k=5)['Vhistogram']
Hist3 = prep_histogram(X=data['rating'].values, Z=data['category'].values, k=5)['Vhistogram']

# Calculate ridit scores
score1 = ridit_score_centered(Hist1)
score2 = ridit_score_centered(Hist2)
score3 = ridit_score_centered(Hist3)

# Run PCA with automatic visualization
results = histogram_pca_r_compatible(
    variables=[Hist1, Hist2, Hist3],
    scores=[score1, score2, score3],
    col_names=['Price', 'Size', 'Rating'],
    row_names=list(Hist1.index),
    plotgraph=True
)

# View results
print(results['PourCentageComposante'])  # Variance explained
print(results['Correlation'])            # Variable loadings
```

📖 **For detailed examples, see [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md)**

## 📊 Examples

### Real Estate Analysis
Analyze property distributions by type:
```python
from histopca import prep_histogram, ridit_score_centered, histogram_pca_r_compatible

# Create histograms for 5 variables
Hist_Price = prep_histogram(X=data['Price'].values, Z=data['Property Type'].values, k=5)['Vhistogram']
Hist_Size = prep_histogram(X=data['Square Footage'].values, Z=data['Property Type'].values, k=5)['Vhistogram']
Hist_Beds = prep_histogram(X=data['Bedrooms'].values, Z=data['Property Type'].values, k=5)['Vhistogram']
Hist_Baths = prep_histogram(X=data['Bathrooms'].values, Z=data['Property Type'].values, k=5)['Vhistogram']
Hist_Acre = prep_histogram(X=data['Acreage'].values, Z=data['Property Type'].values, k=5)['Vhistogram']

# Calculate scores and run PCA
scores = [ridit_score_centered(h) for h in [Hist_Price, Hist_Size, Hist_Beds, Hist_Baths, Hist_Acre]]
results = histogram_pca_r_compatible(
    variables=[Hist_Price, Hist_Size, Hist_Beds, Hist_Baths, Hist_Acre],
    scores=scores,
    col_names=['Price', 'Size', 'Bedrooms', 'Bathrooms', 'Acreage'],
    row_names=list(Hist_Price.index),
    plotgraph=True
)
```

**See [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md) for more examples:**
- Customer purchase analysis
- Product performance by category
- Time series by region