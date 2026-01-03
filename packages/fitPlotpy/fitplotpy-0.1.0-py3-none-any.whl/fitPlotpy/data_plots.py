import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def plot_data(data, title="Data Distribution",
             figsize=(14, 10), bins=15,
             hist_color='deepskyblue', kde_color='lime',
             box_color='magenta', violin_color='orange',
             lwd=3, alpha_fill=0.6):
   
    # ---------- Set up 2x2 Panel ----------
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    
    # ---------- Histogram ----------
    axes[0, 0].hist(data, bins=bins, color=hist_color, edgecolor='black', alpha=alpha_fill)
    axes[0, 0].set_title('Histogram', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Value')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].grid(True, linestyle=':', linewidth=1, color='gray', alpha=0.5)
    
    # ---------- Horizontal Boxplot ----------
    sns.boxplot(x=data, ax=axes[0, 1], color=box_color, linewidth=lwd, orient='h')
    axes[0, 1].set_title('Boxplot', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Value')
    axes[0, 1].grid(True, linestyle=':', linewidth=1, color='gray', alpha=0.5)
    
    # ---------- Kernel Density Estimate ----------
    sns.kdeplot(data, ax=axes[1, 0], color=kde_color, linewidth=lwd, fill=True, alpha=alpha_fill)
    axes[1, 0].set_title('Kernel Density Estimate', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Value')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].grid(True, linestyle=':', linewidth=1, color='gray', alpha=0.5)
    
    # ---------- Violin Plot ----------
    sns.violinplot(y=data, ax=axes[1, 1], color=violin_color, linewidth=lwd)
    axes[1, 1].set_title('Violin Plot', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Value')
    axes[1, 1].grid(True, linestyle=':', linewidth=1, color='gray', alpha=0.5)
    
    # ---------- Main Title ----------
    plt.suptitle(title, fontsize=18, fontweight='bold')
    plt.show()
