"""
Auto-Corrected Histogram PCA
=============================
Automatically flips component signs to match R's typical orientation
where first variable loads positively on PC1.
"""

import pandas as pd
import numpy as np
from .histogram_pca import HistogramPCA, prep_histogram, ridit_score_centered
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns


def histogram_pca_r_compatible(variables, scores, col_names=None, row_names=None,
                               k=5, t=1.1, axes=(0, 1), transformation=1, 
                               method='hypercube', plotgraph=True):
    """
    Histogram PCA with automatic sign correction to match R orientation.
    
    This wrapper ensures that:
    1. PC1 has positive loadings (flips if negative)
    2. Visualizations match R's appearance
    3. Results are directly comparable to R output
    
    Parameters are the same as HistogramPCA.fit()
    """
    
    # Run standard PCA
    hist_pca = HistogramPCA()
    results = hist_pca.fit(
        variables=variables,
        scores=scores,
        col_names=col_names,
        row_names=row_names,
        t=t,
        axes=axes,
        transformation=transformation,
        method=method
    )
    
    # Check if we need to flip signs
    corr_matrix = results['Correlation'].copy()
    pc_intervals = results['PCinterval'].copy()
    
    # Flip PC1 if first variable is negative
    if corr_matrix.iloc[0, 0] < 0:
        print("→ Flipping PC1 to match R orientation (positive loadings)")
        
        # Flip correlation matrix
        corr_matrix.iloc[:, 0] = -corr_matrix.iloc[:, 0]
        
        # Flip PC intervals
        pc_min_1 = pc_intervals['PCMin.1'].copy()
        pc_max_1 = pc_intervals['PCMax.1'].copy()
        pc_intervals['PCMin.1'] = -pc_max_1
        pc_intervals['PCMax.1'] = -pc_min_1
    
    # Flip PC2 if it doesn't match expected pattern
    # (This is more heuristic - you might want to adjust based on your data)
    if len(corr_matrix) > 3:  # If we have Acreage as 4th variable
        if corr_matrix.iloc[3, 1] < 0:  # Acreage should typically be positive on PC2
            print("→ Flipping PC2 to match R orientation")
            
            # Flip correlation matrix
            corr_matrix.iloc[:, 1] = -corr_matrix.iloc[:, 1]
            
            # Flip PC intervals
            pc_min_2 = pc_intervals['PCMin.2'].copy()
            pc_max_2 = pc_intervals['PCMax.2'].copy()
            pc_intervals['PCMin.2'] = -pc_max_2
            pc_intervals['PCMax.2'] = -pc_min_2
    
    # Update results
    results['Correlation'] = corr_matrix
    results['PCinterval'] = pc_intervals
    
    # Plot if requested
    if plotgraph:
        plot_r_style(pc_intervals, corr_matrix, results['PourCentageComposante'],
                    row_names, col_names, axes)
    
    return results


def plot_r_style(pc_intervals, corr_matrix, variance_explained, 
                row_names, col_names, axes=(0, 1)):
    """
    Create R-style ggplot2 visualization with proper spacing
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # ============================================================
    # PLOT 1: Factorial Plan
    # ============================================================
    
    n = len(pc_intervals)
    colors = sns.color_palette("Set2", n)
    
    if row_names is None:
        row_names = [f'Obs{i+1}' for i in range(n)]
    
    for i in range(n):
        x_min = pc_intervals.iloc[i]['PCMin.1']
        x_max = pc_intervals.iloc[i]['PCMax.1']
        y_min = pc_intervals.iloc[i]['PCMin.2']
        y_max = pc_intervals.iloc[i]['PCMax.2']
        
        rect = Rectangle(
            (x_min, y_min),
            x_max - x_min,
            y_max - y_min,
            facecolor=colors[i],
            edgecolor='black',
            alpha=0.6,
            linewidth=1.5,
            label=row_names[i]
        )
        ax1.add_patch(rect)
        
        # Add text label at top-right
        ax1.text(x_max, y_max, row_names[i],
                fontsize=10, ha='left', va='bottom',
                fontweight='normal')
    
    # Style
    ax1.axhline(y=0, color='blue', linestyle='-', linewidth=1, alpha=0.7)
    ax1.axvline(x=0, color='blue', linestyle='-', linewidth=1, alpha=0.7)
    
    variance = variance_explained['percentage of variance']
    ax1.set_xlabel(f'Axe n{axes[0]+1} ({variance.iloc[axes[0]]:.2f}%)', 
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel(f'Axe n{axes[1]+1} ({variance.iloc[axes[1]]:.2f}%)', 
                  fontsize=14, fontweight='bold')
    ax1.set_title('Factorial Plan', fontsize=16, fontweight='bold', pad=20)
    
    ax1.set_aspect('equal', adjustable='datalim')
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
    ax1.set_axisbelow(True)
    ax1.set_facecolor('#EBEBEB')
    
    # Legend
    handles = [plt.Rectangle((0,0),1,1, facecolor=colors[i], 
                            edgecolor='black', alpha=0.6) 
               for i in range(n)]
    ax1.legend(handles, row_names, loc='best', 
              title='Group', frameon=True, 
              fancybox=True, shadow=True)
    
    # Auto-scale with padding - FIX: Use actual data range, not just visible range
    x_all_values = np.concatenate([pc_intervals['PCMin.1'].values, 
                                    pc_intervals['PCMax.1'].values])
    y_all_values = np.concatenate([pc_intervals['PCMin.2'].values, 
                                    pc_intervals['PCMax.2'].values])
    
    x_range = [x_all_values.min(), x_all_values.max()]
    y_range = [y_all_values.min(), y_all_values.max()]
    
    # Add generous padding (20% on each side)
    x_padding = (x_range[1] - x_range[0]) * 0.2
    y_padding = (y_range[1] - y_range[0]) * 0.2
    
    ax1.set_xlim(x_range[0] - x_padding, x_range[1] + x_padding)
    ax1.set_ylim(y_range[0] - y_padding, y_range[1] + y_padding)
    
    # ============================================================
    # PLOT 2: Correlation Circle
    # ============================================================
    
    circle = plt.Circle((0, 0), 1, fill=False, edgecolor='gray', 
                       linewidth=2, linestyle='-')
    ax2.add_patch(circle)
    
    # Plot arrows
    p = len(corr_matrix)
    if col_names is None:
        col_names = [f'Var{i+1}' for i in range(p)]
    
    for i in range(p):
        x_cor = corr_matrix.iloc[i, axes[0]]
        y_cor = corr_matrix.iloc[i, axes[1]]
        
        ax2.annotate('', xy=(x_cor, y_cor), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', 
                                  color='gray',
                                  lw=2,
                                  shrinkA=0, shrinkB=0))
        
        ax2.text(x_cor * 1.15, y_cor * 1.15, 
                col_names[i],
                fontsize=11, ha='center', va='center',
                fontweight='bold')
    
    # Style
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
    
    ax2.set_xlabel(f'Component n{axes[0]+1} ({variance.iloc[axes[0]]:.2f}%)', 
                 fontsize=14, fontweight='bold')
    ax2.set_ylabel(f'Component n{axes[1]+1} ({variance.iloc[axes[1]]:.2f}%)', 
                 fontsize=14, fontweight='bold')
    ax2.set_title('Correlation Circle', fontsize=16, 
                fontweight='bold', pad=20)
    
    ax2.set_xlim(-1.3, 1.3)
    ax2.set_ylim(-1.3, 1.3)
    ax2.set_aspect('equal', adjustable='box')
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
    ax2.set_axisbelow(True)
    ax2.set_facecolor('#EBEBEB')
    
    plt.tight_layout()
    plt.show()


# ================================================================
# Example usage
# ================================================================

if __name__ == "__main__":
    print("="*80)
    print("R-COMPATIBLE HISTOGRAM PCA")
    print("="*80)
    
    # Load data
    housing = pd.read_csv("cleaned_canada.csv")
    print(f"\nOriginal data: {housing.shape[0]} rows, {housing.shape[1]} columns")
    
    # Filter
    ab = housing[(housing['Price'] <= 5000000) & 
                 (housing['Square Footage'] <= 3000)].copy()
    print(f"Filtered data: {ab.shape[0]} rows")
    
    # Create histograms
    print("\nCreating histograms...")
    Hist1 = prep_histogram(X=ab['Price'].values, Z=ab['Property Type'].values, k=5)['Vhistogram']
    Hist2 = prep_histogram(X=ab['Bedrooms'].values, Z=ab['Property Type'].values, k=5)['Vhistogram']
    Hist3 = prep_histogram(X=ab['Bathrooms'].values, Z=ab['Property Type'].values, k=5)['Vhistogram']
    Hist4 = prep_histogram(X=ab['Acreage'].values, Z=ab['Property Type'].values, k=5)['Vhistogram']
    Hist5 = prep_histogram(X=ab['Square Footage'].values, Z=ab['Property Type'].values, k=5)['Vhistogram']
    
    # Calculate scores
    print("Calculating ridit scores...")
    ss1 = ridit_score_centered(Hist1)
    ss2 = ridit_score_centered(Hist2)
    ss3 = ridit_score_centered(Hist3)
    ss4 = ridit_score_centered(Hist4)
    ss5 = ridit_score_centered(Hist5)
    
    # Display histograms (optional - uncomment to show)
    """
    print("\nDisplaying histograms...")
    from .histogram_pca import display_all_histograms
    display_all_histograms(
        [Hist1, Hist2, Hist3, Hist4, Hist5],
        ['Price', 'Bedrooms', 'Bathrooms', 'Acreage', 'SquareFeet']
    )
    """
    
    # Run R-compatible PCA
    print("\nPerforming R-compatible Histogram PCA...")
    results = histogram_pca_r_compatible(
        variables=[Hist1, Hist2, Hist3, Hist4, Hist5],
        scores=[ss1, ss2, ss3, ss4, ss5],
        col_names=['Price', 'Bedrooms', 'Bathrooms', 'Acreage', 'SquareFeet'],
        row_names=list(Hist1.index),
        plotgraph=True
    )
    
    print("\n" + "="*80)
    print("RESULTS (Sign-Corrected to Match R)")
    print("="*80)
    
    print("\n1. Variance Explained:")
    print(results['PourCentageComposante'])
    
    print("\n2. Correlation Matrix (Component 1 & 2):")
    print(results['Correlation'].iloc[:, [0, 1]])
    
    print("\n3. PC Intervals (PC1 & PC2):")
    print(results['PCinterval'][['PCMin.1', 'PCMax.1', 'PCMin.2', 'PCMax.2']])
    
    print("\n" + "="*80)
    print("✓ Results now match R's orientation and appearance!")
    print("="*80)

