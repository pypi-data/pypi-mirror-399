"""
Real Estate Analysis Example
Demonstrates Histogram PCA with property data

This example generates sample data automatically - no CSV files needed!
"""

import pandas as pd
import numpy as np
from histopca import prep_histogram, ridit_score_centered, histogram_pca_r_compatible


def generate_real_estate_data(n_per_type=100, seed=42):
    """
    Generate sample real estate data for testing
    
    Parameters:
    -----------
    n_per_type : int
        Number of properties per type (default: 100)
    seed : int
        Random seed for reproducibility (default: 42)
    
    Returns:
    --------
    pd.DataFrame
        Sample real estate data with columns:
        - Property Type: Single Family, Condo, Townhouse
        - Price: Property price ($)
        - Square Footage: Living area (sq ft)
        - Bedrooms: Number of bedrooms
        - Bathrooms: Number of bathrooms
        - Acreage: Land size (acres)
    """
    np.random.seed(seed)
    
    # Create arrays for each property type
    property_types = []
    prices = []
    square_footages = []
    bedrooms = []
    bathrooms = []
    acreages = []
    
    # Single Family homes
    property_types.extend(['Single Family'] * n_per_type)
    prices.extend(np.random.normal(850000, 250000, n_per_type))
    square_footages.extend(np.random.normal(2600, 600, n_per_type))
    bedrooms.extend(np.random.choice([3, 4, 5], n_per_type, p=[0.3, 0.5, 0.2]))
    bathrooms.extend(np.random.choice([2, 3, 4], n_per_type, p=[0.4, 0.4, 0.2]))
    acreages.extend(np.random.uniform(0.15, 0.5, n_per_type))
    
    # Condos
    property_types.extend(['Condo'] * n_per_type)
    prices.extend(np.random.normal(420000, 120000, n_per_type))
    square_footages.extend(np.random.normal(1100, 250, n_per_type))
    bedrooms.extend(np.random.choice([1, 2, 3], n_per_type, p=[0.3, 0.5, 0.2]))
    bathrooms.extend(np.random.choice([1, 2], n_per_type, p=[0.6, 0.4]))
    acreages.extend(np.random.uniform(0.0, 0.05, n_per_type))
    
    # Townhouses
    property_types.extend(['Townhouse'] * n_per_type)
    prices.extend(np.random.normal(650000, 180000, n_per_type))
    square_footages.extend(np.random.normal(1750, 350, n_per_type))
    bedrooms.extend(np.random.choice([2, 3, 4], n_per_type, p=[0.3, 0.5, 0.2]))
    bathrooms.extend(np.random.choice([2, 3], n_per_type, p=[0.6, 0.4]))
    acreages.extend(np.random.uniform(0.05, 0.15, n_per_type))
    
    # Create DataFrame
    data = pd.DataFrame({
        'Property Type': property_types,
        'Price': prices,
        'Square Footage': square_footages,
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms,
        'Acreage': acreages
    })
    
    # Ensure positive prices
    data['Price'] = data['Price'].clip(lower=100000)
    
    return data


def main():
    """Run the real estate Histogram PCA example"""
    
    print("="*80)
    print("REAL ESTATE HISTOGRAM PCA EXAMPLE")
    print("="*80)
    
    # Generate sample data
    print("\nGenerating sample real estate data...")
    data = generate_real_estate_data(n_per_type=100)
    print(f"✓ Generated {len(data)} sample properties")
    
    # Show data summary
    property_type_counts = data['Property Type'].value_counts()
    print(f"\nProperty type distribution:")
    for ptype, count in property_type_counts.items():
        print(f"  {ptype}: {count} properties")
    
    print(f"\nData summary:")
    print(f"  Property types: {len(property_type_counts)} types")
    print(f"  Total properties: {len(data)}")
    print(f"  Price range: ${data['Price'].min():,.0f} - ${data['Price'].max():,.0f}")
    print(f"  Size range: {data['Square Footage'].min():.0f} - {data['Square Footage'].max():.0f} sq ft")
    print(f"  Bedrooms range: {data['Bedrooms'].min()} - {data['Bedrooms'].max()}")
    print(f"  Bathrooms range: {data['Bathrooms'].min()} - {data['Bathrooms'].max()}")
    print(f"  Acreage range: {data['Acreage'].min():.2f} - {data['Acreage'].max():.2f} acres")
    
    # Create histograms (5 variables, grouped by Property Type)
    print("\n" + "-"*80)
    print("STEP 1: Creating Histograms")
    print("-"*80)
    
    print("Creating histograms with k=5 bins...")
    Hist1 = prep_histogram(
        X=data['Price'].values, 
        Z=data['Property Type'].values, 
        k=5
    )['Vhistogram']
    print(f"  ✓ Price histogram: {Hist1.shape} (groups × bins)")
    
    Hist2 = prep_histogram(
        X=data['Square Footage'].values, 
        Z=data['Property Type'].values, 
        k=5
    )['Vhistogram']
    print(f"  ✓ Square Footage histogram: {Hist2.shape}")
    
    Hist3 = prep_histogram(
        X=data['Bedrooms'].values, 
        Z=data['Property Type'].values, 
        k=5
    )['Vhistogram']
    print(f"  ✓ Bedrooms histogram: {Hist3.shape}")
    
    Hist4 = prep_histogram(
        X=data['Bathrooms'].values, 
        Z=data['Property Type'].values, 
        k=5
    )['Vhistogram']
    print(f"  ✓ Bathrooms histogram: {Hist4.shape}")
    
    Hist5 = prep_histogram(
        X=data['Acreage'].values, 
        Z=data['Property Type'].values, 
        k=5
    )['Vhistogram']
    print(f"  ✓ Acreage histogram: {Hist5.shape}")
    
    # Calculate ridit scores
    print("\n" + "-"*80)
    print("STEP 2: Calculating Ridit Scores")
    print("-"*80)
    
    print("Calculating ridit scores for all variables...")
    scores = [
        ridit_score_centered(Hist1),
        ridit_score_centered(Hist2),
        ridit_score_centered(Hist3),
        ridit_score_centered(Hist4),
        ridit_score_centered(Hist5)
    ]
    print("  ✓ All ridit scores calculated")
    
    # Run Histogram PCA
    print("\n" + "-"*80)
    print("STEP 3: Running Histogram PCA")
    print("-"*80)
    
    print("Performing R-compatible Histogram PCA with visualization...\n")
    
    results = histogram_pca_r_compatible(
        variables=[Hist1, Hist2, Hist3, Hist4, Hist5],
        scores=scores,
        col_names=['Price', 'Square_Footage', 'Bedrooms', 'Bathrooms', 'Acreage'],
        row_names=list(Hist1.index),
        plotgraph=True
    )
    
    # Display results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    print("\n1. Variance Explained by Each Component:")
    print("-" * 40)
    var_df = results['PourCentageComposante']
    percentages = var_df['percentage of variance'].values
    for i, var in enumerate(percentages, 1):
        print(f"   PC{i}: {var:6.2f}%")
    
    print("\n2. Variable Loadings on PC1:")
    print("-" * 40)
    loadings = results['Correlation']
    for i, var_name in enumerate(['Price', 'Square_Footage', 'Bedrooms', 'Bathrooms', 'Acreage']):
        loading = loadings.iloc[i, 0]
        print(f"   {var_name:18s}: {loading:6.3f}")
    
    print("\n3. Property Type Positions on PC1:")
    print("-" * 40)
    pc_intervals = results['PCinterval']
    pc1_centers = (pc_intervals['PCMin.1'] + pc_intervals['PCMax.1']) / 2
    
    # Sort by score
    score_data = list(zip(pc1_centers.index, pc1_centers.values))
    score_data.sort(key=lambda x: x[1], reverse=True)
    
    for prop_type, score in score_data:
        print(f"   {prop_type:18s}: {score:7.3f}")
    
    print("\n4. Interpretation:")
    print("-" * 40)
    print(f"   PC1 explains {percentages[0]:.1f}% of the variance")
    print(f"   PC1 represents the 'size and value' dimension")
    print(f"   ")
    print(f"   Highest PC1: {score_data[0][0]}")
    print(f"     → Larger, more expensive properties")
    print(f"   Lowest PC1:  {score_data[-1][0]}")
    print(f"     → Smaller, more affordable properties")
    
    print("\n" + "="*80)
    print("✅ EXAMPLE COMPLETE!")
    print("="*80)
    print("\nGenerated outputs:")
    print("  - R-style factorial plan (left plot)")
    print("  - Correlation circle (right plot)")
    print("\nWhat the plots show:")
    print("  - Factorial plan: How property types differ on PC1 and PC2")
    print("  - Correlation circle: How variables relate to the principal components")
    print("\nNext steps:")
    print("  - Adjust sample size: change n_per_type parameter")
    print("  - Adjust number of bins: change k parameter")
    print("  - Try with your own data: replace generate_real_estate_data()")
    print("\nTo save this generated data:")
    print("  data = generate_real_estate_data()")
    print("  data.to_csv('my_sample_data.csv', index=False)")


if __name__ == "__main__":
    main()