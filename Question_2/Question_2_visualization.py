import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import re

# ── Styling ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e8e8e8",
    "grid.linewidth": 0.6,
    "axes.labelcolor": "#444",
    "xtick.color": "#555",
    "ytick.color": "#555",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

BLUE   = "#2563a8"
GRAY   = "#9ca3af"
TEAL   = "#0d9488"
AMBER  = "#d97706"
CORAL  = "#e05c3a"
PURPLE = "#7c3aed"
GREEN  = "#16a34a"

LANG_COLORS = {
    "fre": BLUE, "eng": TEAL, "ger": AMBER,
    "ita": CORAL, "spa": PURPLE,
}
LANG_LABELS = {
    "fre": "French", "eng": "English", "ger": "German",
    "ita": "Italian", "spa": "Spanish",
}

def extract_code(uri):
    return uri.split("/")[-1]

# ── Load data ──────────────────────────────────────────────────────────────────
q1 = pd.read_csv("queryResults_Q2_1_top_languages_found.csv")
q2 = pd.read_csv("queryResults_Q2_2_top_languages_per_decade.csv")
q3 = pd.read_csv("queryResults_Q2_3_place_published.csv")
q4 = pd.read_csv("queryResults_Q2_4_ratio_french_total.csv")

q1["code"] = q1["lang"].apply(extract_code)
q2["code"] = q2["lang"].apply(extract_code)

# ── Figure setup: 2×2 grid ─────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 14))
fig.suptitle("BnF Collection — Language & Geography Analysis", fontsize=16,
             fontweight="bold", color="#1a1a2e", y=0.98)

axes = [
    fig.add_subplot(2, 2, 1),
    fig.add_subplot(2, 2, 2),
    fig.add_subplot(2, 2, 3),
    fig.add_subplot(2, 2, 4),
]

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Top 20 languages (horizontal bar)
# ══════════════════════════════════════════════════════════════════════════════
ax1 = axes[0]

LANG_NAMES = {
    "fre":"French","eng":"English","ger":"German","ita":"Italian",
    "zxx":"No linguistic content","lat":"Latin","spa":"Spanish",
    "grc":"Ancient Greek","rus":"Russian","dut":"Dutch","por":"Portuguese",
    "chi":"Chinese","pol":"Polish","ara":"Arabic","jpn":"Japanese",
    "frm":"Middle French","swe":"Swedish","cze":"Czech","heb":"Hebrew",
    "hun":"Hungarian",
}

q1_plot = q1.copy()
q1_plot["name"] = q1_plot["code"].map(lambda c: LANG_NAMES.get(c, c))
q1_plot = q1_plot.sort_values("nb")

colors = [BLUE if c == "fre" else GRAY for c in q1_plot["code"]]
bars = ax1.barh(q1_plot["name"], q1_plot["nb"], color=colors, height=0.7)

total = q1_plot["nb"].sum()
for bar, val in zip(bars, q1_plot["nb"]):
    pct = val / total * 100
    ax1.text(bar.get_width() + total * 0.005, bar.get_y() + bar.get_height() / 2,
             f"{pct:.1f}%", va="center", ha="left", fontsize=8, color="#555")

ax1.set_xlabel("Number of records", fontsize=9)
ax1.set_title("Top 20 languages", fontweight="bold", fontsize=11, pad=10)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M" if x >= 1e6 else f"{int(x/1e3)}k"))
ax1.set_xlim(0, q1_plot["nb"].max() * 1.18)

blue_patch = mpatches.Patch(color=BLUE, label="French")
gray_patch = mpatches.Patch(color=GRAY, label="Other languages")
ax1.legend(handles=[blue_patch, gray_patch], fontsize=8, loc="lower right")

# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Language % share per decade (stacked area)
# ══════════════════════════════════════════════════════════════════════════════
ax2 = axes[1]

pivot = q2.pivot_table(index="decade", columns="code", values="nb", fill_value=0)
pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
pivot_pct = pivot_pct.sort_index()
decades = pivot_pct.index.astype(int)

plot_langs = ["fre", "eng", "ger", "ita", "spa"]
available = [l for l in plot_langs if l in pivot_pct.columns]

bottom = pd.Series(0.0, index=pivot_pct.index)
for lang in available:
    vals = pivot_pct[lang]
    ax2.fill_between(decades, bottom, bottom + vals,
                     color=LANG_COLORS[lang], alpha=0.85, linewidth=0)
    mid = bottom + vals / 2
    # label only if area is big enough
    for i, (d, m, v) in enumerate(zip(decades, mid, vals)):
        if v > 4 and d == 1970:
            ax2.text(d, float(m), LANG_LABELS[lang], ha="center", va="center",
                     fontsize=8, color="white", fontweight="bold")
    bottom = bottom + vals

# "Other" remainder
other = 100 - bottom
ax2.fill_between(decades, bottom, bottom + other,
                 color="#d1d5db", alpha=0.6, linewidth=0, label="Other")

ax2.set_xlim(decades.min(), decades.max())
ax2.set_ylim(0, 100)
ax2.set_xlabel("Decade", fontsize=9)
ax2.set_ylabel("Share (%)", fontsize=9)
ax2.set_title("Language share by decade (stacked area)", fontweight="bold", fontsize=11, pad=10)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x)}%"))

legend_handles = [mpatches.Patch(color=LANG_COLORS[l], label=LANG_LABELS[l]) for l in available]
legend_handles.append(mpatches.Patch(color="#d1d5db", label="Other"))
ax2.legend(handles=legend_handles, fontsize=8, loc="upper left",
           bbox_to_anchor=(0.01, 0.99), framealpha=0.85)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — French share % per decade (line)
# ══════════════════════════════════════════════════════════════════════════════
ax3 = axes[2]

q4["pct_french"] = q4["french"] / q4["total"] * 100
q4_sorted = q4.sort_values("decade")

ax3.plot(q4_sorted["decade"].astype(int), q4_sorted["pct_french"],
         color=BLUE, linewidth=2.5, marker="o", markersize=5, zorder=3)
ax3.fill_between(q4_sorted["decade"].astype(int), q4_sorted["pct_french"],
                 color=BLUE, alpha=0.12)

# Annotate a few key points
for _, row in q4_sorted.iterrows():
    if row["decade"] in [1800, 1900, 1940, 1970, 2010]:
        ax3.annotate(f"{row['pct_french']:.0f}%",
                     xy=(row["decade"], row["pct_french"]),
                     xytext=(0, 10), textcoords="offset points",
                     ha="center", fontsize=8, color=BLUE)

ax3.set_xlabel("Decade", fontsize=9)
ax3.set_ylabel("French share (%)", fontsize=9)
ax3.set_title("French-language share over time", fontweight="bold", fontsize=11, pad=10)
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x)}%"))
ax3.set_ylim(0, 105)

# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Top publication places (clean, excluding unknowns)
# ══════════════════════════════════════════════════════════════════════════════
ax4 = axes[3]

UNKNOWN_PATTERNS = [
    r"^\[S", r"^S\.l", r"^\(S\.", r"^\[Europe\]",
    r"^\[France\]", r"^\(Paris,?\)$", r"^\[Paris\]$",
]

def is_unknown(place):
    return any(re.match(pat, str(place)) for pat in UNKNOWN_PATTERNS)

q3_clean = q3[~q3["place"].apply(is_unknown)].copy()
# Also exclude bare [Paris] variant but keep real Paris entries for context
# We already filter [Paris] above; "Paris" proper wasn't in top 30 (it's in the filter)
q3_top = q3_clean.head(15).sort_values("nb")

# Color: French cities vs foreign
french_cities = {"Lyon","Toulouse","Bordeaux","Saint-Denis","Montpellier","Grenoble"}
bar_colors = [TEAL if c in french_cities else CORAL for c in q3_top["place"]]

bars = ax4.barh(q3_top["place"], q3_top["nb"], color=bar_colors, height=0.7)

for bar, val in zip(bars, q3_top["nb"]):
    ax4.text(bar.get_width() + q3_top["nb"].max() * 0.01,
             bar.get_y() + bar.get_height() / 2,
             f"{int(val):,}", va="center", ha="left", fontsize=8, color="#555")

ax4.set_xlabel("Number of records", fontsize=9)
ax4.set_title("Top publication places (excl. Paris & unknowns)", fontweight="bold", fontsize=11, pad=10)
ax4.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x/1e3)}k"))
ax4.set_xlim(0, q3_top["nb"].max() * 1.18)

fr_patch  = mpatches.Patch(color=TEAL,  label="French cities")
int_patch = mpatches.Patch(color=CORAL, label="Foreign cities")
ax4.legend(handles=[fr_patch, int_patch], fontsize=8, loc="lower right")

# ── Layout & save ──────────────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("bnf_analysis.png", dpi=150, bbox_inches="tight")
print("Saved.")