import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
import os

cfg = Config()

# Use app service principal authentication
def get_connection(http_path):
    server_hostname = cfg.host
    if server_hostname.startswith('https://'):
        server_hostname = server_hostname.replace('https://', '')
    elif server_hostname.startswith('http://'):
        server_hostname = server_hostname.replace('http://', '')
    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
        _use_arrow_native_complex_types=False,
    )

# Read data from a Unity Catalog table and return it as a pandas DataFrame
def read_table(table_name: str, conn) -> pd.DataFrame:
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall_arrow().to_pandas()


wc = WorkspaceClient()
http_path_input = wc.dbutils.secrets.get(scope='general', key='http_path_input')
table_name = wc.dbutils.secrets.get(scope='general', key='table_name')
print(f"HTTP Path: {http_path_input}")

st.subheader(f'{http_path_input}')
# Display the result in a Streamlit DataFrame
if http_path_input and table_name:
    conn = get_connection(http_path_input)
    df = read_table(table_name, conn)
    st.write("Columns:", df.columns.tolist())
    # st.write("Dtypes:", df.dtypes)
    
    total_dist = df['distance_miles'].sum() if 'distance_miles' in df.columns else 0
    total_cals = df['calories'].sum() if 'calories' in df.columns else 0


    metric_col1, metric_col2 = st.columns(2)

    metric_col1.metric(
        label="⏱️ Total Distance",
        border = True,
        value=total_dist
    )
    metric_col2.metric(
        label="🏃 Total Calories",
        border = True,
        value=total_cals
    )

    col1, col2 = st.columns([2, 2], gap ='medium')

    col1.subheader("Distance over months")
    monthly_distance = (
            df.groupby('month_start_date', as_index=False)['distance_miles']
            .sum()
            .sort_values('month_start_date', ascending=True)
    )
    
    col1.bar_chart(
        monthly_distance,
        x="month_start_date",
        y="distance_miles",
        x_label="Month",
        y_label="Total Distance",
    )

    col2.subheader("Distance over weeks")
    weekly_distance = (
    df.groupby('week_start_date', as_index=False)['distance_miles']
    .sum()
    .sort_values('week_start_date', ascending=True)
    )

    col2.bar_chart(
        weekly_distance,
        x="week_start_date",
        y="distance_miles",
        x_label="Week",
        y_label="Total Distance",
    )



    # Distance over months
    

    # Distance over weeks

    # Marathon prediction over weeks
    # Calories over weeks=
    # Calories over months
else:
    st.warning("Provide both the warehouse path and a table name to load data.")