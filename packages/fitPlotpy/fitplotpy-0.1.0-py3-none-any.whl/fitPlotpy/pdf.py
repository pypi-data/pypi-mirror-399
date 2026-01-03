import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import matplotlib.patheffects as pe

def plot_pdf(pdf, param_list, xlim=(0,10), ylim=(0,5), n=500,
             main="Probability Density Function",
             xlab="x", ylab="f(x)", colors=None, shade_colors=None,
             lwd=3.5, lty="-", grid=True):

    x = np.linspace(*xlim, n)
    k = len(param_list)

    if colors is None:
        colors = plt.cm.plasma(np.linspace(0.1, 0.9, k))

    if shade_colors is None:
        shade_colors = [(*to_rgba(c)[:3], 0.25) for c in colors]

    fig, ax = plt.subplots(figsize=(6,4))
    ax.set_title(main, fontweight="bold")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

    for i, p in enumerate(param_list):
        y = pdf(x, **p)
        ax.fill_between(x, y, color=shade_colors[i])
        line, = ax.plot(x, y, color=colors[i], lw=lwd,
                         label=", ".join(f"{k}={v}" for k,v in p.items()))
        line.set_path_effects([
            pe.Stroke(linewidth=lwd+3, foreground=colors[i], alpha=0.25),
            pe.Normal()
        ])

    ax.legend()
    if grid: ax.grid(True, ls="--", alpha=0.6)
    plt.show()


