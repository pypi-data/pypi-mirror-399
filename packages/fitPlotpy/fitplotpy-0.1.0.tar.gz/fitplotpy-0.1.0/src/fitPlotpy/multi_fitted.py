
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import to_rgba

def plot_multi_fitted(
    data,
    dist_list,
    xlim=None,
    n=500,
    show_histogram=True,
    show_ecdf=True,
    title=None
):
    data = np.asarray(data)
    data_sorted = np.sort(data)

    if xlim is None:
        xlim = (0.95 * data.min(), 1.05 * data.max())

    x = np.linspace(xlim[0], xlim[1], n)
    k = len(dist_list)

    colors = plt.cm.plasma(np.linspace(0.1, 0.9, k))

    fig, axes = plt.subplots(1, 2, figsize=(10, 8), dpi=110)
    fig.patch.set_facecolor("white")

    # --------------------- PDF PANEL ---------------------
    if show_histogram:
        axes[0].hist(data, bins=8, density=True, color="gray",
                     edgecolor="black", alpha=0.6)

    for i, dist in enumerate(dist_list):
        y = dist["pdf"](x, **dist["params"])
        r, g, b, _ = to_rgba(colors[i])
        axes[0].fill_between(x, y, color=(r, g, b, 0.25))

        line, = axes[0].plot(
            x, y, color=colors[i], linewidth=3.5, label=dist["name"]
        )
        line.set_path_effects([
            pe.Stroke(linewidth=7, foreground=colors[i], alpha=0.25),
            pe.Normal()
        ])

    axes[0].set_title("Fitted PDFs", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel(r"$f(x)$")
    axes[0].legend()
    axes[0].grid(True, linestyle="--", color="lightgray", linewidth=0.8)

    # --------------------- CDF PANEL ---------------------
    for i, dist in enumerate(dist_list):
        y = dist["cdf"](x, **dist["params"])
        line, = axes[1].plot(x, y, color=colors[i], linewidth=3.5, label=dist["name"])
        line.set_path_effects([
            pe.Stroke(linewidth=7, foreground=colors[i], alpha=0.25),
            pe.Normal()
        ])

    if show_ecdf:
        ecdf_y = np.arange(1, len(data)+1) / len(data)
        axes[1].step(data_sorted, ecdf_y, where="post",
                     color="black", linewidth=2, label="Empirical CDF")

    axes[1].set_ylim(0, 1)
    axes[1].set_title("Fitted CDFs", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel(r"$F(x)$")
    axes[1].legend()
    axes[1].grid(True, linestyle="--", color="lightgray", linewidth=0.8)

    for ax in axes:
        for spine in ax.spines.values():
            spine.set_linewidth(1.4)
        ax.tick_params(axis="both", labelsize=10, width=1.2)

    plt.tight_layout()
    plt.suptitle(title, fontsize=12, fontweight="bold")
    plt.show()

