import pandas as pd
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px

__version__='1.1'

excel_file = "vic/Analitika-stroski.xlsx"

@st.cache_data(ttl='1d')
def import_data():
    return pd.read_excel(excel_file, index_col=None, header = 0, na_values=['NA'], usecols=["YEAR","MONTH","COST","ELECTRICITY"])

df = import_data()

min_year = df['YEAR'].min()
max_year = df['YEAR'].max()

def get_unique_years(df):
    return list(df['YEAR'].unique())

def get_max_year(df):
    return df['YEAR'].max()


st.header(f'MONTHLY COSTS - VIČ ({min_year}-{max_year})')
st.write(f'Version: {__version__}')

with st.sidebar:
    years = get_unique_years(df)
    max_year = get_max_year(df)
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    selected_years = st.multiselect('Filter by Year:', years, default = (max_year))
    selected_months = st.multiselect('Filter by Month:', months, default = [])
    # if there is no filter on years then show all data for chosen month(s)
    if len(selected_years) == 0 and len(selected_months) > 0:
        selected_years = years
    # if there is no filter on months then show all data for chosen year(s)
    if len(selected_months) == 0 and len(selected_years) > 0:
        selected_months = months
    

df_filtered = df[df['YEAR'].isin(selected_years) & df['MONTH'].isin(selected_months)]

st.sidebar.dataframe(df_filtered,
                    column_config = {'YEAR': st.column_config.NumberColumn(format="%f")},
                    hide_index=True
)

# Some basic metric of the monthly cost
min_cost = 0
max_cost = 0
sum_cost = 0
avg_cost = 0

sum_cost = df_filtered['COST'].sum()
count    = df_filtered['COST'].count()

if sum_cost > 0 and count > 0:
    avg_cost = round(sum_cost / count)
    min_cost = round(df_filtered['COST'].min())
    max_cost = round(df_filtered['COST'].max())


# Print metrics
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric('Min. monthly Cost (€)', min_cost)
    with c2:
        st.metric('Max. monthly Cost (€)', max_cost)
    with c3:
        st.metric('Avg. monthly Cost (€)', avg_cost)

# Add some visualization - builtin Streamlit chart
aggregations = {
    "COST": "sum",
    "ELECTRICITY": "sum"
}
df_grouped = df_filtered.groupby(['YEAR']).agg(aggregations).reset_index() 
df_grouped = df_grouped.rename(columns={'YEAR':'Year','COST':'Total cost(€)','ELECTRICITY':'Electricity(€)'})

c1, c2 = st.columns(2)

with c1:
    st.dataframe(df_grouped,
                column_config = {'Year': st.column_config.NumberColumn(format="%f")},
                hide_index=True)
with c2:
    # we added -Year- columns as a year converted to a string 
    # to prevent wrong labels (eg. displawing 2022,0 instead of 2022)
    df_grouped['-Year-'] = df_grouped['Year'].astype(str)
    st.line_chart(df_grouped, x='-Year-', y='Total cost(€)')

# Plotly demo
df['YEARMONTH'] = df['YEAR'].astype(str) + '-' + df['MONTH'].astype(str)

fig = go.Figure()
fig.add_trace(
  go.Scatter(x=df['YEARMONTH'], y=df['COST'], mode='lines+markers', name='Total Cost')  
)
fig.add_trace(
  go.Scatter(x=df['YEARMONTH'], y=df['ELECTRICITY'], mode='lines+markers', name='Electricity bill')  
)
fig.update_layout(
    title="Monthly cost over the years",
    xaxis_title='Monthly bills',
    yaxis_title='Cost (€)'
)
st.plotly_chart(fig, use_container_width=True)
