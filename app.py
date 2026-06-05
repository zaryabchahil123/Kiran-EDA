from __future__ import annotations

from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from charts import (
    plot_attendance_box,
    plot_attendance_scatter,
    plot_correlation_heatmap,
    plot_cumulative_area,
    plot_goals_histogram,
    plot_goals_trend_line,
    plot_goals_violin,
    plot_player_event_counts,
    plot_stage_count,
    plot_stage_goals_bar,
    plot_winner_pie,
)
from filters import (
    apply_dashboard_filters,
    compute_kpis,
    get_filter_options,
    load_world_cup_data,
)
from theme import dark_table_html, get_app_styles


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


st.set_page_config(
    page_title="FIFA World Cup Dashboard | Kiran",
    layout="wide",
)


@st.cache_data(show_spinner="Loading World Cup data...")
def load_data():
    return load_world_cup_data(DATA_DIR)


def main() -> None:
    inject_styles()

    data = load_data()
    options = get_filter_options(data)
    filter_state = render_sidebar(options)
    filtered = apply_dashboard_filters(data, **filter_state)
    kpis = compute_kpis(filtered)

    st.title("FIFA World Cup Data Visualization Dashboard")
    st.caption("Student: Kiran | Exploratory Data Analysis Project")
    st.write(
        "A professional interactive dashboard analyzing FIFA World Cup tournaments, "
        "matches, attendance, goals, teams, stages, and player event records."
    )

    render_kpis(kpis)

    if filtered.matches.empty:
        st.warning("No matches found for the selected filters.")

    overview_tab, match_tab, player_tab, data_tab = st.tabs(
        ["Tournament Overview", "Match Analysis", "Player Events", "Filtered Data"]
    )

    with overview_tab:
        left, right = st.columns(2)
        with left:
            show_chart(plot_winner_pie(filtered.cups))
        with right:
            show_chart(plot_goals_trend_line(filtered.cups))

        left, right = st.columns(2)
        with left:
            show_chart(plot_cumulative_area(filtered.cups))
        with right:
            show_chart(plot_correlation_heatmap(filtered.cups, filtered.matches))

    with match_tab:
        left, right = st.columns(2)
        with left:
            show_chart(plot_goals_histogram(filtered.matches))
        with right:
            show_chart(plot_stage_goals_bar(filtered.matches))

        left, right = st.columns(2)
        with left:
            show_chart(plot_attendance_scatter(filtered.matches))
        with right:
            show_chart(plot_attendance_box(filtered.matches))

        left, right = st.columns(2)
        with left:
            show_chart(plot_stage_count(filtered.matches))
        with right:
            show_chart(plot_goals_violin(filtered.matches))

    with player_tab:
        render_player_events(filtered.players)

    with data_tab:
        render_data_tables(filtered)


def render_sidebar(options: dict[str, object]) -> dict[str, object]:
    defaults = {
        "year_range": options["year_range"],
        "host_country": "All",
        "teams": [],
        "stages": [],
        "attendance_range": options["attendance_range"],
        "search_text": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    st.sidebar.title("Filters")
    st.sidebar.caption("Student: Kiran")

    if st.sidebar.button("Reset / Clear Filters", width="stretch"):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()

    min_year, max_year = options["year_range"]
    min_attendance, max_attendance = options["attendance_range"]

    year_range = st.sidebar.slider(
        "Date / Tournament Year Range",
        min_value=min_year,
        max_value=max_year,
        key="year_range",
    )
    host_country = st.sidebar.selectbox(
        "Host Country",
        ["All", *options["host_countries"]],
        key="host_country",
    )
    teams = st.sidebar.multiselect(
        "Team Multi-Select",
        options["teams"],
        key="teams",
    )
    stages = st.sidebar.multiselect(
        "Stage / Category Filter",
        options["stages"],
        key="stages",
    )
    attendance_range = st.sidebar.slider(
        "Numerical Attendance Range",
        min_value=min_attendance,
        max_value=max_attendance,
        key="attendance_range",
    )
    search_text = st.sidebar.text_input(
        "Search / Text Filter",
        key="search_text",
        placeholder="City, stadium, team, referee",
    )

    return {
        "year_range": year_range,
        "host_country": host_country,
        "teams": teams,
        "stages": stages,
        "attendance_range": attendance_range,
        "search_text": search_text,
    }


def render_kpis(kpis: dict[str, object]) -> None:
    total_matches, total_goals, average_goals, total_attendance, top_winner = st.columns(5)

    with total_matches:
        render_kpi_card("Total Matches", f"{kpis['total_matches']:,}")
    with total_goals:
        render_kpi_card("Total Goals", f"{kpis['total_goals']:,}")
    with average_goals:
        render_kpi_card("Avg Goals / Match", f"{kpis['average_goals']:.2f}")
    with total_attendance:
        render_kpi_card("Total Attendance", f"{kpis['total_attendance']:,}")
    with top_winner:
        render_kpi_card("Top Winner", str(kpis["top_winner"]))

    st.info(f"Highest scoring match in view: {kpis['highest_scoring_match']}")


def render_kpi_card(label: str, value: str) -> None:
    safe_label = escape(label)
    safe_value = escape(value)
    st.markdown(
        f"""
        <div class="kpi-card" role="group" aria-label="{safe_label}">
            <div class="kpi-label">{safe_label}</div>
            <div class="kpi-value">{safe_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_player_events(players) -> None:
    event_rows = players[players["Has Event"]].copy()

    left, right = st.columns([0.42, 0.58])
    with left:
        st.subheader("Player Event Summary")
        st.metric("Player Rows", f"{len(players):,}")
        st.metric("Rows With Events", f"{len(event_rows):,}")
        unique_players = event_rows["Player Name"].nunique() if not event_rows.empty else 0
        st.metric("Players With Events", f"{unique_players:,}")

    with right:
        st.subheader("Most Frequent Event Codes")
        show_chart(plot_player_event_counts(players))

    preview_columns = [
        "Year",
        "Stage",
        "Team Initials",
        "Player Name",
        "Position",
        "Event",
        "Coach Name",
    ]
    st.subheader("Filtered Player Event Records")
    st.markdown(
        dark_table_html(event_rows[preview_columns].head(300), max_height=460),
        unsafe_allow_html=True,
    )


def render_data_tables(filtered) -> None:
    match_columns = [
        "Year",
        "Date",
        "Stage",
        "City",
        "Stadium",
        "Home Team Name",
        "Home Team Goals",
        "Away Team Goals",
        "Away Team Name",
        "Attendance",
        "Result",
        "Total Goals",
    ]
    player_columns = [
        "Year",
        "Stage",
        "Team Initials",
        "Line-up",
        "Shirt Number",
        "Player Name",
        "Position",
        "Event",
    ]

    st.subheader("Filtered Match Records")
    st.markdown(
        dark_table_html(filtered.matches[match_columns], max_height=520),
        unsafe_allow_html=True,
    )
    st.download_button(
        "Download Filtered Matches CSV",
        data=filtered.matches.to_csv(index=False).encode("utf-8"),
        file_name="filtered_world_cup_matches.csv",
        mime="text/csv",
        width="stretch",
    )

    st.subheader("Filtered Player Records")
    st.markdown(
        dark_table_html(filtered.players[player_columns].head(500), max_height=520),
        unsafe_allow_html=True,
    )


def show_chart(figure) -> None:
    st.pyplot(figure, width="stretch")
    plt.close(figure)


def inject_styles() -> None:
    st.markdown(get_app_styles(), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
