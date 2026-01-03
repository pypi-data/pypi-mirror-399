import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from scipy import linalg
import warnings
warnings.filterwarnings('ignore')

class HistogramPCA:
    """
    Histogram PCA implementation following the R code structure
    """
    
    def __init__(self):
        self.correlation = None
        self.eigenvectors = None
        self.table_mean = None
        self.percentage_components = None
        self.pc_interval = None
        
    @staticmethod
    def centrage(x, reduire=0):
        """
        Center and optionally scale the data
        reduire=1: center only
        reduire=0: center and scale (standardize)
        """
        x = np.array(x)
        x_centered = x - np.mean(x, axis=0)
        
        if reduire == 1:
            return x_centered
        else:
            x_std = np.std(x, axis=0, ddof=1)
            x_std[x_std == 0] = 1  # Avoid division by zero
            return x_centered / x_std
    
    @staticmethod
    def fintab(gen1):
        """
        Process the interval table
        """
        gen1 = pd.DataFrame(gen1)
        k = len(gen1)
        k3 = k // 2
        k1 = 2 * gen1.shape[1]
        k2 = k1 // 2
        
        t1 = gen1.iloc[:k//2, :]
        t2 = gen1.iloc[k//2:, :]
        t3 = pd.concat([t1.reset_index(drop=True), t2.reset_index(drop=True)], axis=1)
        
        t5 = []
        for i in range(k2):
            t5.append(pd.concat([t3.iloc[:, i], t3.iloc[:, i + k2]], axis=1))
        
        t6 = []
        for i in range(k2):
            temp = np.zeros((k3, 2))
            for j in range(k3):
                row_vals = t5[i].iloc[j, :].values
                temp[j, :] = [np.min(row_vals), np.max(row_vals)]
            t6.append(temp)
        
        t7 = t6[0]
        for s in range(1, k2):
            t7 = np.column_stack([t7, t6[s]])
        
        return pd.DataFrame(t7)
    
    @staticmethod
    def ucad(p):
        """
        Generate column names for PC intervals
        """
        names = []
        for i in range(1, p + 1):
            names.extend([f'PCMin.{i}', f'PCMax.{i}'])
        return names
    
    def fit(self, variables, scores=None, t=1.1, axes=(0, 1), 
            row_names=None, col_names=None, transformation=1, 
            method='hypercube'):
        """
        Main Histogram PCA function
        
        VERSION 2.0 - SVD calculation fixed to match R exactly
        
        Parameters:
        -----------
        variables : list of DataFrames
            List of histogram tables
        scores : list of arrays
            Ridit scores for each variable
        t : float
            Parameter for Chebyshev inequality (default 1.1)
        axes : tuple
            Axes to display (0-indexed)
        row_names : list
            Names of observations (rows)
        col_names : list
            Names of variables (columns)
        transformation : int
            1: no transformation, 2: angular transformation
        method : str
            'hypercube' (default)
        """
        
        print("\n" + "="*80)
        print("📊 Histogram PCA v2.0 - SVD Fix Applied")
        print("   Expected: PC1 ≈ 72.26% (v1.0 gave 69.60%)")
        print("="*80 + "\n")
        
        k = t
        n = variables[0].shape[0]
        p = len(variables)
        
        # Apply angular transformation if requested
        if transformation == 2:
            variables = [np.arcsin(np.sqrt(var)) for var in variables]
        
        # Center the data
        variables = [self.centrage(var) for var in variables]
        
        # Generate default scores if not provided
        if scores is None:
            scores = []
            for var in variables:
                scores.append(np.arange(1, var.shape[1] + 1))
        
        # Calculate means
        mean = np.zeros((n, p))
        for i in range(n):
            for j in range(p):
                # Handle both DataFrame and array inputs
                if hasattr(variables[j], 'iloc'):
                    var_row = variables[j].iloc[i, :].values
                else:
                    var_row = variables[j][i, :]
                mean[i, j] = np.sum(var_row * scores[j])
        
        # Calculate covariance matrix V
        V = (1/n) * mean.T @ mean
        
        print(f"\n🔍 DEBUG INFO:")
        print(f"   n (observations) = {n}")
        print(f"   p (variables) = {p}")
        print(f"   mean matrix shape: {mean.shape}")
        print(f"   V matrix shape: {V.shape}")
        print(f"   trace(V) = {np.trace(V):.6f}")
        print(f"   First row of mean: {mean[0, :]}")
        
        # Warning for n < p case
        if n < p:
            print(f"\n⚠️  WARNING: More variables (p={p}) than observations (n={n})!")
            print(f"   Only {n} principal components will be computed.")
            print(f"   For better results, collect more images or reduce features.")
        
        print(f"\n📊 SCORES DEBUG:")
        for j in range(min(2, p)):  # Show first 2 variables
            print(f"   Variable {j+1} scores: {scores[j]}")
            print(f"   Variable {j+1} (row 0): {variables[j][0, :] if hasattr(variables[j], 'shape') else variables[j].iloc[0, :].values}")
        print()
        
        # Calculate standard deviations
        dev_standard = np.zeros((n, p))
        for i in range(n):
            for j in range(p):
                # Handle both DataFrame and array inputs
                if hasattr(variables[j], 'iloc'):
                    var_j = variables[j].iloc[i, :].values
                else:
                    var_j = variables[j][i, :]
                score_j = scores[j]
                sum_weighted = np.sum(var_j * score_j)
                sum_weighted_sq = np.sum((var_j ** 2) * score_j)
                dev_standard[i, j] = np.sqrt(
                    (sum_weighted_sq - (sum_weighted ** 2) / n) / (n - 1)
                )
        
        # Calculate Tmin and Tmax using Chebyshev inequality
        t_min = mean - k * dev_standard
        t_max = mean + k * dev_standard
        
        # SVD decomposition - Match R's approach exactly
        # R: Vect <- svd(mean, nu = n, nv = p)$v
        # R: Val <- svd(V, nu = p)$d
        
        # Get eigenvectors from SVD of mean matrix (as in R)
        U_mean, S_mean, Vt_mean = linalg.svd(mean, full_matrices=False)
        Vect = Vt_mean.T  # Right singular vectors
        
        # Get eigenvalues from SVD of V matrix (as in R)
        U_V, S_V, Vt_V = linalg.svd(V, full_matrices=False)
        Val = S_V  # Singular values of V = eigenvalues of V
        
        # Process intervals
        T = np.vstack([t_min, t_max])
        prep_t = self.fintab(T)
        
        # Create hypercube vertices
        compo = []
        for i in range(n):
            # Get min and max for each variable
            row_intervals = []
            for j in range(p):
                row_intervals.append([prep_t.iloc[i, 2*j], prep_t.iloc[i, 2*j + 1]])
            
            # Generate all combinations (vertices of hypercube)
            from itertools import product
            vertices = list(product(*row_intervals))
            vertices = np.array(vertices)
            
            # Project vertices onto principal components
            projected = vertices @ Vect
            compo.append(projected)
        
        # Calculate min and max projections for each observation
        # Handle case where n < p (fewer observations than variables)
        n_components = min(n, p)
        compo_min = np.zeros((n, n_components))
        compo_max = np.zeros((n, n_components))
        
        for i in range(n):
            for j in range(n_components):
                if j < compo[i].shape[1]:  # Check if component exists
                    compo_min[i, j] = np.min(compo[i][:, j])
                    compo_max[i, j] = np.max(compo[i][:, j])
        
        # Calculate percentage of variance
        pval = Val / np.sum(Val) * 100
        
        # Create percentage table (only for available components)
        pval2 = pd.DataFrame({
            'eigenvalue': Val[:n_components],
            'percentage of variance': pval[:n_components],
            'cumulative percentage of variance': np.cumsum(pval[:n_components])
        }, index=[f'comp{i+1}' for i in range(n_components)])
        
        # Calculate classical components and correlation
        class_compo = mean @ Vect[:, :n_components]  # Only use available components
        correl = np.corrcoef(mean.T, class_compo.T)[:p, p:p+n_components]
        
        # Store results
        self.correlation = pd.DataFrame(
            correl,
            columns=[f'Component {i+1}' for i in range(n_components)],
            index=col_names if col_names else [f'Variable {i+1}' for i in range(p)]
        )
        
        self.eigenvectors = pd.DataFrame(
            Vect[:, :n_components],
            columns=[f'EigenVector {i+1}' for i in range(n_components)]
        )
        
        self.table_mean = pd.DataFrame(
            mean,
            columns=col_names if col_names else [f'Variable {i+1}' for i in range(p)]
        )
        
        self.percentage_components = pval2
        
        # Create PC interval table
        # Use actual number of components (min of n and p)
        gen_pc = np.vstack([compo_min, compo_max])
        pc_interval = self.fintab(gen_pc)
        pc_interval.columns = self.ucad(n_components)
        pc_interval.index = row_names if row_names else [f'Obs{i+1}' for i in range(n)]
        
        self.pc_interval = pc_interval
        
        # Plotting
        self._plot_factorial_plan(compo_min, compo_max, axes, pval, 
                                  row_names, transformation)
        self._plot_correlation_circle(correl, axes, pval, col_names)
        
        # 3D plot if p > 2
        if p > 2:
            self._plot_3d(compo_min, compo_max, pval, row_names)
        
        return {
            'Correlation': self.correlation,
            'VecteurPropre': self.eigenvectors,
            'Tableaumean': self.table_mean,
            'PourCentageComposante': self.percentage_components,
            'PCinterval': self.pc_interval
        }
    
    def _plot_factorial_plan(self, compo_min, compo_max, axes, pval, 
                            row_names, transformation):
        """Plot the factorial plan matching R's ggplot2 style"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        ax1, ax2 = axes
        n = len(compo_min)
        
        # Use seaborn color palette
        colors = sns.color_palette("Set2", n)
        
        # Plot rectangles
        for i in range(n):
            x_min = compo_min[i, ax1]
            x_max = compo_max[i, ax1]
            y_min = compo_min[i, ax2]
            y_max = compo_max[i, ax2]
            
            rect = Rectangle(
                (x_min, y_min),
                x_max - x_min,
                y_max - y_min,
                facecolor=colors[i],
                edgecolor='black',
                alpha=0.6,
                linewidth=1.5
            )
            ax.add_patch(rect)
            
            # Add text labels
            label = row_names[i] if row_names else f'Obs{i+1}'
            ax.text(x_max, y_max, label, 
                   fontsize=10, ha='left', va='bottom',
                   fontweight='normal')
        
        # Add reference lines
        ax.axhline(y=0, color='blue', linestyle='-', linewidth=1, alpha=0.7)
        ax.axvline(x=0, color='blue', linestyle='-', linewidth=1, alpha=0.7)
        
        # Labels with variance percentages
        ax.set_xlabel(f'Axe n{ax1+1} ({pval[ax1]:.2f}%)', fontsize=14, fontweight='bold')
        ax.set_ylabel(f'Axe n{ax2+1} ({pval[ax2]:.2f}%)', fontsize=14, fontweight='bold')
        
        title = 'Factorial Plan'
        if transformation == 2:
            title += ' with Angular Transformation'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Style to match ggplot2
        ax.set_aspect('equal', adjustable='datalim')
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
        ax.set_axisbelow(True)
        ax.set_facecolor('#EBEBEB')
        
        # Set explicit limits with padding to show all rectangles
        x_all = np.concatenate([compo_min[:, ax1], compo_max[:, ax1]])
        y_all = np.concatenate([compo_min[:, ax2], compo_max[:, ax2]])
        
        x_range = [x_all.min(), x_all.max()]
        y_range = [y_all.min(), y_all.max()]
        
        x_padding = max(0.5, (x_range[1] - x_range[0]) * 0.15)
        y_padding = max(0.5, (y_range[1] - y_range[0]) * 0.15)
        
        ax.set_xlim(x_range[0] - x_padding, x_range[1] + x_padding)
        ax.set_ylim(y_range[0] - y_padding, y_range[1] + y_padding)
        
        plt.tight_layout()
        plt.show()
    
    def _plot_correlation_circle(self, correl, axes, pval, col_names):
        """Plot the correlation circle matching R's ggplot2 style"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        ax1, ax2 = axes
        
        # Draw circle
        circle = plt.Circle((0, 0), 1, fill=False, edgecolor='gray', 
                           linewidth=2, linestyle='-')
        ax.add_patch(circle)
        
        # Plot arrows and labels
        p = correl.shape[0]
        for i in range(p):
            x_cor = correl[i, ax1]
            y_cor = correl[i, ax2]
            
            # Draw arrow with better styling
            ax.annotate('', xy=(x_cor, y_cor), xytext=(0, 0),
                       arrowprops=dict(arrowstyle='->',
                                     color='gray',
                                     lw=2,
                                     shrinkA=0, shrinkB=0))
            
            label = col_names[i] if col_names else f'Variable {i+1}'
            ax.text(x_cor * 1.15, y_cor * 1.15, label,
                   fontsize=11, ha='center', va='center',
                   fontweight='bold')
        
        # Add reference lines
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
        
        # Labels
        ax.set_xlabel(f'Component n{ax1+1} ({pval[ax1]:.2f}%)', 
                     fontsize=14, fontweight='bold')
        ax.set_ylabel(f'Component n{ax2+1} ({pval[ax2]:.2f}%)', 
                     fontsize=14, fontweight='bold')
        ax.set_title('Correlation Circle', fontsize=16, 
                    fontweight='bold', pad=20)
        
        # Style to match ggplot2
        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
        ax.set_axisbelow(True)
        ax.set_facecolor('#EBEBEB')
        
        plt.tight_layout()
        plt.show()
    
    def _plot_3d(self, compo_min, compo_max, pval, row_names):
        """Plot 3D factorial plan with wire-frame boxes (matching R)"""
        fig = plt.figure(figsize=(14, 12))
        ax = fig.add_subplot(111, projection='3d')
        
        n = len(compo_min)
        colors = plt.cm.Set2(np.linspace(0, 1, n))
        
        # Define cube edge connectivity (R's approach)
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # bottom face
            [4, 5], [5, 6], [6, 7], [7, 4],  # top face
            [0, 4], [1, 5], [2, 6], [3, 7]   # vertical edges
        ]
        
        # Plot each observation's wire-frame box
        for i in range(n):
            x_min, x_max = compo_min[i, 0], compo_max[i, 0]
            y_min, y_max = compo_min[i, 1], compo_max[i, 1]
            z_min, z_max = compo_min[i, 2], compo_max[i, 2]
            
            # Define the 8 vertices
            vertices = np.array([
                [x_min, y_min, z_min],  # 0
                [x_max, y_min, z_min],  # 1
                [x_max, y_max, z_min],  # 2
                [x_min, y_max, z_min],  # 3
                [x_min, y_min, z_max],  # 4
                [x_max, y_min, z_max],  # 5
                [x_max, y_max, z_max],  # 6
                [x_min, y_max, z_max]   # 7
            ])
            
            # Draw all 12 edges
            for edge in edges:
                points = vertices[edge]
                ax.plot3D(*points.T, color=colors[i], linewidth=2, alpha=0.8)
            
            # Add text label at center of box
            label = row_names[i] if row_names else f'Obs{i+1}'
            ax.text((x_min + x_max)/2, (y_min + y_max)/2, (z_min + z_max)/2,
                   label, fontsize=10, fontweight='bold',
                   ha='center', va='center', color=colors[i])
        
        # Set labels with variance percentages
        ax.set_xlabel(f'PC.1 ({pval[0]:.2f}%)', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_ylabel(f'PC.2 ({pval[1]:.2f}%)', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_zlabel(f'PC.3 ({pval[2]:.2f}%)', fontsize=12, fontweight='bold', labelpad=10)
        ax.set_title('3D Factorial Plan', fontsize=14, fontweight='bold', pad=20)
        
        # Set view angle to match R (front-ish view)
        ax.view_init(elev=25, azim=-60)
        
        # Add grid and styling
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        
        # Set background color
        ax.xaxis.pane.set_edgecolor('gray')
        ax.yaxis.pane.set_edgecolor('gray')
        ax.zaxis.pane.set_edgecolor('gray')
        ax.xaxis.pane.set_alpha(0.1)
        ax.yaxis.pane.set_alpha(0.1)
        ax.zaxis.pane.set_alpha(0.1)
        
        plt.tight_layout()
        plt.show()


def ridit_score_standard(X):
    """
    Calculate standard Ridit scores
    """
    X = pd.DataFrame(X)
    entree = X.sum(axis=0).values
    p = X.shape[1]
    
    res = np.zeros(p)
    res[0] = 0.5 * entree[0]
    
    for j in range(1, p):
        res[j] = 0.5 * entree[j] + np.sum(entree[:j])
    
    return res


def ridit_score_centered(X):
    """
    Calculate centered Ridit scores (Ridi2)
    
    NOTE: This replicates R's implementation which has a quirk:
    The normalization loop modifies res[j] one at a time, causing
    the sum to change during iteration. This results in scores that
    DON'T sum to 1, matching R's behavior exactly.
    """
    X = pd.DataFrame(X)
    entree = X.mean(axis=0).values
    p = X.shape[1]
    
    res = np.zeros(p)
    res[0] = 0.5 * entree[0]
    
    for j in range(1, p):
        res[j] = 0.5 * entree[j] + np.sum(entree[:j])
    
    # Normalize - REPLICATE R'S LOOP BUG!
    # R does: for(j in 1:p) { res[j] = res[j] / sum(res) }
    # This modifies res during iteration, changing the sum!
    for j in range(p):
        res[j] = res[j] / np.sum(res)
    
    return res


def ridit_score_normalized(X):
    """
    Calculate normalized Ridit scores (Ridi3) - used for TGV
    """
    X = pd.DataFrame(X)
    entree = X.mean(axis=0).values
    p = X.shape[1]
    
    res = np.zeros(p)
    res[0] = 0.5 * entree[0]
    
    for j in range(1, p):
        res[j] = 0.5 * entree[j] + np.sum(entree[:j])
    
    # Standardize (z-score)
    res = (res - np.mean(res)) / np.std(res, ddof=1)
    
    return res


def prep_histogram(X, Z, k=3):
    """
    Transform data into histogram format
    
    Parameters:
    -----------
    X : array-like
        Continuous variable to discretize
    Z : array-like
        Grouping variable (categories)
    k : int
        Number of bins
    
    Returns:
    --------
    dict with 'mid' (bin edges) and 'Vhistogram' (histogram DataFrame)
    """
    X = np.array(X)
    Z = np.array(Z)
    
    # Get unique categories
    categories = np.unique(Z)
    ncat = len(categories)
    
    # Create bins
    mido = np.linspace(X.min(), X.max(), k + 1)
    
    # Calculate histograms for each category
    V_histogram = np.zeros((ncat, k))
    
    for i, cat in enumerate(categories):
        X_subset = X[Z == cat]
        counts, _ = np.histogram(X_subset, bins=mido)
        V_histogram[i, :] = counts / np.sum(counts)
    
    V_histogram_df = pd.DataFrame(
        V_histogram,
        index=categories,
        columns=[f'V{j+1}' for j in range(k)]
    )
    
    return {
        'mid': mido,
        'Vhistogram': V_histogram_df
    }


# Visualization function using matplotlib/seaborn
def visu(PC, Correl, row_names=None, labs=None, axes=(0, 1), size=10):
    """
    Visualize PCA results with rectangles and correlation circle
    Matches R's ggplot2 style exactly
    """
    import warnings
    warnings.filterwarnings('ignore')
    
    n = len(PC)
    
    x1_var = 2 * axes[0]
    x2_var = 2 * axes[0] + 1
    y1_var = 2 * axes[1]
    y2_var = 2 * axes[1] + 1
    
    # Prepare data
    PC1 = pd.DataFrame({
        'x1': PC.iloc[:, x1_var],
        'x2': PC.iloc[:, x2_var],
        'y1': PC.iloc[:, y1_var],
        'y2': PC.iloc[:, y2_var]
    })
    
    if row_names is None:
        row_names = [f'{i+1}' for i in range(n)]
    
    PC1['Group'] = row_names
    
    if labs is None:
        labs = [f'Axe n{axes[0]+1}', f'Axe n{axes[1]+1}']
    
    # Create figure with two subplots
    fig = plt.figure(figsize=(16, 7))
    
    # ============================================================
    # PLOT 1: Factorial Plan with Rectangles (matching R ggplot2)
    # ============================================================
    ax1 = fig.add_subplot(121)
    
    # Use seaborn color palette for consistency
    colors = sns.color_palette("tab10", n)
    
    # Plot rectangles with proper styling
    for i in range(n):
        x_min = PC1.iloc[i]['x1']
        x_max = PC1.iloc[i]['x2']
        y_min = PC1.iloc[i]['y1']
        y_max = PC1.iloc[i]['y2']
        
        # Draw filled rectangle
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
        
        # Add text label at top-right corner
        ax1.text(x_max, y_max, row_names[i],
                fontsize=size, ha='left', va='bottom',
                fontweight='normal')
    
    # Set axis properties to match R ggplot2
    ax1.set_xlabel(labs[0], fontsize=14, fontweight='bold')
    ax1.set_ylabel(labs[1], fontsize=14, fontweight='bold')
    ax1.set_title('Factorial Plan', fontsize=16, fontweight='bold', pad=20)
    
    # Set equal aspect ratio
    ax1.set_aspect('equal', adjustable='datalim')
    
    # Add grid with ggplot2 style
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
    ax1.set_axisbelow(True)
    
    # Style the plot background (ggplot2 gray background)
    ax1.set_facecolor('#EBEBEB')
    
    # Add legend
    handles = [plt.Rectangle((0,0),1,1, facecolor=colors[i], 
                            edgecolor='black', alpha=0.6) 
               for i in range(n)]
    ax1.legend(handles, row_names, loc='best', 
              title='Group', frameon=True, 
              fancybox=True, shadow=True)
    
    # Auto-scale with some padding
    x_range = [PC1[['x1', 'x2']].min().min(), PC1[['x1', 'x2']].max().max()]
    y_range = [PC1[['y1', 'y2']].min().min(), PC1[['y1', 'y2']].max().max()]
    x_padding = (x_range[1] - x_range[0]) * 0.1
    y_padding = (y_range[1] - y_range[0]) * 0.1
    ax1.set_xlim(x_range[0] - x_padding, x_range[1] + x_padding)
    ax1.set_ylim(y_range[0] - y_padding, y_range[1] + y_padding)
    
    # ============================================================
    # PLOT 2: Correlation Circle (matching R ggplot2)
    # ============================================================
    ax2 = fig.add_subplot(122)
    
    # Draw circle
    circle = plt.Circle((0, 0), 1, fill=False, edgecolor='gray', 
                       linewidth=2, linestyle='-')
    ax2.add_patch(circle)
    
    # Get correlations for selected axes
    correlations = Correl.iloc[:, axes]
    
    # Plot arrows and labels
    for i in range(len(correlations)):
        x_cor = correlations.iloc[i, 0]
        y_cor = correlations.iloc[i, 1]
        
        # Draw arrow
        ax2.annotate('', xy=(x_cor, y_cor), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='->', 
                                  color='gray',
                                  lw=2,
                                  shrinkA=0, shrinkB=0))
        
        # Add variable label
        ax2.text(x_cor * 1.15, y_cor * 1.15, 
                correlations.index[i],
                fontsize=11, ha='center', va='center',
                fontweight='bold')
    
    # Set axis properties
    ax2.set_xlabel(labs[0], fontsize=14, fontweight='bold')
    ax2.set_ylabel(labs[1], fontsize=14, fontweight='bold')
    ax2.set_title('Circle of correlations', fontsize=16, 
                 fontweight='bold', pad=20)
    
    # Set limits and aspect
    ax2.set_xlim(-1.3, 1.3)
    ax2.set_ylim(-1.3, 1.3)
    ax2.set_aspect('equal', adjustable='box')
    
    # Add grid
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
    ax2.set_axisbelow(True)
    
    # Style background
    ax2.set_facecolor('#EBEBEB')
    
    # Add axes lines
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
    
    plt.tight_layout()
    plt.show()



# =============================================================================
# HISTOGRAM VISUALIZATION FUNCTIONS
# =============================================================================

def plot_histograms(histograms, variable_names=None, figsize=(16, 10)):
    """
    Display histograms for all variables and property types
    Shows grouped bar charts with bins grouped by property type
    
    Parameters:
    -----------
    histograms : list of DataFrames
        List of histogram DataFrames (one per variable)
    variable_names : list of str, optional
        Names of variables
    figsize : tuple, optional
        Figure size (width, height)
    """
    n_vars = len(histograms)
    
    if variable_names is None:
        variable_names = [f"Variable {i+1}" for i in range(n_vars)]
    
    # Create subplots - one per variable
    fig, axes = plt.subplots(n_vars, 1, figsize=figsize)
    if n_vars == 1:
        axes = [axes]
    
    # Color palette for property types
    property_types = histograms[0].index
    n_types = len(property_types)
    colors = sns.color_palette("Set2", n_types)
    
    for var_idx, (hist, var_name) in enumerate(zip(histograms, variable_names)):
        ax = axes[var_idx]
        
        # Get number of bins
        n_bins = hist.shape[1]
        x_positions = np.arange(n_bins)
        width = 0.8 / n_types  # Width of each bar
        
        # Plot bars for each property type
        for i, prop_type in enumerate(property_types):
            offset = (i - n_types/2) * width + width/2
            values = hist.loc[prop_type].values
            
            ax.bar(x_positions + offset, values, width, 
                  label=prop_type, color=colors[i], 
                  edgecolor="black", linewidth=0.8, alpha=0.8)
        
        # Styling
        ax.set_xlabel("Bins", fontsize=11, fontweight="bold")
        ax.set_ylabel("Frequency", fontsize=11, fontweight="bold")
        ax.set_title(f"Histogram: {var_name}", fontsize=13, fontweight="bold", pad=10)
        ax.set_xticks(x_positions)
        ax.set_xticklabels([f"Bin {i+1}" for i in range(n_bins)])
        ax.grid(True, alpha=0.3, axis="y", linestyle="--")
        ax.set_axisbelow(True)
        ax.set_facecolor("#F5F5F5")
        
        # Legend only on first plot
        if var_idx == 0:
            ax.legend(title="Property Type", bbox_to_anchor=(1.02, 1), 
                     loc="upper left", frameon=True, fancybox=True, shadow=True)
    
    plt.suptitle("Histograms by Variable and Property Type", 
                fontsize=16, fontweight="bold", y=0.995)
    plt.tight_layout()
    plt.show()


def plot_histograms_grid(histograms, variable_names=None, figsize=(18, 12)):
    """
    Display histograms in a grid layout (one subplot per variable)
    Each subplot shows all property types for that variable
    
    Parameters:
    -----------
    histograms : list of DataFrames
        List of histogram DataFrames (one per variable)
    variable_names : list of str, optional
        Names of variables
    figsize : tuple, optional
        Figure size (width, height)
    """
    n_vars = len(histograms)
    
    if variable_names is None:
        variable_names = [f"Variable {i+1}" for i in range(n_vars)]
    
    # Determine grid size
    n_cols = min(3, n_vars)
    n_rows = (n_vars + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_vars == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    # Color palette
    property_types = histograms[0].index
    n_types = len(property_types)
    colors = sns.color_palette("Set2", n_types)
    
    for var_idx, (hist, var_name) in enumerate(zip(histograms, variable_names)):
        ax = axes[var_idx]
        
        n_bins = hist.shape[1]
        x = np.arange(n_types)
        width = 0.15
        
        # Plot each bin as a group
        for bin_idx in range(n_bins):
            offset = (bin_idx - n_bins/2) * width + width/2
            values = hist.iloc[:, bin_idx].values
            
            ax.bar(x + offset, values, width,
                  label=f"Bin {bin_idx+1}",
                  edgecolor="black", linewidth=0.5, alpha=0.8)
        
        # Styling
        ax.set_xlabel("Property Type", fontsize=10, fontweight="bold")
        ax.set_ylabel("Frequency", fontsize=10, fontweight="bold")
        ax.set_title(f"{var_name}", fontsize=12, fontweight="bold", pad=8)
        ax.set_xticks(x)
        ax.set_xticklabels(property_types, rotation=45, ha="right", fontsize=8)
        ax.grid(True, alpha=0.3, axis="y", linestyle="--")
        ax.set_axisbelow(True)
        ax.set_facecolor("#F5F5F5")
        ax.legend(fontsize=8, ncol=n_bins, loc="upper right")
    
    # Hide unused subplots
    for idx in range(n_vars, len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle("Distribution of Property Types Across Bins", 
                fontsize=16, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_histograms_stacked(histograms, variable_names=None, figsize=(16, 10)):
    """
    Display histograms as stacked bar charts
    Shows the proportion of each bin within each property type
    
    Parameters:
    -----------
    histograms : list of DataFrames
        List of histogram DataFrames (one per variable)
    variable_names : list of str, optional
        Names of variables
    figsize : tuple, optional
        Figure size (width, height)
    """
    n_vars = len(histograms)
    
    if variable_names is None:
        variable_names = [f"Variable {i+1}" for i in range(n_vars)]
    
    # Create subplots
    fig, axes = plt.subplots(n_vars, 1, figsize=figsize)
    if n_vars == 1:
        axes = [axes]
    
    property_types = histograms[0].index
    n_types = len(property_types)
    
    for var_idx, (hist, var_name) in enumerate(zip(histograms, variable_names)):
        ax = axes[var_idx]
        
        n_bins = hist.shape[1]
        x = np.arange(n_types)
        
        # Get colors for bins
        bin_colors = plt.cm.viridis(np.linspace(0.2, 0.9, n_bins))
        
        # Create stacked bars
        bottom = np.zeros(n_types)
        for bin_idx in range(n_bins):
            values = hist.iloc[:, bin_idx].values
            ax.bar(x, values, label=f"Bin {bin_idx+1}",
                  bottom=bottom, color=bin_colors[bin_idx],
                  edgecolor="white", linewidth=1.5, alpha=0.9)
            bottom += values
        
        # Styling
        ax.set_xlabel("Property Type", fontsize=11, fontweight="bold")
        ax.set_ylabel("Cumulative Frequency", fontsize=11, fontweight="bold")
        ax.set_title(f"{var_name} - Stacked Distribution", 
                    fontsize=13, fontweight="bold", pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(property_types, rotation=45, ha="right")
        ax.grid(True, alpha=0.3, axis="y", linestyle="--")
        ax.set_axisbelow(True)
        ax.set_facecolor("#F5F5F5")
        ax.set_ylim(0, 1.05)  # Since histograms sum to 1
        
        # Add horizontal line at y=1
        ax.axhline(y=1, color="red", linestyle="--", linewidth=1, alpha=0.5)
        
        if var_idx == 0:
            ax.legend(title="Bins", bbox_to_anchor=(1.02, 1), 
                     loc="upper left", frameon=True, ncol=1)
    
    plt.suptitle("Stacked Histograms by Variable", 
                fontsize=16, fontweight="bold", y=0.995)
    plt.tight_layout()
    plt.show()


def display_all_histograms(histograms, variable_names=None):
    """
    Display histograms in all three styles
    
    Parameters:
    -----------
    histograms : list of DataFrames
        List of histogram DataFrames (one per variable)
    variable_names : list of str, optional
        Names of variables
    
    Example:
    --------
    >>> display_all_histograms(
    ...     [Hist1, Hist2, Hist3, Hist4, Hist5],
    ...     ["Price", "Bedrooms", "Bathrooms", "Acreage", "SquareFeet"]
    ... )
    """
    print("="*80)
    print("HISTOGRAM VISUALIZATIONS")
    print("="*80)
    
    print("\n1. Grouped Bar Charts (Bins grouped by property type)")
    plot_histograms(histograms, variable_names)
    
    print("\n2. Grid Layout (Property types grouped by bins)")
    plot_histograms_grid(histograms, variable_names)
    
    print("\n3. Stacked Bar Charts (Proportions within each property type)")
    plot_histograms_stacked(histograms, variable_names)
    
    print("\n" + "="*80)
    print("All histogram visualizations displayed!")
    print("="*80)