# HistoPCA Usage Guide: From Your Data to Results

This guide shows you how to transform **any CSV data** into histograms and run Histogram PCA analysis.

## 🎯 What You Need

1. **A CSV file** with:
   - Numeric variables (continuous data like price, size, age, etc.)
   - A categorical grouping variable (like city, product type, customer segment)

2. **Python packages**:
```bash
pip install histopca pandas numpy matplotlib
```

## 📊 Step-by-Step Tutorial

### Step 1: Load Your Data
```python
import pandas as pd
import numpy as np
from histopca import (
    prep_histogram,
    ridit_score_centered,
    histogram_pca_r_compatible,
    display_all_histograms
)

# Load your CSV file
data = pd.read_csv("your_data.csv")

# Preview your data
print(data.head())
print(data.columns)
```

### Step 2: Clean Your Data (Optional but Recommended)
```python
# Remove missing values
data = data.dropna()

# Filter outliers (example: remove extreme prices)
data = data[data['Price'] <= 5000000]
data = data[data['Price'] > 0]

# Check your grouping variable
print(data['Property Type'].value_counts())
```

### Step 3: Create Histograms from Your Variables

**Key Parameters:**
- `X`: Your numeric variable (e.g., price, age, size)
- `Z`: Your grouping variable (e.g., category, region, type)
- `k`: Number of histogram bins (typically 5-10)

**Example with Real Estate Data:**
```python
# Create histograms for each variable you want to analyze
# Each histogram shows the distribution for each group

Hist_Price = prep_histogram(
    X=data['Price'].values,           # Numeric variable
    Z=data['Property Type'].values,   # Grouping variable
    k=5                                # Number of bins
)['Vhistogram']

Hist_Size = prep_histogram(
    X=data['Square Footage'].values,
    Z=data['Property Type'].values,
    k=5
)['Vhistogram']

Hist_Bedrooms = prep_histogram(
    X=data['Bedrooms'].values,
    Z=data['Property Type'].values,
    k=5
)['Vhistogram']

Hist_Bathrooms = prep_histogram(
    X=data['Bathrooms'].values,
    Z=data['Property Type'].values,
    k=5
)['Vhistogram']

Hist_Acreage = prep_histogram(
    X=data['Acreage'].values,
    Z=data['Property Type'].values,
    k=5
)['Vhistogram']

print(f"Created histograms: {Hist_Price.shape}")
# Output: (3, 5) means 3 groups, 5 bins each
```

### Step 4: Calculate Ridit Scores

Ridit scores transform histogram data into a standardized form for PCA:
```python
score_price = ridit_score_centered(Hist_Price)
score_size = ridit_score_centered(Hist_Size)
score_beds = ridit_score_centered(Hist_Bedrooms)
score_baths = ridit_score_centered(Hist_Bathrooms)
score_acre = ridit_score_centered(Hist_Acreage)

print("✓ Ridit scores calculated")
```

### Step 5: Run Histogram PCA
```python
results = histogram_pca_r_compatible(
    variables=[Hist_Price, Hist_Size, Hist_Bedrooms, Hist_Bathrooms, Hist_Acreage],
    scores=[score_price, score_size, score_beds, score_baths, score_acre],
    col_names=['Price', 'Square_Footage', 'Bedrooms', 'Bathrooms', 'Acreage'],
    row_names=list(Hist_Price.index),  # Your group names
    plotgraph=True  # Creates visualization
)
```

### Step 6: Interpret Results
```python
# Variance explained by each component
print("\nVariance Explained:")
print(results['PourCentageComposante'])

# Variable loadings (correlations with PCs)
print("\nVariable Loadings on PC1:")
print(results['Correlation'].iloc[:, 0])

# Group positions on principal components
print("\nPC Intervals:")
print(results['PCinterval'])
```

---

## 🔄 Adapting to YOUR Data

### Example 1: Customer Purchase Analysis
```python
# Your CSV: customers.csv
# Columns: customer_id, region, age, income, purchases, tenure

data = pd.read_csv("customers.csv")

# Create histograms for each metric by region
Hist_Age = prep_histogram(
    X=data['age'].values,
    Z=data['region'].values,  # Group by region
    k=5
)['Vhistogram']

Hist_Income = prep_histogram(
    X=data['income'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

Hist_Purchases = prep_histogram(
    X=data['purchases'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

Hist_Tenure = prep_histogram(
    X=data['tenure'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

# Calculate scores
score_age = ridit_score_centered(Hist_Age)
score_income = ridit_score_centered(Hist_Income)
score_purchases = ridit_score_centered(Hist_Purchases)
score_tenure = ridit_score_centered(Hist_Tenure)

# Run PCA
results = histogram_pca_r_compatible(
    variables=[Hist_Age, Hist_Income, Hist_Purchases, Hist_Tenure],
    scores=[score_age, score_income, score_purchases, score_tenure],
    col_names=['Age', 'Income', 'Purchases', 'Tenure'],
    row_names=list(Hist_Age.index),
    plotgraph=True
)
```

### Example 2: Product Performance by Category
```python
# Your CSV: products.csv
# Columns: product_id, category, price, rating, sales, reviews

data = pd.read_csv("products.csv")

# Create histograms by product category
Hist_Price = prep_histogram(
    X=data['price'].values,
    Z=data['category'].values,  # Group by category
    k=5
)['Vhistogram']

Hist_Rating = prep_histogram(
    X=data['rating'].values,
    Z=data['category'].values,
    k=5
)['Vhistogram']

Hist_Sales = prep_histogram(
    X=data['sales'].values,
    Z=data['category'].values,
    k=5
)['Vhistogram']

# Calculate scores and run PCA
score_price = ridit_score_centered(Hist_Price)
score_rating = ridit_score_centered(Hist_Rating)
score_sales = ridit_score_centered(Hist_Sales)

results = histogram_pca_r_compatible(
    variables=[Hist_Price, Hist_Rating, Hist_Sales],
    scores=[score_price, score_rating, score_sales],
    col_names=['Price', 'Rating', 'Sales'],
    row_names=list(Hist_Price.index),
    plotgraph=True
)
```

### Example 3: Time Series by Region
```python
# Your CSV: sales_data.csv
# Columns: date, region, revenue, customers, orders, avg_order

data = pd.read_csv("sales_data.csv")

# Create histograms by region
Hist_Revenue = prep_histogram(
    X=data['revenue'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

Hist_Customers = prep_histogram(
    X=data['customers'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

Hist_Orders = prep_histogram(
    X=data['orders'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

Hist_AvgOrder = prep_histogram(
    X=data['avg_order'].values,
    Z=data['region'].values,
    k=5
)['Vhistogram']

# Run analysis
score_rev = ridit_score_centered(Hist_Revenue)
score_cust = ridit_score_centered(Hist_Customers)
score_ord = ridit_score_centered(Hist_Orders)
score_avg = ridit_score_centered(Hist_AvgOrder)

results = histogram_pca_r_compatible(
    variables=[Hist_Revenue, Hist_Customers, Hist_Orders, Hist_AvgOrder],
    scores=[score_rev, score_cust, score_ord, score_avg],
    col_names=['Revenue', 'Customers', 'Orders', 'Avg_Order'],
    row_names=list(Hist_Revenue.index),
    plotgraph=True
)
```

---

## 📊 Visualizing Individual Histograms

Before running PCA, you can visualize your histograms:
```python
from histopca import display_all_histograms
import matplotlib.pyplot as plt

# Display histogram for one variable
display_all_histograms(
    Hist_Price,
    title="Price Distribution by Property Type"
)
plt.savefig('price_histograms.png')
plt.show()
```

---

## 🎯 Quick Checklist

Before creating histograms, make sure:

- [ ] Your data is loaded into a pandas DataFrame
- [ ] You have **numeric variables** (continuous data)
- [ ] You have a **grouping variable** (categorical)
- [ ] Missing values are handled
- [ ] Outliers are filtered if needed
- [ ] Each group has sufficient data points

**Minimum Requirements:**
- At least **2 groups** in your grouping variable
- At least **2 numeric variables** to analyze
- At least **20-30 observations per group** (more is better)

---

## 🚀 Complete Example Template

Copy and adapt this template for your data:
```python
import pandas as pd
from histopca import (
    prep_histogram,
    ridit_score_centered,
    histogram_pca_r_compatible
)

# 1. LOAD DATA
data = pd.read_csv("YOUR_FILE.csv")

# 2. CLEAN DATA (adjust as needed)
data = data.dropna()
# Add your filters here

# 3. CREATE HISTOGRAMS
# Replace 'Var1', 'Var2', etc. with your column names
# Replace 'Group' with your grouping column

Hist1 = prep_histogram(X=data['Var1'].values, Z=data['Group'].values, k=5)['Vhistogram']
Hist2 = prep_histogram(X=data['Var2'].values, Z=data['Group'].values, k=5)['Vhistogram']
Hist3 = prep_histogram(X=data['Var3'].values, Z=data['Group'].values, k=5)['Vhistogram']
# Add more histograms as needed

# 4. CALCULATE SCORES
score1 = ridit_score_centered(Hist1)
score2 = ridit_score_centered(Hist2)
score3 = ridit_score_centered(Hist3)
# Add more scores

# 5. RUN PCA
results = histogram_pca_r_compatible(
    variables=[Hist1, Hist2, Hist3],
    scores=[score1, score2, score3],
    col_names=['Var1', 'Var2', 'Var3'],
    row_names=list(Hist1.index),
    plotgraph=True
)

# 6. VIEW RESULTS
print("\nVariance Explained:")
print(results['PourCentageComposante'])

print("\nVariable Loadings:")
print(results['Correlation'])

print("\nGroup Positions:")
print(results['PCinterval'])
```

---

## 💡 Tips for Best Results

1. **Choose relevant variables**: Select variables that measure different aspects of your data
2. **Use appropriate bins**: Start with k=5, increase for more detail
3. **Check group sizes**: Ensure each group has enough observations
4. **Interpret PC1 first**: It explains the most variance
5. **Look for patterns**: Groups that are far apart on PC1 are very different

---

## 🔍 Understanding the Output

### Variance Explained
Shows how much information each principal component captures:
```python
print(results['PourCentageComposante'])
#   PC1: 72.26%  ← Most important
#   PC2: 18.45%  ← Second most important
#   PC3:  6.29%
```

### Variable Loadings
Shows how each variable correlates with the principal components:
```python
print(results['Correlation'])
# High positive loading (>0.7): Variable strongly associated with PC
# Near zero (~0): Variable not related to this PC
# High negative loading (<-0.7): Variable inversely associated with PC
```

### PC Intervals
Shows where each group is positioned on the principal components:
```python
print(results['PCinterval'])
# PCMin.1, PCMax.1: Range on PC1 for each group
# Groups far apart on PC1 are very different
```

---

## 🎓 When to Use Histogram PCA

**✅ Good Use Cases:**
- Comparing distributions across groups (e.g., customer segments by region)
- Analyzing interval-valued data (e.g., min-max temperature ranges)
- Working with aggregated/binned data
- Time series of distributions

**❌ When Standard PCA is Better:**
- You have individual observations (not distributions)
- Variables are already single-valued
- Simple correlation analysis is sufficient

---

## 🔗 More Resources

- **Full documentation**: [GitHub Repository](https://github.com/brahim7/foursight.ai_histopca)
- **Report issues**: [GitHub Issues](https://github.com/brahim7/foursight.ai_histopca/issues)
- **Original R package**: [HistDAWass on CRAN](https://cran.r-project.org/package=HistDAWass)


---

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue on GitHub!

Want to contribute code? Pull requests are welcome!

---

## 📧 Contact

- **Author**: Bibi Brahim, Sun Makosso Alix
- **Email**: brahim_b@foursight.ai


---

## 📝 License

AGPL License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 foursight labs, foursight.ai