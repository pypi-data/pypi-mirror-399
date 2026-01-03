"""
HistoPCA - Histogram-based Principal Component Analysis
========================================================

A Python implementation of Histogram PCA for analyzing distributional data.

Key Features:
- Histogram-based PCA for interval/distributional data
- Compatible with R's HistDAWass implementation
- Automatic sign correction for R compatibility
- Visualization tools
- Ridit scoring for categorical data

Example Usage:
-------------
```python
from histopca import HistogramPCA, prep_histogram, ridit_score_centered

# Prepare histograms
hist1 = prep_histogram(X=data['variable1'], Z=data['groups'], k=5)
score1 = ridit_score_centered(hist1['Vhistogram'])

# Run PCA
pca = HistogramPCA()
results = pca.fit(
    variables=[hist1['Vhistogram']],
    scores=[score1],
    col_names=['Variable1'],
    row_names=list(hist1['Vhistogram'].index)
)

# Access results
print(results['PourCentageComposante'])  # Variance explained
print(results['Correlation'])  # Variable loadings
print(results['PCinterval'])  # PC intervals for each observation
```

"""

__version__ = "0.1.2"
__author__ = "Bibi Brahim and Sun Makosso Alix"
__authors__ = "Bibi Brahim and Sun Makosso Alix"
__email__ = "brahim_b@foursight.ai"
__maintainer__ = "Bibi Brahim"
__license__ = "AGPL-3.0-or-later"

# Import main classes and functions
from .histogram_pca import (
    HistogramPCA,
    prep_histogram,
    ridit_score_centered,
    display_all_histograms
)

from .r_compatible import (
    histogram_pca_r_compatible,
    plot_r_style
)

__all__ = [
    'HistogramPCA',
    'prep_histogram',
    'ridit_score_centered',
    'display_all_histograms',
    'histogram_pca_r_compatible',
    'plot_r_style'
]