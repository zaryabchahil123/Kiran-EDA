# FIFA World Cup Data Visualization Dashboard

Student Name: Kiran

This project is a Streamlit dashboard for the provided FIFA World Cup datasets in the `data/` folder. The dashboard uses Pandas and NumPy for cleaning/filtering, Matplotlib and Seaborn for charts, and Streamlit for the interactive frontend.

## Dataset Files

The required CSV filenames are kept unchanged:

- `data/WorldCups.csv`
- `data/WorldCupMatches.csv`
- `data/WorldCupPlayers.csv`

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Dashboard

```bash
streamlit run app.py
```

## Project Structure

```text
data/
  WorldCups.csv
  WorldCupMatches.csv
  WorldCupPlayers.csv
notebooks/
  analysis.ipynb
app.py
charts.py
filters.py
requirements.txt
README.md
tests/
  test_charts.py
  test_filters.py
```

## Dashboard Features

- KPI cards: total matches, total goals, average goals per match, total attendance, top winner.
- Filters: tournament year range, host country dropdown, team multi-select, stage/category multi-select, attendance range slider, text search, reset button.
- Required charts: pie chart, histogram, line chart, bar chart, scatter plot, box plot, heatmap, area chart, count plot, violin plot.
- Filtered match and player data tables with a CSV download for match records.

## Brief Insights

- Brazil has the most World Cup titles in the tournament summary data.
- The cleaned match table contains 836 unique matches after removing empty rows and duplicate match IDs.
- Goals, attendance, stages, and team participation vary strongly by tournament era because the number of qualified teams and matches increased over time.

## Run Tests

```bash
python -m unittest discover -v
```

