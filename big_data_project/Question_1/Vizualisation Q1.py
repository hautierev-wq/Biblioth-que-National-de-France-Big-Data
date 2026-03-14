"""
BnF Catalogue — Visualization
==============================
Reads the three CSV result files and produces a 4-panel figure.

"""

import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

# ── File paths (edit if your CSVs are elsewhere) ──────────────────────────────
HERE = pathlib.Path(__file__).parent

F_TYPES  = HERE / "queryResults_Q1_1_format_distribution.csv"
F_CHRON  = HERE / "queryResults_Q1_2_aount_published_per_year.csv"
F_AUTH   = HERE / "queryResults_Q1_3_amount_published_per_author.csv"

# ── Palette ───────────────────────────────────────────────────────────────────
C_NAVY   = "#1a3f6f"
C_GOLD   = "#c8922a"
C_TEAL   = "#1d7c6e"
C_CORAL  = "#c0432f"
C_SLATE  = "#5a6472"
C_LIGHT  = "#f7f5f0"
C_GRID   = "#e2dfd8"

TYPE_COLORS = [
    "#1a3f6f", "#2a6496", "#3d8abf",
    "#c8922a", "#1d7c6e", "#c0432f",
    "#7b5ea7",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt(n: float) -> str:
    """Human-readable number: 10718872 → '10.7M'."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(int(n))


def style_ax(ax, title=""):
    ax.set_facecolor(C_LIGHT)
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8.5)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight="bold",
                     color="#111111", pad=9)


def century_to_year(code: str) -> int:
    """'19xx' → 1900."""
    try:
        return int(str(code)[:2]) * 100
    except ValueError:
        return -1


# ── Panel 1: Record types (donut + bar) ───────────────────────────────────────

def plot_types(ax, df: pd.DataFrame):
    df = df.copy()
    df["label"] = (
        df["type"]
        .str.split("/").str[-1]   # last URI segment
        .str.replace(r"([A-Z])", r" \1", regex=True)  # CamelCase → words
        .str.strip()
    )
    df["count"] = pd.to_numeric(df["count"])
    df = df.sort_values("count", ascending=True)

    colors = TYPE_COLORS[:len(df)]
    bars = ax.barh(df["label"], df["count"], color=colors, height=0.6, zorder=2)

    total = df["count"].sum()
    for bar, val in zip(bars, df["count"]):
        pct = val / total * 100
        ax.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            f"{fmt(val)}  ({pct:.1f}%)",
            va="center", ha="left", fontsize=7.5, color=C_SLATE,
        )

    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.set_xlim(right=df["count"].max() * 1.38)
    style_ax(ax, "Record types")
    ax.set_xlabel(f"Records  ·  total {fmt(total)}", fontsize=8, color=C_SLATE)


# ── Panel 2: Chronological (area + line) ─────────────────────────────────────

def plot_chronological(ax, df: pd.DataFrame):
    df = df.copy()
    df["year"] = df["century"].apply(century_to_year)
    df["count"] = pd.to_numeric(df["count"])
    df = df[df["year"] < 2027].sort_values("year")

    x, y = df["year"].values, df["count"].values

    ax.fill_between(x, y, alpha=0.15, color=C_NAVY, zorder=1)
    ax.plot(x, y, color=C_NAVY, linewidth=2.2, zorder=3)
    ax.scatter(x, y, color=C_NAVY, s=28, zorder=4)

    # annotate top-3 peaks
    top3 = df.nlargest(3, "count")
    for _, row in top3.iterrows():
        century_num = int(row["year"] / 100) + 1
        suffix = {1:"st",2:"nd",3:"rd"}.get(century_num % 10 if century_num not in (11,12,13) else 0, "th")
        ax.annotate(
            f"{century_num}{suffix} c.\n{fmt(row['count'])}",
            xy=(row["year"], row["count"]),
            xytext=(6, 8), textcoords="offset points",
            fontsize=7.5, color=C_NAVY,
            arrowprops=dict(arrowstyle="-", color=C_NAVY, lw=0.8),
        )

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    labels = [str(y) for y in x]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7.5)
    style_ax(ax, "Chronological distribution (by century)")
    ax.set_ylabel("Records", fontsize=8, color=C_SLATE)


# ── Panel 3: Top authors ──────────────────────────────────────────────────────

def plot_top_authors(ax, df: pd.DataFrame):
    df = df.copy()
    df["workCount"] = pd.to_numeric(df["workCount"])
    df["authorLabel"] = df["authorLabel"].fillna("(no label)")

    top = df.nlargest(20, "workCount").sort_values("workCount", ascending=True)

    bars = ax.barh(top["authorLabel"], top["workCount"],
                   color=C_TEAL, height=0.65, zorder=2)

    for bar, val in zip(bars, top["workCount"]):
        ax.text(
            bar.get_width() * 1.01,
            bar.get_y() + bar.get_height() / 2,
            fmt(val), va="center", ha="left", fontsize=7.5, color=C_SLATE,
        )

    ax.set_xlim(right=top["workCount"].max() * 1.22)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    style_ax(ax, "Top 20 authors by work count")
    ax.set_xlabel("Works", fontsize=8, color=C_SLATE)


# ── Panel 4: Long-tail (log/log rank vs count) ────────────────────────────────

def plot_longtail(ax, df: pd.DataFrame):
    df = df.copy()
    df["workCount"] = pd.to_numeric(df["workCount"])
    df = df.sort_values("workCount", ascending=False).reset_index(drop=True)
    ranks  = df.index + 1
    counts = df["workCount"].values

    ax.scatter(ranks, counts, color=C_CORAL, s=22, alpha=0.8, zorder=3)
    ax.plot(ranks, counts, color=C_CORAL, linewidth=1.2, alpha=0.5, zorder=2)

    # shade tail
    if len(ranks) > 4:
        ax.fill_between(ranks[3:], counts[3:], alpha=0.12, color=C_CORAL)
        ax.axvline(4, color=C_GOLD, linewidth=1.2, linestyle="--", zorder=4)
        ax.text(4.4, counts[3] * 0.9, "long tail →",
                fontsize=8, color=C_GOLD, va="top")

    # label top-5
    for i in range(min(5, len(df))):
        name = df.loc[i, "authorLabel"]
        if pd.isna(name) or name == "(no label)":
            continue
        short = name.split()[-1]  # surname only
        ax.annotate(short, xy=(ranks[i], counts[i]),
                    xytext=(3, 3), textcoords="offset points",
                    fontsize=7, color=C_SLATE)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    style_ax(ax, "Long-tail: author rank vs. work count (log scale)")
    ax.set_xlabel("Author rank", fontsize=8, color=C_SLATE)
    ax.set_ylabel("Works", fontsize=8, color=C_SLATE)
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, zorder=0)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    df_types = pd.read_csv(F_TYPES)
    df_chron = pd.read_csv(F_CHRON)
    df_auth  = pd.read_csv(F_AUTH)

    fig = plt.figure(figsize=(16, 12), facecolor="white")
    fig.suptitle(
        "BnF — Catalogue Analysis",
        fontsize=14, fontweight="bold", color="#111111", y=0.985,
    )

    gs = GridSpec(2, 2, figure=fig,
                  hspace=0.44, wspace=0.30,
                  left=0.06, right=0.97,
                  top=0.94, bottom=0.07)

    plot_types(fig.add_subplot(gs[0, 0]), df_types)
    plot_chronological(fig.add_subplot(gs[0, 1]), df_chron)
    plot_top_authors(fig.add_subplot(gs[1, 0]), df_auth)
    plot_longtail(fig.add_subplot(gs[1, 1]), df_auth)

    fig.text(0.5, 0.005,
             "Source: data.bnf.fr/sparql",
             ha="center", fontsize=7.5, color=C_SLATE)

    out = HERE / "bnf_analysis.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved → {out}")
    plt.show()


if __name__ == "__main__":
    main()