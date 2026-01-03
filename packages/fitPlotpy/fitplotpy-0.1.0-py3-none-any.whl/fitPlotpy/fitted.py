import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import to_rgba

def plot_fitted(
    data,
    pdf,
    cdf,
    ppf,
    params,
    bins=20,
    n=500,
    title=None
):
    data = np.asarray(data)
    data = np.sort(data)
    N = len(data)

    # Grid for smooth curves
    x = np.linspace(data.min()*0.95, data.max()*1.05, n)

    # Fitted curves
    pdf_y = pdf(x, **params)
    cdf_y = cdf(x, **params)

    # Empirical CDF
    ecdf_y = np.arange(1, N + 1) / N

    # Probabilities for QQ & PP
    p = (np.arange(1, N + 1) - 0.5) / N
    theo_q = ppf(p, **params)
    theo_p = cdf(data, **params)

    # Color theme
    main_color = "#2E1772"
    r, g, b, _ = to_rgba(main_color)
    shade_color = (r, g, b, 0.25)

    # ================= FIGURE (FIXED LAYOUT) =================
    fig, axes = plt.subplots(
        2, 2,
        figsize=(8, 6),      # ⬅ bigger figure
        dpi=110
    )
    fig.patch.set_facecolor("white")

    # Increase spacing between plots
    fig.subplots_adjust(
        left=0.07,
        right=0.97,
        bottom=0.07,
        top=0.92,
        wspace=0.30,          # ⬅ horizontal space
        hspace=0.35           # ⬅ vertical space
    )

    # ==================================================
    # (1) Histogram + Fitted PDF
    # ==================================================
    axes[0, 0].hist(
        data,
        bins=bins,
        density=True,
        color="lightgray",
        edgecolor="black",
        alpha=0.7
    )

    axes[0, 0].fill_between(x, pdf_y, color=shade_color)
    pdf_line, = axes[0, 0].plot(x, pdf_y, color=main_color, linewidth=3.5, label="Fitted PDF")

    pdf_line.set_path_effects([
        pe.Stroke(linewidth=7, foreground=main_color, alpha=0.25),
        pe.Normal()
    ])

    axes[0, 0].set_title("Histogram with Fitted PDF", fontsize=8, fontweight="bold")
    axes[0, 0].set_xlabel("x")
    axes[0, 0].set_ylabel(r"$f(x)$")
    axes[0, 0].legend(handles = [pdf_line], loc="best")

    # ==================================================
    # (2) Empirical CDF + Fitted CDF
    # ==================================================
    axes[0, 1].step(
        data,
        ecdf_y,
        where="post",
        color="black",
        linewidth=2,
        label="Empirical CDF"
    )

    cdf_line, = axes[0, 1].plot(
        x,
        cdf_y,
        color=main_color,
        linewidth=3.5,
        label="Fitted CDF"
    )

    cdf_line.set_path_effects([
        pe.Stroke(linewidth=7, foreground=main_color, alpha=0.25),
        pe.Normal()
    ])

    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].set_title("Empirical vs Fitted CDF", fontsize=8, fontweight="bold")
    axes[0, 1].set_xlabel("x")
    axes[0, 1].set_ylabel(r"$F(x)$")
    axes[0, 1].legend(loc="lower right")

    # ==================================================
    # (3) Quantile–Quantile Plot
    # ==================================================
    axes[1, 0].scatter(
        theo_q,
        data,
        s=45,
        color=main_color,
        edgecolor="black"
    )

    q_min = min(theo_q.min(), data.min())
    q_max = max(theo_q.max(), data.max())
    axes[1, 0].plot(
        [q_min, q_max],
        [q_min, q_max],
        linestyle="--",
        color="black",
        linewidth=2
    )

    axes[1, 0].set_title("Quantile–Quantile Plot", fontsize=8, fontweight="bold")
    axes[1, 0].set_xlabel("Theoretical Quantiles", fontsize=8)
    axes[1, 0].set_ylabel("Sample Quantiles", fontsize=8)

    # ==================================================
    # (4) Probability–Probability Plot
    # ==================================================
    axes[1, 1].scatter(
        theo_p,
        ecdf_y,
        s=45,
        color=main_color,
        edgecolor="black"
    )

    axes[1, 1].plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="black",
        linewidth=2
    )

    axes[1, 1].set_title("Probability–Probability Plot", fontsize=8, fontweight="bold")
    axes[1, 1].set_xlabel("Theoretical Probabilities", fontsize=8)
    axes[1, 1].set_ylabel("Empirical Probabilities", fontsize=8)

    # ==================================================
    # Styling
    # ==================================================
    for ax in axes.ravel():
        ax.grid(True, linestyle="--", color="lightgray", linewidth=0.8)
        for spine in ax.spines.values():
            spine.set_linewidth(1.4)
        ax.tick_params(axis="both", labelsize=11, width=1.2)

    plt.suptitle(title, fontsize=18, fontweight="bold")
    plt.show()
