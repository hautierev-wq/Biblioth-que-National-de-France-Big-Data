"""
BnF Catalogue — Subjects & Themes Visualization (Question 3)
=============================================================
Reads three real SPARQL CSV exports and produces a 4-panel figure.

Panels:
  1. Top 30 RAMEAU subject headings (horizontal bar)
  2. Subject evolution over time - top subjects by year (line chart)
  3. Language x Subject heat map (normalised)
  4. Top 5 subjects per language - volume comparison (grouped bar)
"""

import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib.gridspec import GridSpec

HERE = pathlib.Path(__file__).parent

F_SUBJECTS = HERE / "queryResults_Q3_1_top_rameau_subjects.csv"
F_CENTURY  = HERE / "queryResults_Q3_2_subject_by_century.csv"
F_LANG     = HERE / "queryResults_Q3_3_language_subject_crossanalysis.csv"

C_NAVY   = "#1a3f6f"
C_GOLD   = "#c8922a"
C_TEAL   = "#1d7c6e"
C_CORAL  = "#c0432f"
C_SLATE  = "#5a6472"
C_LIGHT  = "#f7f5f0"
C_GRID   = "#e2dfd8"
C_PURPLE = "#7b5ea7"

LINE_COLORS = [C_NAVY, C_CORAL, C_TEAL, C_GOLD, C_PURPLE,
               "#3a7d44", "#d4762a", "#2a6496"]

LANG_MAP = {
    "http://id.loc.gov/vocabulary/iso639-2/fre": "French",
    "http://id.loc.gov/vocabulary/iso639-2/eng": "English",
    "http://id.loc.gov/vocabulary/iso639-2/ger": "German",
    "http://id.loc.gov/vocabulary/iso639-2/spa": "Spanish",
    "http://id.loc.gov/vocabulary/iso639-2/ita": "Italian",
}

LANG_COLORS = {
    "French": C_NAVY, "English": C_TEAL,
    "German": C_GOLD, "Spanish": C_CORAL, "Italian": C_PURPLE
}

def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}k"
    return str(int(n))

def style_ax(ax, title=""):
    ax.set_facecolor(C_LIGHT)
    ax.set_axisbelow(True)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    if title:
        ax.set_title(title, fontsize=10.5, fontweight="bold",
                     color="#111111", pad=9)

# ── Panel 1: Top 30 RAMEAU subjects ──────────────────────────────────────────

def plot_top_subjects(ax, df):
    df = df.copy()
    df["workCount"] = pd.to_numeric(df["workCount"])
    top = df.nlargest(30, "workCount").sort_values("workCount", ascending=True)

    colors = [C_NAVY if i >= len(top) - 5 else C_TEAL for i in range(len(top))]
    bars = ax.barh(top["subjectLabel"], top["workCount"],
                   color=colors, height=0.65, zorder=2)

    total = df["workCount"].sum()
    for bar, val in zip(bars, top["workCount"]):
        pct = val / total * 100
        ax.text(bar.get_width() * 1.01,
                bar.get_y() + bar.get_height() / 2,
                f"{fmt(val)}  ({pct:.1f}%)",
                va="center", ha="left", fontsize=6.5, color=C_SLATE)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_xlim(right=top["workCount"].max() * 1.48)
    style_ax(ax, "Top 30 RAMEAU subject headings")
    ax.set_xlabel(f"Works linked  ·  total sample {fmt(total)}",
                  fontsize=8, color=C_SLATE)

# ── Panel 2: Subject evolution over time ─────────────────────────────────────

def plot_subject_evolution(ax, df):
    df = df.copy()
    df.columns = ["subjectLabel", "date", "count"]
    df["count"] = pd.to_numeric(df["count"])
    df["date"]  = pd.to_numeric(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"]  = df["date"].astype(int)
    df = df[(df["date"] >= 1700) & (df["date"] <= 2024)]

    top_subjects = (df.groupby("subjectLabel")["count"]
                    .sum().nlargest(8).index.tolist())

    for i, subj in enumerate(top_subjects):
        sub = (df[df["subjectLabel"] == subj]
               .sort_values("date")
               .set_index("date")["count"]
               .reindex(range(df["date"].min(), df["date"].max() + 1), fill_value=0)
               .rolling(5, center=True, min_periods=1).mean()
               .reset_index())
        sub.columns = ["date", "count"]
        color = LINE_COLORS[i % len(LINE_COLORS)]
        label = subj if len(subj) <= 22 else subj[:20] + "…"
        ax.plot(sub["date"], sub["count"],
                linewidth=1.8, color=color, label=label, zorder=3)
        ax.fill_between(sub["date"], sub["count"], alpha=0.07, color=color)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, zorder=0)
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_facecolor(C_LIGHT)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    ax.set_title("Top subject headings over time (5-yr rolling avg)",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    ax.set_ylabel("Works per year", fontsize=8, color=C_SLATE)
    ax.set_xlabel("Publication year", fontsize=8, color=C_SLATE)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.7,
              ncol=2, borderpad=0.5)

# ── Panel 3: Language x Subject heat map ─────────────────────────────────────

def plot_language_heatmap(ax, df):
    df = df.copy()
    df.columns = ["language", "subjectLabel", "count"]
    df["count"] = pd.to_numeric(df["count"])
    df["lang"]  = df["language"].map(LANG_MAP)
    df = df[df["lang"].notna()]

    top_subjects = (df.groupby("subjectLabel")["count"]
                    .sum().nlargest(14).index.tolist())
    pivot = (df[df["subjectLabel"].isin(top_subjects)]
             .pivot_table(index="subjectLabel", columns="lang",
                          values="count", aggfunc="sum", fill_value=0))

    col_order = [l for l in ["French","English","German","Spanish","Italian"]
                 if l in pivot.columns]
    pivot = pivot[col_order]
    pivot_norm = pivot.div(pivot.sum(axis=0), axis=1)

    im = ax.imshow(pivot_norm.values, aspect="auto",
                   cmap="YlOrRd", interpolation="nearest")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=8.5, color=C_SLATE)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=7.5, color=C_SLATE)

    for r in range(len(pivot.index)):
        for c in range(len(pivot.columns)):
            val = pivot.values[r, c]
            txt_col = "white" if pivot_norm.values[r, c] > 0.10 else C_SLATE
            ax.text(c, r, fmt(val), ha="center", va="center",
                    fontsize=6.5, color=txt_col)

    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(length=0)
    ax.set_title("Subject coverage by language (normalised per language)",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    plt.colorbar(im, ax=ax, shrink=0.65, label="Share within language",
                 format=mticker.FuncFormatter(lambda x, _: f"{x:.0%}"))

# ── Panel 4: Top 5 subjects per language ─────────────────────────────────────

def plot_language_top5(ax, df):
    df = df.copy()
    df.columns = ["language", "subjectLabel", "count"]
    df["count"] = pd.to_numeric(df["count"])
    df["lang"]  = df["language"].map(LANG_MAP)
    df = df[df["lang"].notna()]

    langs = ["French", "English", "German", "Spanish", "Italian"]
    x = np.arange(5)
    width = 0.15
    offsets = np.linspace(-0.30, 0.30, 5)

    for idx, lang in enumerate(langs):
        sub = df[df["lang"] == lang].nlargest(5, "count").reset_index(drop=True)
        # Pad to exactly 5 rows
        vals = np.zeros(5)
        vals[:len(sub)] = sub["count"].values
        color = LANG_COLORS[lang]
        ax.bar(x + offsets[idx], vals,
               width, color=color, alpha=0.85, label=lang, zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels(["#1", "#2", "#3", "#4", "#5"],
                       fontsize=9, color=C_SLATE)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_facecolor(C_LIGHT)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    ax.set_title("Top 5 subjects per language — volume comparison",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    ax.set_ylabel("Works", fontsize=8, color=C_SLATE)
    ax.set_xlabel("Subject rank within language", fontsize=8, color=C_SLATE)
    ax.legend(fontsize=7.5, loc="upper right", framealpha=0.7)

    # Annotate each bar with subject name
    for idx, lang in enumerate(langs):
        sub = df[df["lang"] == lang].nlargest(5, "count").reset_index(drop=True)
        for rank, (_, row) in enumerate(sub.iterrows()):
            short = row["subjectLabel"][:10] + "…" if len(row["subjectLabel"]) > 10 else row["subjectLabel"]
            ax.text(rank + offsets[idx], row["count"] * 1.02,
                    short, ha="center", va="bottom",
                    fontsize=5.5, color=C_SLATE, rotation=45)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    df_subjects = pd.read_csv(F_SUBJECTS)
    df_century  = pd.read_csv(F_CENTURY)
    df_lang     = pd.read_csv(F_LANG)

    fig = plt.figure(figsize=(18, 14), facecolor="white")
    fig.suptitle("BnF — Subjects & Themes Analysis  (Question 3)",
                 fontsize=15, fontweight="bold", color="#111111", y=0.985)

    gs = GridSpec(2, 2, figure=fig,
                  hspace=0.46, wspace=0.32,
                  left=0.05, right=0.97,
                  top=0.94, bottom=0.06)

    plot_top_subjects(fig.add_subplot(gs[0, 0]), df_subjects)
    plot_subject_evolution(fig.add_subplot(gs[0, 1]), df_century)
    plot_language_heatmap(fig.add_subplot(gs[1, 0]), df_lang)
    plot_language_top5(fig.add_subplot(gs[1, 1]), df_lang)

    fig.text(0.5, 0.003,
             "Source: data.bnf.fr/sparql  ·  RAMEAU subject headings",
             ha="center", fontsize=7.5, color=C_SLATE)

    out = HERE / "bnf_subjects_themes.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved → {out}")
    plt.show()

if __name__ == "__main__":
    main()
