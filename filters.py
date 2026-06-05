from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DATA_FILES = {
    "cups": "WorldCups.csv",
    "matches": "WorldCupMatches.csv",
    "players": "WorldCupPlayers.csv",
}


@dataclass(frozen=True)
class WorldCupData:
    cups: pd.DataFrame
    matches: pd.DataFrame
    players: pd.DataFrame


@dataclass(frozen=True)
class FilteredWorldCupData:
    cups: pd.DataFrame
    matches: pd.DataFrame
    players: pd.DataFrame


def load_world_cup_data(data_dir: str | Path = "data") -> WorldCupData:
    """Load and clean the exact FIFA World Cup CSV files required by the assignment."""
    data_path = Path(data_dir)
    cups = pd.read_csv(data_path / DATA_FILES["cups"])
    matches = pd.read_csv(data_path / DATA_FILES["matches"])
    players = pd.read_csv(data_path / DATA_FILES["players"])

    cups = _clean_cups(cups)
    matches = _clean_matches(matches)
    players = _clean_players(players, matches)

    return WorldCupData(cups=cups, matches=matches, players=players)


def get_filter_options(data: WorldCupData) -> dict[str, object]:
    teams = sorted(
        set(data.matches["Home Team Name"].dropna()).union(
            set(data.matches["Away Team Name"].dropna())
        )
    )
    attendance = data.matches["Attendance"].dropna()
    attendance_range = (
        int(attendance.min()) if not attendance.empty else 0,
        int(attendance.max()) if not attendance.empty else 0,
    )

    return {
        "year_range": (
            int(data.cups["Year"].min()),
            int(data.cups["Year"].max()),
        ),
        "host_countries": sorted(data.cups["Country"].dropna().unique().tolist()),
        "teams": teams,
        "stages": sorted(data.matches["Stage"].dropna().unique().tolist()),
        "attendance_range": attendance_range,
    }


def apply_dashboard_filters(
    data: WorldCupData,
    year_range: tuple[int, int] | None = None,
    host_country: str = "All",
    teams: Iterable[str] | None = None,
    stages: Iterable[str] | None = None,
    attendance_range: tuple[int, int] | None = None,
    search_text: str = "",
) -> FilteredWorldCupData:
    matches = data.matches.copy()
    cups = data.cups.copy()

    if year_range is not None:
        start_year, end_year = sorted((int(year_range[0]), int(year_range[1])))
        matches = matches[matches["Year"].between(start_year, end_year)]
        cups = cups[cups["Year"].between(start_year, end_year)]

    if host_country and host_country != "All":
        cups = cups[cups["Country"].str.casefold() == host_country.casefold()]
        matches = matches[matches["Year"].isin(cups["Year"])]

    selected_teams = [team for team in (teams or []) if team]
    if selected_teams:
        matches = matches[
            matches["Home Team Name"].isin(selected_teams)
            | matches["Away Team Name"].isin(selected_teams)
        ]

    selected_stages = [stage for stage in (stages or []) if stage]
    if selected_stages:
        matches = matches[matches["Stage"].isin(selected_stages)]

    if attendance_range is not None:
        min_attendance, max_attendance = sorted(
            (int(attendance_range[0]), int(attendance_range[1]))
        )
        attendance_values = data.matches["Attendance"].dropna()
        full_attendance_range = (
            int(attendance_values.min()) if not attendance_values.empty else 0,
            int(attendance_values.max()) if not attendance_values.empty else 0,
        )
        attendance_mask = matches["Attendance"].between(
            min_attendance,
            max_attendance,
            inclusive="both",
        )
        if (min_attendance, max_attendance) == full_attendance_range:
            attendance_mask = attendance_mask | matches["Attendance"].isna()
        matches = matches[attendance_mask]

    cleaned_search = search_text.strip().casefold()
    if cleaned_search:
        matches = matches[_search_mask(matches, cleaned_search)]

    active_years = set(matches["Year"].dropna().astype(int).tolist())
    active_match_ids = set(matches["MatchID"].dropna().astype(int).tolist())
    cups = cups[cups["Year"].isin(active_years)]
    players = data.players[data.players["MatchID"].isin(active_match_ids)].copy()

    return FilteredWorldCupData(
        cups=cups.reset_index(drop=True),
        matches=matches.reset_index(drop=True),
        players=players.reset_index(drop=True),
    )


def compute_kpis(filtered: FilteredWorldCupData) -> dict[str, object]:
    matches = filtered.matches
    cups = filtered.cups

    total_matches = int(len(matches))
    total_goals = int(matches["Total Goals"].sum()) if not matches.empty else 0
    average_goals = float(total_goals / total_matches) if total_matches else 0.0
    total_attendance = int(matches["Attendance"].sum(skipna=True)) if not matches.empty else 0

    if cups.empty:
        top_winner = "N/A"
    else:
        top_winner = cups["Winner"].value_counts().idxmax()

    if matches.empty:
        highest_scoring_match = "N/A"
    else:
        highest_row = matches.loc[matches["Total Goals"].idxmax()]
        highest_scoring_match = (
            f"{highest_row['Year']}: {highest_row['Home Team Name']} "
            f"{int(highest_row['Home Team Goals'])}-{int(highest_row['Away Team Goals'])} "
            f"{highest_row['Away Team Name']}"
        )

    return {
        "total_matches": total_matches,
        "total_goals": total_goals,
        "average_goals": average_goals,
        "total_attendance": total_attendance,
        "top_winner": top_winner,
        "highest_scoring_match": highest_scoring_match,
    }


def _clean_cups(cups: pd.DataFrame) -> pd.DataFrame:
    cleaned = cups.dropna(how="all").copy()
    _clean_object_columns(cleaned)

    numeric_columns = ["Year", "GoalsScored", "QualifiedTeams", "MatchesPlayed"]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").astype(int)

    cleaned["Attendance"] = (
        cleaned["Attendance"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype(int)
    )
    cleaned["Goals Per Match"] = cleaned["GoalsScored"] / cleaned["MatchesPlayed"]
    cleaned["Attendance Per Match"] = cleaned["Attendance"] / cleaned["MatchesPlayed"]
    cleaned["Decade"] = (cleaned["Year"] // 10) * 10

    return cleaned.sort_values("Year").reset_index(drop=True)


def _clean_matches(matches: pd.DataFrame) -> pd.DataFrame:
    cleaned = matches.dropna(how="all").copy()
    _clean_object_columns(cleaned)

    numeric_columns = [
        "Year",
        "Home Team Goals",
        "Away Team Goals",
        "Attendance",
        "Half-time Home Goals",
        "Half-time Away Goals",
        "RoundID",
        "MatchID",
    ]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["Year", "MatchID", "Home Team Name", "Away Team Name"])
    cleaned = cleaned.drop_duplicates(subset=["MatchID"], keep="first")

    integer_columns = [
        "Year",
        "Home Team Goals",
        "Away Team Goals",
        "Half-time Home Goals",
        "Half-time Away Goals",
        "RoundID",
        "MatchID",
    ]
    for column in integer_columns:
        cleaned[column] = cleaned[column].astype(int)

    cleaned["Datetime"] = cleaned["Datetime"].astype(str).str.strip()
    date_values = cleaned["Datetime"].str.replace(" - ", " ", regex=False)
    cleaned["Date"] = pd.to_datetime(
        date_values,
        format="%d %b %Y %H:%M",
        errors="coerce",
    )
    cleaned["Total Goals"] = cleaned["Home Team Goals"] + cleaned["Away Team Goals"]
    cleaned["Goal Difference"] = (
        cleaned["Home Team Goals"] - cleaned["Away Team Goals"]
    ).abs()
    cleaned["Result"] = np.select(
        [
            cleaned["Home Team Goals"] > cleaned["Away Team Goals"],
            cleaned["Away Team Goals"] > cleaned["Home Team Goals"],
        ],
        ["Home Win", "Away Win"],
        default="Draw",
    )
    cleaned["Winner Team"] = np.select(
        [
            cleaned["Home Team Goals"] > cleaned["Away Team Goals"],
            cleaned["Away Team Goals"] > cleaned["Home Team Goals"],
        ],
        [cleaned["Home Team Name"], cleaned["Away Team Name"]],
        default="Draw",
    )
    cleaned["Match Label"] = (
        cleaned["Year"].astype(str)
        + ": "
        + cleaned["Home Team Name"].astype(str)
        + " vs "
        + cleaned["Away Team Name"].astype(str)
    )
    cleaned["Decade"] = (cleaned["Year"] // 10) * 10

    return cleaned.sort_values(["Year", "Date", "MatchID"]).reset_index(drop=True)


def _clean_players(players: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    cleaned = players.dropna(how="all").copy()
    _clean_object_columns(cleaned)

    numeric_columns = ["RoundID", "MatchID", "Shirt Number"]
    for column in numeric_columns:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").fillna(0).astype(int)

    cleaned["Event"] = cleaned["Event"].fillna("").astype(str).str.strip()
    cleaned["Has Event"] = cleaned["Event"].ne("")

    match_lookup = matches[
        ["MatchID", "Year", "Stage", "Home Team Name", "Away Team Name"]
    ].drop_duplicates("MatchID")
    cleaned = cleaned.merge(match_lookup, on="MatchID", how="left")

    return cleaned.reset_index(drop=True)


def _search_mask(matches: pd.DataFrame, search_text: str) -> pd.Series:
    search_columns = [
        "Stage",
        "Stadium",
        "City",
        "Home Team Name",
        "Away Team Name",
        "Referee",
        "Assistant 1",
        "Assistant 2",
        "Match Label",
    ]
    mask = pd.Series(False, index=matches.index)
    for column in search_columns:
        values = matches[column].fillna("").astype(str).str.casefold()
        mask = mask | values.str.contains(search_text, regex=False)
    return mask


def _clean_object_columns(frame: pd.DataFrame) -> None:
    for column in frame.columns:
        if pd.api.types.is_object_dtype(frame[column]) or pd.api.types.is_string_dtype(frame[column]):
            frame[column] = frame[column].map(_clean_text_value)


def _clean_text_value(value: object) -> object:
    if pd.isna(value):
        return value

    text = str(value)
    text = text.replace('rn">', "")
    text = text.replace("\xa0", " ")
    text = " ".join(text.strip().split())

    replacements = {
        "C�te d'Ivoire": "Cote d'Ivoire",
        "IR Iran": "Iran",
        "Germany FR": "Germany FR",
    }
    return replacements.get(text, text)
