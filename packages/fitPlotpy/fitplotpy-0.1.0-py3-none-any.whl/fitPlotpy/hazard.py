import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import matplotlib.patheffects as pe

def plot_hazard(
    pdf,
    cdf,
    param_list,
    xlim=(0, 10),
    ylim=None,
    n=500,
    main=r"$\mathbf{Hazard\ Function}$",
    xlab=r"$x$",
    ylab=r"$h(x)$",
    colors=None,
    shade_colors=None,
    lwd=3.5,
    lty="-",
    grid=True,
    grid_lty="--",
    grid_col="lightgray",
    grid_lwd=0.8
):

    x = np.linspace(xlim[0], xlim[1], n)
    k = len(param_list)

    # ---------- Color palette ----------
    if colors is None:
        cmap = plt.cm.plasma
        colors = cmap(np.linspace(0.1, 0.9, k))

    # ---------- Shading colors ----------
    if shade_colors is None:
        shade_colors = []
        for c in colors:
            r, g, b, _ = to_rgba(c)
            shade_colors.append((r, g, b, 0.25))

    # ---------- Figure ----------
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # ---------- Titles ----------
    ax.set_title(main, fontsize=12, fontweight="bold", pad=15)
    ax.set_xlabel(xlab, fontsize=10)
    ax.set_ylabel(ylab, fontsize=10)

    ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    # ---------- Grid ----------
    if grid:
        ax.grid(True, linestyle=grid_lty, linewidth=grid_lwd, color=grid_col)

    # ---------- Axes styling ----------
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    ax.tick_params(axis="both", labelsize=11, width=1.2)

    # ---------- Plot Hazard ----------
    for i, params in enumerate(param_list):
        f = pdf(x, **params)
        F = cdf(x, **params)

        # numerical safety
        hazard = np.where(1 - F > 1e-10, f / (1 - F), np.nan)

        ax.fill_between(x, hazard, color=shade_colors[i])

        label = ", ".join([rf"${k}={v}$" for k, v in params.items()])

        line, = ax.plot(
            x, hazard,
            color=colors[i],
            linewidth=lwd,
            linestyle=lty,
            label=label
        )

        # Glow 🔥
        line.set_path_effects([
            pe.Stroke(linewidth=lwd + 3, foreground=colors[i], alpha=0.25),
            pe.Normal()
        ])

    # ---------- Legend ----------
    leg = ax.legend(
        fontsize=10,
        frameon=True,
        fancybox=True,
        framealpha=0.95,
        loc="upper center"
    )
    leg.get_frame().set_edgecolor("black")
    leg.get_frame().set_linewidth(0.8)

    plt.tight_layout()
    plt.show()

