"""
BnF Catalogue — Digitization & Access Visualization (Question 5)
=================================================================
4-panel figure using real BnF SPARQL data.

Q5.1 — What share of collection has a Gallica link?
Q5.2 — Is there a bias in what gets digitized (format/language)?
Q5.3 — How does digitized volume vary across centuries?
"""

import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.gridspec import GridSpec

HERE = pathlib.Path(__file__).parent

F_SHARE   = HERE / "queryResults_Q5_1_gallica_share.csv"
F_TYPE    = HERE / "queryResults_Q5_2_digitization_by_type.csv"
F_DATE    = HERE / "queryResults_Q5_3_digitized_by_date.csv"
F_CENTURY = HERE / "queryResults_Q5_3b_digitized_by_century.csv"
F_LANG    = HERE / "queryResults_Q5_4_digitization_by_language.csv"

C_NAVY   = "#1a3f6f"
C_GOLD   = "#c8922a"
C_TEAL   = "#1d7c6e"
C_CORAL  = "#c0432f"
C_SLATE  = "#5a6472"
C_LIGHT  = "#f7f5f0"
C_GRID   = "#e2dfd8"
C_PURPLE = "#7b5ea7"
C_GREY   = "#d9d5ce"

LANG_NAMES = {
    "http://id.loc.gov/vocabulary/iso639-2/fre": "French",
    "http://id.loc.gov/vocabulary/iso639-2/ger": "German",
    "http://id.loc.gov/vocabulary/iso639-2/eng": "English",
    "http://id.loc.gov/vocabulary/iso639-2/ita": "Italian",
    "http://id.loc.gov/vocabulary/iso639-2/spa": "Spanish",
    "http://id.loc.gov/vocabulary/iso639-2/oci": "Occitan",
    "http://id.loc.gov/vocabulary/iso639-2/dut": "Dutch",
    "http://id.loc.gov/vocabulary/iso639-2/vie": "Vietnamese",
    "http://id.loc.gov/vocabulary/iso639-2/ara": "Arabic",
    "http://id.loc.gov/vocabulary/iso639-2/pol": "Polish",
    "http://id.loc.gov/vocabulary/iso639-2/rus": "Russian",
    "http://id.loc.gov/vocabulary/iso639-2/yid": "Yiddish",
    "http://id.loc.gov/vocabulary/iso639-2/por": "Portuguese",
    "http://id.loc.gov/vocabulary/iso639-2/bre": "Breton",
    "http://id.loc.gov/vocabulary/iso639-2/dan": "Danish",
    "http://id.loc.gov/vocabulary/iso639-2/gsw": "Alsatian",
    "http://id.loc.gov/vocabulary/iso639-2/baq": "Basque",
    "http://id.loc.gov/vocabulary/iso639-2/mlg": "Malagasy",
    "http://id.loc.gov/vocabulary/iso639-2/arm": "Armenian",
    "http://id.loc.gov/vocabulary/iso639-2/ota": "Ottoman Turkish",
}

TYPE_NAMES = {
    "http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation": "Manifestation",
    "http://purl.org/ontology/bibo/Periodical": "Periodical",
    "http://rdvocab.info/uri/schema/FRBRentitiesRDA/Work": "Work",
    "http://rdaregistry.info/Elements/c/#C10007": "RDA Manifestation",
    "http://rdaregistry.info/Elements/c/#C10001": "RDA Work",
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

# ── Panel 1: Gallica share donut ─────────────────────────────────────────────

def plot_gallica_share(ax, df):
    df = df.set_index("metric")
    df["value"] = pd.to_numeric(df["value"])

    digitized = df.loc["Digitized records (Gallica)", "value"]
    not_digit = df.loc["Not digitized", "value"]
    total     = df.loc["Total catalogue records", "value"]
    pct       = df.loc["Percentage digitized", "value"]

    wedges, _, autotexts = ax.pie(
        [digitized, not_digit],
        colors=[C_TEAL, C_GREY],
        autopct=lambda p: f"{p:.1f}%",
        pctdistance=0.72,
        startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2.5),
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.text(0, 0.08, f"{pct}%", ha="center", va="center",
            fontsize=16, fontweight="bold", color=C_TEAL)
    ax.text(0, -0.18, "digitized", ha="center", va="center",
            fontsize=9, color=C_SLATE)

    patches = [
        mpatches.Patch(color=C_TEAL, label=f"Digitized on Gallica: {fmt(digitized)}"),
        mpatches.Patch(color=C_GREY, label=f"Not digitized: {fmt(not_digit)}"),
    ]
    ax.legend(handles=patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.12), fontsize=8,
              framealpha=0.7, ncol=1)
    ax.set_title(f"Share of collection with Gallica link\n(Total: {fmt(total)} records)",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)

# ── Panel 2: Digitized volume by year 1500-2000 ───────────────────────────────

def plot_by_year(ax, df):
    df = df.copy()
    df.columns = ["date", "count"]
    df["date"]  = pd.to_numeric(df["date"], errors="coerce")
    df["count"] = pd.to_numeric(df["count"])
    df = df.dropna().sort_values("date")

    # 5yr rolling average
    full = df.set_index("date")["count"].reindex(
        range(int(df["date"].min()), 2001), fill_value=0
    ).rolling(5, center=True, min_periods=1).mean().reset_index()
    full.columns = ["date", "count"]

    ax.fill_between(full["date"], full["count"],
                    alpha=0.18, color=C_NAVY, zorder=1)
    ax.plot(full["date"], full["count"],
            color=C_NAVY, linewidth=2, zorder=3)

    # Annotate key events
    events = {
        1789: ("Revolution\n1789", "above"),
        1870: ("Franco-Prussian\nWar", "above"),
        1914: ("WWI", "above"),
        1932: ("Peak\n1932", "above"),
    }
    for year, (label, pos) in events.items():
        row = full[full["date"] == year]
        if not row.empty:
            yval = row["count"].values[0]
            ax.axvline(year, color=C_GOLD, linewidth=1,
                       linestyle="--", alpha=0.8, zorder=2)
            ax.annotate(label,
                        xy=(year, yval),
                        xytext=(6, 10), textcoords="offset points",
                        fontsize=6.5, color=C_GOLD,
                        arrowprops=dict(arrowstyle="-", color=C_GOLD, lw=0.7))

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, zorder=0)
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_facecolor(C_LIGHT)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    ax.set_title("Digitized works by publication year (5-yr rolling avg)",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    ax.set_ylabel("Digitized works per year", fontsize=8, color=C_SLATE)
    ax.set_xlabel("Publication year", fontsize=8, color=C_SLATE)

# ── Panel 3: Digitized by century (bar) ──────────────────────────────────────

def plot_by_century(ax, df):
    df = df.copy()
    df.columns = ["century", "count"]
    df["count"] = pd.to_numeric(df["count"])
    df["label"] = df["century"].astype(int).apply(
        lambda c: f"{c//100 + 1}th c.\n({c}s)"
    )

    colors = [C_TEAL if i < len(df) - 1 else C_NAVY
              for i in range(len(df))]
    bars = ax.bar(df["label"], df["count"],
                  color=colors, width=0.6, zorder=2,
                  edgecolor="white", linewidth=1.5)

    total = df["count"].sum()
    for bar, val in zip(bars, df["count"]):
        pct = val / total * 100
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() * 1.02,
                f"{fmt(val)}\n({pct:.1f}%)",
                ha="center", va="bottom",
                fontsize=7.5, color=C_SLATE)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt(v)))
    ax.grid(axis="y", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_facecolor(C_LIGHT)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.tick_params(colors=C_SLATE, labelsize=8)
    ax.set_title("Volume of digitized content by century",
                 fontsize=10.5, fontweight="bold", color="#111111", pad=9)
    ax.set_ylabel("Digitized records", fontsize=8, color=C_SLATE)
    ax.set_ylim(top=df["count"].max() * 1.25)

# ── Panel 4: Language bias ────────────────────────────────────────────────────

def plot_language_bias(ax, df):
    df = df.copy()
    df.columns = ["language", "count"]
    df["count"] = pd.to_numeric(df["count"])
    df["lang"]  = df["language"].map(LANG_NAMES).fillna("Other")
    df = df.groupby("lang")["count"].sum().reset_index()
    df = df.sort_values("count", ascending=True)

    total = df["count"].sum()
    colors = [C_NAVY if row["lang"] == "French" else C_TEAL
              for _, row in df.iterrows()]

    bars = ax.barh(df["lang"], df["count"],
                   color=colors, height=0.6, zorder=2)

    for bar, val in zip(bars, df["count"]):
        pct = val / total * 100
        ax.text(bar.get_width() * 1.01,
                bar.get_y() + bar.get_height() / 2,
                f"{fmt(val)}  ({pct:.1f}%)",
                va="center", ha="left", fontsize=7.5, color=C_SLATE)

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt(x)))
    ax.grid(axis="x", color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_xlim(right=df["count"].max() * 1.5)
    style_ax(ax, "Digitization bias by language")
    ax.set_xlabel(f"Digitized records with language tag  ·  total {fmt(total)}",
                  fontsize=8, color=C_SLATE)

    french_pct = df[df["lang"] == "French"]["count"].values[0] / total * 100
    ax.text(0.97, 0.05,
            f"French = {french_pct:.1f}%\nof tagged records",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color="white", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4",
                      facecolor=C_NAVY, edgecolor=C_NAVY, alpha=0.9))

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    df_share   = pd.read_csv(F_SHARE)
    df_type    = pd.read_csv(F_TYPE)
    df_date    = pd.read_csv(F_DATE)
    df_century = pd.read_csv(F_CENTURY)
    df_lang    = pd.read_csv(F_LANG)

    fig = plt.figure(figsize=(18, 14), facecolor="white")
    fig.suptitle("BnF — Digitization & Access Analysis  (Question 5)",
                 fontsize=15, fontweight="bold", color="#111111", y=0.985)

    gs = GridSpec(2, 2, figure=fig,
                  hspace=0.46, wspace=0.32,
                  left=0.06, right=0.97,
                  top=0.94, bottom=0.07)

    plot_gallica_share(fig.add_subplot(gs[0, 0]), df_share)
    plot_by_year(fig.add_subplot(gs[0, 1]), df_date)
    plot_by_century(fig.add_subplot(gs[1, 0]), df_century)
    plot_language_bias(fig.add_subplot(gs[1, 1]), df_lang)

    fig.text(0.5, 0.003,
             "Source: data.bnf.fr/sparql  ·  Gallica digitization data  ·  rdarelationships:electronicReproduction",
             ha="center", fontsize=7.5, color=C_SLATE)

    out = HERE / "bnf_digitization_access.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved → {out}")
    plt.show()

if __name__ == "__main__":
    main()
