\# Sales Data Analysis \& Insights Dashboard



\## Overview

An interactive sales analytics project built with Python. It processes sales records, stores cleaned data in SQLite, and visualizes business performance through a Streamlit dashboard.



\## Features

\- Data cleaning and validation using Pandas

\- ETL pipeline: Extract, Transform, and Load

\- SQLite database integration

\- SQL-based sales summaries

\- Revenue, order, and units-sold KPIs

\- Interactive filters for date, category, and region

\- Monthly revenue and category/region visualizations

\- Download filtered sales records as CSV



\## Technologies

Python, Pandas, SQLite, SQL, Streamlit, Plotly, Git, and GitHub.



\## Run Locally



1\. Clone or download this repository.

2\. Install the dependencies:



&#x20;  `python -m pip install -r requirements.txt`



3\. Run the ETL pipeline:



&#x20;  `python process\_sales.py`



4\. Launch the dashboard:



&#x20;  `python -m streamlit run app.py`



\## Project Structure



\- `data/sales.csv` — Sample input data

\- `output/cleaned\_sales.csv` — Cleaned sales data

\- `process\_sales.py` — ETL and SQL analytics

\- `app.py` — Interactive dashboard

\- `sales.db` — SQLite database

\- `requirements.txt` — Python dependencies



\## Learning Outcomes

Practiced data preprocessing, ETL development, relational database operations, SQL aggregation, interactive visualization, and dashboard development.



\## Future Improvements

\- Connect to a larger real-world dataset

\- Add automated scheduled data refresh

\- Add sales forecasting and more business metrics



