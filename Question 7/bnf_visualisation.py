
import argparse
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
BLUE   = "#2C5F8A"
TEAL   = "#1D9E75"
AMBER  = "#D4840A"
RED    = "#C0392B"
PURPLE = "#6C4AB6"
GRAY   = "#8D8D8D"
BG     = "#F7F6F3"
PANEL  = "#FFFFFF"
TEXT   = "#1A1A1A"
MUTED  = "#6B6B6B"

SCORE_COLORS = [RED, AMBER, AMBER, BLUE, TEAL]   # 0-4

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_int(n):
    return f"{int(n):,}"

def fmt_pct(v, total):
    if total == 0:
        return "0.0%"
    return f"{v / total * 100:.1f}%"

def clean_title(t, max_len=52):
    t = str(t).strip().strip('"')
    return textwrap.shorten(t, width=max_len, placeholder="…")


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_quality(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip('"').str.strip()
    for c in df.columns:
        df[c] = pd.to_numeric(df[c].astype(str).str.strip('"'), errors="coerce")
    return df.iloc[0]

def load_dupes(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip('"').str.strip()
    df["title"] = df["title"].astype(str).str.strip('"')
    df["copies"] = pd.to_numeric(df["copies"].astype(str).str.strip('"'), errors="coerce")
    return df.dropna(subset=["copies"]).sort_values("copies", ascending=False)

def load_scores(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip('"').str.strip()
    df["score"] = pd.to_numeric(df["score"].astype(str).str.strip('"'), errors="coerce")
    df["recordCount"] = pd.to_numeric(df["recordCount"].astype(str).str.strip('"'), errors="coerce")
    return df.dropna().sort_values("score")



# Panel A — field coverage bar chart


def draw_coverage(ax, row):
    total = row["total"]
    fields = {
        "Date\n(dcterms:date)":       row["hasDate"],
        "Language\n(dcterms:language)": row["hasLang"],
        "Subject\n(dcterms:subject)": row["hasSubject"],
        "Author\n(marcrel:aut)":       row["hasAuthor"],
    }

    labels = list(fields.keys())
    values = [v / total * 100 for v in fields.values()]
    colors = [BLUE, TEAL, AMBER, PURPLE]

    bars = ax.barh(labels, values, color=colors, height=0.55, zorder=3)

    for bar, raw in zip(bars, fields.values()):
        w = bar.get_width()
        ax.text(min(w + 1.5, 97), bar.get_y() + bar.get_height() / 2,
                f"{w:.1f}%  ({fmt_int(raw)})",
                va="center", ha="left", fontsize=9, color=MUTED)

    ax.set_xlim(10, 115)
    ax.set_xlabel("% of records", fontsize=9, color=MUTED)
    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=8, colors=MUTED)
    ax.set_facecolor(PANEL)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.grid(axis="x", color="#EEEEEE", zorder=0)
    ax.invert_yaxis()

    # Fully-complete annotation
    all_four = min(fields.values())



# Panel B — score distribution (stacked / grouped bar)


def draw_scores(ax, df):
    total = df["recordCount"].sum()
    scores = df["score"].astype(int).tolist()
    counts = df["recordCount"].astype(int).tolist()
    pcts   = [c / total * 100 for c in counts]
    colors = [SCORE_COLORS[min(s, 4)] for s in scores]

    bars = ax.bar(scores, pcts, color=colors, width=0.6, zorder=3)

    for bar, cnt, pct in zip(bars, counts, pcts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{pct:.1f}%\n{fmt_int(cnt)}",
                ha="center", va="bottom", fontsize=8, color=MUTED, linespacing=1.4)

    ax.set_xticks(scores)
    ax.set_xticklabels([f"Score {s}/4" for s in scores], fontsize=9)
    ax.set_ylabel("% of total records", fontsize=9, color=MUTED)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.tick_params(axis="y", labelsize=8, colors=MUTED)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_facecolor(PANEL)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.grid(axis="y", color="#EEEEEE", zorder=0)
    ax.set_ylim(0, max(pcts) * 1.25)

    # Legend
    legend_items = [
        mpatches.Patch(color=RED,   label="0 — no metadata"),
        mpatches.Patch(color=AMBER, label="1–2 — partial"),
        mpatches.Patch(color=BLUE,  label="3 — good"),
        mpatches.Patch(color=TEAL,  label="4 — complete"),
    ]
    ax.legend(handles=legend_items, fontsize=8, frameon=False,
              loc="upper right", labelcolor=MUTED)


# ---------------------------------------------------------------------------
# Panel C — top duplicates horizontal bar
# ---------------------------------------------------------------------------

def draw_dupes(ax, df, n=20):
    top = df.head(n).copy()
    top["label"] = top["title"].apply(lambda t: clean_title(t, 55))
    top = top.sort_values("copies", ascending=True)

    # Colour by rough category
    def cat_color(t):
        t = t.lower()
        if "monnaie" in t or "drachme" in t or "tétradrachme" in t or "statère" in t:
            return AMBER
        if "recueil" in t or "programme" in t or "document" in t:
            return TEAL
        if "estampe" in t or "dessin" in t or "photogr" in t:
            return PURPLE
        return BLUE

    colors = [cat_color(t) for t in top["title"]]
    bars = ax.barh(top["label"], top["copies"], color=colors, height=0.65, zorder=3)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 20, bar.get_y() + bar.get_height() / 2,
                fmt_int(w), va="center", fontsize=8, color=MUTED)

    ax.set_xlabel("Number of duplicate records", fontsize=9, color=MUTED)
    ax.tick_params(axis="y", labelsize=7.5)
    ax.tick_params(axis="x", labelsize=8, colors=MUTED)
    ax.set_facecolor(PANEL)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.grid(axis="x", color="#EEEEEE", zorder=0)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: fmt_int(x)))

    legend_items = [
        mpatches.Patch(color=AMBER,  label="Numismatics"),
        mpatches.Patch(color=TEAL,   label="Printed collections"),
        mpatches.Patch(color=PURPLE, label="Graphic / photography"),
        mpatches.Patch(color=BLUE,   label="Other"),
    ]
    ax.legend(handles=legend_items, fontsize=8, frameon=False,
              loc="lower right", labelcolor=MUTED)


# ---------------------------------------------------------------------------
# Summary metric strip
# ---------------------------------------------------------------------------

def draw_metrics(ax, row, scores_df):
    ax.set_facecolor(BG)
    ax.axis("off")

    total  = int(row["total"])
    score4 = int(scores_df[scores_df["score"] == 4]["recordCount"].sum())
    score0 = int(scores_df[scores_df["score"] == 0]["recordCount"].sum())

    metrics = [
        ("Total records",         fmt_int(total),                    BLUE),
        ("Have a date",           fmt_pct(row["hasDate"],   total),  TEAL),
        ("Have a language",       fmt_pct(row["hasLang"],   total),  TEAL),
        ("Have a subject",        fmt_pct(row["hasSubject"],total),  AMBER),
        ("Have an author",        fmt_pct(row["hasAuthor"], total),  PURPLE),
        ("Score 4/4 (complete)",  fmt_pct(score4,           total),  TEAL),
        ("Score 0/4 (empty)",     fmt_pct(score0,           total),  RED),
    ]

    n = len(metrics)
    xs = np.linspace(0.04, 0.96, n)

    for x, (label, value, color) in zip(xs, metrics):
        ax.text(x, 0.72, value, ha="center", va="bottom",
                fontsize=17, fontweight="bold", color=color,
                transform=ax.transAxes)
        ax.text(x, 0.30, label, ha="center", va="top",
                fontsize=7.5, color=MUTED, transform=ax.transAxes,
                wrap=True)

    ax.axhline(0.05, color="#DDDDDD", linewidth=0.8)


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

def build_figure(quality_row, dupes_df, scores_df, out_path):
    fig = plt.figure(figsize=(18, 16), facecolor=BG)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.93, bottom=0.04,
                        hspace=0.55, wspace=0.35)

    # Title
    fig.text(0.5, 0.965,
             "Metadata Quality Report",
             ha="center", va="top", fontsize=16, fontweight="bold", color=TEXT)
    fig.text(0.5, 0.930,
             f"Based on {fmt_int(quality_row['total'])} bibliographic records  ·  "
             "Fields: dcterms:date · dcterms:language · dcterms:subject · marcrel:aut",
             ha="center", va="top", fontsize=9, color=MUTED)

    # Grid: 3 rows, 2 cols
    # Row 0: metric strip (full width)
    # Row 1: coverage (left) + score dist (right)
    # Row 2: duplicates (full width)
    gs = fig.add_gridspec(3, 2,
                          height_ratios=[0.33, 0.58, 0.69],
                          hspace=0.52, wspace=0.32)
    
    ax_coverage = fig.add_subplot(gs[1, 0])
    ax_scores   = fig.add_subplot(gs[1, 1])
    ax_dupes    = fig.add_subplot(gs[2, :])

    for ax, title in [
        (ax_coverage, "Field coverage across all records"),
        (ax_scores,   "Completeness score distribution  (0 = no metadata · 4 = all fields)"),
        (ax_dupes,    "Top 20 duplicate groups by record count"),
    ]:
        ax.set_facecolor(PANEL)
        ax.set_title(title, fontsize=10.5, fontweight="bold", color=TEXT,
                     pad=10, loc="left")

    draw_coverage(ax_coverage, quality_row)
    draw_scores(ax_scores, scores_df)
    draw_dupes(ax_dupes, dupes_df)

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
    print(f"Saved → {out_path}")
    plt.show()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualise BnF SPARQL results")
    parser.add_argument("--quality", default="queryResults_Q7_1_doc_quality.csv")
    parser.add_argument("--dupes",   default="queryResults_Q7_2_duplicates.csv")
    parser.add_argument("--scores",  default="queryResults_Q7_3_datascore.csv")
    parser.add_argument("--out",     default="bnf_metadata_report.png")
    args = parser.parse_args()

    quality_row = load_quality(args.quality)
    dupes_df    = load_dupes(args.dupes)
    scores_df   = load_scores(args.scores)

    build_figure(quality_row, dupes_df, scores_df, args.out)
