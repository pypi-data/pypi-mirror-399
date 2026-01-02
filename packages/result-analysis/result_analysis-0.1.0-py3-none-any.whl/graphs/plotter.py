import matplotlib.pyplot as plt


def plot_chart(df, x, y, title, xl, yl, kind="bar", rot=45, figsize=(12, 6), **kwargs):
    plt.figure(figsize=figsize)
    if kind == "bar":
        plt.bar(df[x], df[y], **kwargs)
    elif kind == "line":
        plt.plot(df[x], df[y], marker="o", **kwargs)
    elif kind == "scatter":
        plt.scatter(df[x], df[y], **kwargs)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xl, fontsize=12)
    plt.ylabel(yl, fontsize=12)
    plt.xticks(rotation=rot, ha="right")
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()
