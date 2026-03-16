"""
BnF Catalogue — Authorities & Linked Data Visualization (Question 4)
=====================================================================
Reads three CSV result files and produces a 4-panel figure.

Panels:
  1. Authority records by type (donut chart)
  2. Percentage of bibliographic records linked to authority (gauge/bar)
  3. External source alignments (horizontal bar)
  4. Authority type proportions vs total catalogue (stacked comparison)
"""

import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.gridspec import GridSpec

HERE = pathlib.Path(__file__).parent

F_AUTH    = HERE / "queryResults_Q4_1_authority_counts.csv"
F_LINKAGE = HERE / "queryResults_Q4_2_authority_linkage.csv"
F_EXT     = HERE / "queryResults_Q4_3_external_alignments.csv"

C_NAVY   = "#1a3f6f"
C_GOLD   = "#c8922a"
C_TEAL   = "#1d7c6e"
C_CORAL  = "#c0432f"
C_SLATE  = "#5a6472"
C_LIGHT  = "#f7f5f0"
C_GRID   = "#e2dfd8"
C_PURPLE = "#7b5ea7"
C_GREEN  = "#3a7d44"

TYPE_COLORS = [C_NAVY, C_TEAL, C_GOLD, C_CORAL]

EXT_COLORS = {
    "VIAF":        "#1a3f6f",
    "Wikidata":    "#c8922a",
    "IdRef":       "#1d7c6e",
    "ISNI":        "#c0432f",
    "DBpedia":     "#7b5ea7",
    "GeoNames":    "#3a7d44",
    "MusicBrainz": "#d4762a",
    "Other":       "#5a6472",
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

# ── Panel 1: Authority records by type (donut) ────────────────────────────────

def plot_authority_donut(ax, df):
    df = df.copy()
    df["count"] = pd.to_numeric(df["count"])
    df = df.sort_values("count", ascending=False)

    total = df["count"].sum()
    colors = TYPE_COLORS[:len(df)]

    wedges, texts, autotexts = ax.pie(
        df["count"],
        labels=None,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%",
        pctdistance=0.75,
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
    )

    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    # Centre label
    ax.text(0, 0, f"Total\n{fmt(total)}", ha="center", va="center",
            fontsize=9, fontweight="bold", color="#111111")

    # Legend
    legend_labels = [f"{row['type']}  ({fmt(row['count'])})"
                     for _, row in df.iterrows()]
    patches = [mpatches.Patch(color=colors[i], label=legend_labels[i])
               for i in range(len(df))]
    ax.legend(handles=patches, loc="lower center", bbox_to_anchor=(0.5, -0.12),
              fontsize=7.5, framealpha=0.7, ncol=2)

    ax.set_title("Authority records by type", fontsize=10.5,
                 fontweight="bold", color="#111111", pad=9)

# ── Panel 2: Linkage percentage (horizontal stacked bar) ─────────────────────

def plot_linkage(ax, df):
    df = df.copy()
    df = df.set_index("metric")
    df["value"] = pd.to_numeric(df["value"])

    total    = df.loc["Total bibliographic records", "value"]
    linked   = df.loc["Records linked to creator authority", "value"]
    unlinked = df.loc["Records with no creator link", "value"]
    pct      = df.loc["Percentage linked", "value"]

    # Stacked horizontal bar
    ax.barh(["BnF Catalogue"], [linked],   color=C_TEAL,  height=0.4,
            label=f"Linked ({fmt(linked)})", zorder=2)
    ax.barh(["BnF Catalogue"], [unlinked], color=C_CORAL, height=0.4,
            left=[linked], label=f"Not linked ({fmt(unlinked)})", zorder=2)

    # Percentage annotation in the middle of linked bar
    ax.text(linked / 2, 0,
            f"{pct}% linked",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color="white")

    ax.text(linked + unlinked / 2, 0,
            f"{100 - pct:.1f}%\nnot linked",
            ha="center", va="center",
            fontsize=9, fontweight="bold", color="white")

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_facecolor(C_LIGHT)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    ax.set_title("Bibliographic records linked to a creator authority",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    ax.set_xlabel(f"Total records: {fmt(total)}", fontsize=8, color=C_SLATE)
    ax.legend(fontsize=8, loc="lower right", framealpha=0.7)

# ── Panel 3: External alignments (horizontal bar) ────────────────────────────

def plot_external_alignments(ax, df):
    df = df.copy()
    df["alignmentCount"] = pd.to_numeric(df["alignmentCount"])
    df = df.sort_values("alignmentCount", ascending=True)

    colors = [EXT_COLORS.get(s, C_SLATE) for s in df["externalSource"]]
    bars = ax.barh(df["externalSource"], df["alignmentCount"],
                   color=colors, height=0.6, zorder=2)

    total = df["alignmentCount"].sum()
    for bar, val in zip(bars, df["alignmentCount"]):
        pct = val / total * 100
        ax.text(bar.get_width() * 1.01,
                bar.get_y() + bar.get_height() / 2,
                f"{fmt(val)}  ({pct:.1f}%)",
                va="center", ha="left", fontsize=7.5, color=C_SLATE)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_xlim(right=df["alignmentCount"].max() * 1.45)
    style_ax(ax, "External source alignments (Wikidata, VIAF, IdRef…)")
    ax.set_xlabel(f"Alignment links  ·  total {fmt(total)}",
                  fontsize=8, color=C_SLATE)

# ── Panel 4: Authority types vs catalogue scale ───────────────────────────────

def plot_scale_comparison(ax, df_auth, df_linkage):
    df_auth = df_auth.copy()
    df_auth["count"] = pd.to_numeric(df_auth["count"])
    df_linkage = df_linkage.copy()
    df_linkage = df_linkage.set_index("metric")
    df_linkage["value"] = pd.to_numeric(df_linkage["value"])

    total_bib = df_linkage.loc["Total bibliographic records", "value"]

    categories = list(df_auth["type"]) + ["Bibliographic\nRecords"]
    values     = list(df_auth["count"]) + [total_bib]
    colors     = TYPE_COLORS[:len(df_auth)] + [C_NAVY]

    bars = ax.bar(categories, values, color=colors, width=0.6,
                  zorder=2, edgecolor="white", linewidth=1.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() * 1.02,
                fmt(val), ha="center", va="bottom",
                fontsize=8, color=C_SLATE, fontweight="bold")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_facecolor(C_LIGHT)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    ax.set_title("Authority types vs total catalogue scale",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    ax.set_ylabel("Record count", fontsize=8, color=C_SLATE)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    df_auth    = pd.read_csv(F_AUTH)
    df_linkage = pd.read_csv(F_LINKAGE)
    df_ext     = pd.read_csv(F_EXT)

    fig = plt.figure(figsize=(18, 14), facecolor="white")
    fig.suptitle("BnF — Authorities & Linked Data Analysis  (Question 4)",
                 fontsize=15, fontweight="bold", color="#111111", y=0.985)

    gs = GridSpec(2, 2, figure=fig,
                  hspace=0.46, wspace=0.32,
                  left=0.05, right=0.97,
                  top=0.94, bottom=0.06)

    plot_authority_donut(fig.add_subplot(gs[0, 0]), df_auth)
    plot_linkage(fig.add_subplot(gs[0, 1]), df_linkage)
    plot_external_alignments(fig.add_subplot(gs[1, 0]), df_ext)
    plot_scale_comparison(fig.add_subplot(gs[1, 1]), df_auth, df_linkage)

    fig.text(0.5, 0.003,
             "Source: data.bnf.fr/sparql  ·  BnF Authority Records & Linked Data",
             ha="center", fontsize=7.5, color=C_SLATE)

    out = HERE / "bnf_authorities_linked_data.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved → {out}")
    plt.show()

if __name__ == "__main__":
    main()
