from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PALETTE = ["#14B8A6", "#F43F5E", "#F59E0B", "#60A5FA", "#A78BFA", "#94A3B8"]
SEQUENTIAL = ["#E0F2FE", "#7DD3FC", "#38BDF8", "#0369A1", "#0F172A"]
FIGURE_BACKGROUND = "#111827"
AXIS_BACKGROUND = "#151f32"
GRID_COLOR = "#334155"
TEXT_COLOR = "#f8fafc"
MUTED_TEXT = "#a7b0c0"
SPINE_COLOR = "#475569"

sns.set_theme(
    style="darkgrid",
    context="notebook",
    rc={
        "axes.facecolor": AXIS_BACKGROUND,
        "figure.facecolor": FIGURE_BACKGROUND,
        "axes.edgecolor": SPINE_COLOR,
        "axes.labelcolor": TEXT_COLOR,
        "axes.titlecolor": TEXT_COLOR,
        "xtick.color": MUTED_TEXT,
        "ytick.color": MUTED_TEXT,
        "grid.color": GRID_COLOR,
        "text.color": TEXT_COLOR,
        "legend.facecolor": AXIS_BACKGROUND,
        "legend.edgecolor": SPINE_COLOR,
    },
)
warnings.filterwarnings(
    "ignore",
    category=PendingDeprecationWarning,
    message="vert: bool will be deprecated.*",
)


def plot_winner_pie(cups: pd.DataFrame):
    if cups.empty:
        return _empty_figure("World Cup Titles by Winner")

    winners = cups["Winner"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    wedges, _, _ = ax.pie(
        winners.values,
        labels=None,
        autopct="%1.1f%%",
        startangle=90,
        colors=_colors(len(winners)),
        pctdistance=0.78,
    )
    ax.legend(
        wedges,
        winners.index,
        title="Winner",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )
    ax.set_title("World Cup Titles by Winner")
    ax.axis("equal")
    return _finalize(fig)


def plot_goals_histogram(matches: pd.DataFrame):
    if matches.empty:
        return _empty_figure("Distribution of Goals per Match")

    fig, ax = plt.subplots(figsize=(8, 5))
    max_goals = int(matches["Total Goals"].max())
    bins = range(0, max_goals + 2)
    sns.histplot(matches, x="Total Goals", bins=bins, color=PALETTE[0], edgecolor=FIGURE_BACKGROUND, ax=ax)
    ax.set_title("Distribution of Goals per Match")
    ax.set_xlabel("Total Goals")
    ax.set_ylabel("Number of Matches")
    return _finalize(fig)


def plot_goals_trend_line(cups: pd.DataFrame):
    if cups.empty:
        return _empty_figure("Goals Scored by Tournament Year")

    plot_data = cups.sort_values("Year")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        plot_data["Year"],
        plot_data["GoalsScored"],
        marker="o",
        linewidth=2.4,
        color=PALETTE[1],
        label="Goals scored",
    )
    ax.set_title("Goals Scored by Tournament Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Goals Scored")
    ax.legend()
    return _finalize(fig)


def plot_stage_goals_bar(matches: pd.DataFrame):
    if matches.empty:
        return _empty_figure("Top Stages by Goals")

    stage_goals = (
        matches.groupby("Stage", as_index=False)["Total Goals"]
        .sum()
        .sort_values("Total Goals", ascending=False)
        .head(12)
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(stage_goals, x="Total Goals", y="Stage", hue="Stage", palette=_colors(len(stage_goals)), legend=False, ax=ax)
    ax.set_title("Top Stages by Total Goals")
    ax.set_xlabel("Total Goals")
    ax.set_ylabel("Stage")
    return _finalize(fig)


def plot_attendance_scatter(matches: pd.DataFrame):
    plot_data = matches.dropna(subset=["Attendance", "Total Goals"])
    if plot_data.empty:
        return _empty_figure("Attendance vs Goals")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        plot_data,
        x="Attendance",
        y="Total Goals",
        hue="Result",
        size="Total Goals",
        sizes=(35, 180),
        palette={"Home Win": PALETTE[0], "Away Win": PALETTE[1], "Draw": PALETTE[2]},
        alpha=0.82,
        ax=ax,
    )
    ax.set_title("Attendance vs Goals")
    ax.set_xlabel("Attendance")
    ax.set_ylabel("Total Goals")
    ax.legend(title="Result", bbox_to_anchor=(1.02, 1), loc="upper left")
    return _finalize(fig)


def plot_attendance_box(matches: pd.DataFrame):
    plot_data = matches.dropna(subset=["Attendance", "Stage"]).copy()
    if plot_data.empty:
        return _empty_figure("Attendance Spread by Stage")

    top_stages = plot_data["Stage"].value_counts().head(10).index
    plot_data = plot_data[plot_data["Stage"].isin(top_stages)]
    fig, ax = plt.subplots(figsize=(9, 5))
    grouped_attendance = [
        plot_data.loc[plot_data["Stage"] == stage, "Attendance"].to_numpy()
        for stage in top_stages
    ]
    box = ax.boxplot(
        grouped_attendance,
        tick_labels=top_stages,
        orientation="horizontal",
        patch_artist=True,
    )
    for patch in box["boxes"]:
        patch.set_facecolor(PALETTE[3])
        patch.set_alpha(0.72)
    for median in box["medians"]:
        median.set_color(TEXT_COLOR)
        median.set_linewidth(1.6)
    ax.set_title("Attendance Spread by Stage")
    ax.set_xlabel("Attendance")
    ax.set_ylabel("Stage")
    return _finalize(fig)


def plot_correlation_heatmap(cups: pd.DataFrame, matches: pd.DataFrame):
    if cups.empty:
        return _empty_figure("Correlation Heatmap")

    match_year = (
        matches.groupby("Year")
        .agg(
            MatchGoals=("Total Goals", "sum"),
            MatchAttendance=("Attendance", "sum"),
            MatchCount=("MatchID", "count"),
        )
        .reset_index()
    )
    merged = cups.merge(match_year, on="Year", how="left")
    numeric_columns = [
        "GoalsScored",
        "QualifiedTeams",
        "MatchesPlayed",
        "Attendance",
        "Goals Per Match",
        "Attendance Per Match",
        "MatchGoals",
        "MatchAttendance",
        "MatchCount",
    ]
    numeric = merged[numeric_columns].dropna(axis=1, how="all")
    if len(numeric) < 2 or numeric.shape[1] < 2:
        return _empty_figure("Correlation Heatmap")

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        numeric.corr(),
        annot=True,
        fmt=".2f",
        cmap="vlag",
        center=0,
        linewidths=0.5,
        cbar_kws={"label": "Correlation"},
        ax=ax,
    )
    ax.set_title("Correlation Heatmap of Tournament Metrics")
    return _finalize(fig)


def plot_cumulative_area(cups: pd.DataFrame):
    if cups.empty:
        return _empty_figure("Cumulative Goals Over Time")

    plot_data = cups.sort_values("Year").copy()
    plot_data["Cumulative Goals"] = plot_data["GoalsScored"].cumsum()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(
        plot_data["Year"],
        plot_data["Cumulative Goals"],
        color=PALETTE[2],
        alpha=0.32,
        label="Cumulative goals",
    )
    ax.plot(plot_data["Year"], plot_data["Cumulative Goals"], color=PALETTE[2], linewidth=2.4)
    ax.set_title("Cumulative Goals Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Goals")
    ax.legend()
    return _finalize(fig)


def plot_stage_count(matches: pd.DataFrame):
    if matches.empty:
        return _empty_figure("Match Count by Stage")

    order = matches["Stage"].value_counts().head(12).index
    plot_data = matches[matches["Stage"].isin(order)]
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(plot_data, y="Stage", order=order, color=PALETTE[4], ax=ax)
    ax.set_title("Match Count by Stage")
    ax.set_xlabel("Number of Matches")
    ax.set_ylabel("Stage")
    return _finalize(fig)


def plot_goals_violin(matches: pd.DataFrame):
    if matches.empty:
        return _empty_figure("Goal Distribution by Result")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.violinplot(
        matches,
        x="Result",
        y="Total Goals",
        hue="Result",
        palette=_colors(matches["Result"].nunique()),
        legend=False,
        inner="quartile",
        cut=0,
        ax=ax,
    )
    ax.set_title("Goal Distribution by Match Result")
    ax.set_xlabel("Result")
    ax.set_ylabel("Total Goals")
    return _finalize(fig)


def plot_player_event_counts(players: pd.DataFrame):
    if players.empty or "Has Event" not in players.columns:
        return _empty_figure("Most Frequent Player Event Codes")

    event_rows = players[players["Has Event"]].copy()
    if event_rows.empty:
        return _empty_figure("Most Frequent Player Event Codes")

    event_counts = (
        event_rows["Event"]
        .value_counts()
        .head(15)
        .rename_axis("Event")
        .reset_index(name="Records")
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        event_counts,
        x="Records",
        y="Event",
        hue="Event",
        palette=_colors(len(event_counts)),
        legend=False,
        ax=ax,
    )
    ax.set_title("Most Frequent Player Event Codes")
    ax.set_xlabel("Records")
    ax.set_ylabel("Event")
    return _finalize(fig)


def _empty_figure(title: str, message: str = "No data available for the selected filters"):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=12, color=MUTED_TEXT)
    ax.set_title(title)
    ax.set_axis_off()
    return _finalize(fig)


def _colors(count: int) -> list[str]:
    if count <= len(PALETTE):
        return PALETTE[:count]
    repeats = (count // len(PALETTE)) + 1
    return (PALETTE * repeats)[:count]


def _finalize(fig):
    fig.patch.set_facecolor(FIGURE_BACKGROUND)
    for ax in fig.axes:
        ax.set_facecolor(AXIS_BACKGROUND)
        ax.title.set_fontweight("bold")
        ax.title.set_color(TEXT_COLOR)
        ax.xaxis.label.set_color(TEXT_COLOR)
        ax.yaxis.label.set_color(TEXT_COLOR)
        ax.tick_params(colors=MUTED_TEXT)
        for spine in ax.spines.values():
            spine.set_color(SPINE_COLOR)
        legend = ax.get_legend()
        if legend is not None:
            legend.get_frame().set_facecolor(AXIS_BACKGROUND)
            legend.get_frame().set_edgecolor(SPINE_COLOR)
            for text in legend.get_texts():
                text.set_color(TEXT_COLOR)
            title = legend.get_title()
            if title is not None:
                title.set_color(TEXT_COLOR)
    fig.tight_layout()
    return fig
