
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Sales Dashboard")

@st.cache_data
def load_data(path):
    df = pd.read_excel(path, parse_dates=['Date'])
    return df

df = load_data("cleaned_sales_data.xlsx")

st.title("Sales Dashboard — Service Popularity, Stylist Performance, Client Retention")

# KPIs
col1, col2, col3, col4 = st.columns(4)
total_revenue = df['Revenue'].sum()
total_appointments = len(df)
new_clients = df[df['CustomerType'].str.lower() == 'new']['CustomerType'].count()
returning_clients = df[df['CustomerType'].str.lower() == 'returning']['CustomerType'].count()
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Appointments", f"{total_appointments}")
col3.metric("New Clients", f"{new_clients}")
col4.metric("Returning Clients", f"{returning_clients}")

# Service popularity (by Service column if exists)
if 'Service' in df.columns:
    st.subheader("Service Popularity")
    service_counts = df['Service'].value_counts().reset_index()
    service_counts.columns = ['Service','Count']
    fig = px.bar(service_counts, x='Service', y='Count', title="Bookings per Service")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No 'Service' column found in the data. Service popularity charts will appear if you add a 'Service' column.")

# Revenue by Sales Rep (Stylist performance proxy)
st.subheader("Stylist / Sales Rep Performance")
revenue_by_rep = df.groupby('SalesRep', dropna=False)['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
fig2 = px.bar(revenue_by_rep, x='SalesRep', y='Revenue', title='Revenue by Sales Rep')
st.plotly_chart(fig2, use_container_width=True)

# Client retention over time
st.subheader("Client Retention Over Time (New vs Returning)")
df['Month'] = df['Date'].dt.to_period('M').astype(str)
monthly = df.groupby(['Month','CustomerType']).size().reset_index(name='Count')
fig3 = px.line(monthly, x='Month', y='Count', color='CustomerType', markers=True, title='Monthly New vs Returning Clients')
st.plotly_chart(fig3, use_container_width=True)

# Filters and data table
st.sidebar.header("Filters")
min_date = st.sidebar.date_input("Start date", df['Date'].min().date())
max_date = st.sidebar.date_input("End date", df['Date'].max().date())
channel = st.sidebar.multiselect("Channel", options=df['Channel'].unique(), default=list(df['Channel'].unique()))
rep = st.sidebar.multiselect("Sales Rep", options=df['SalesRep'].unique(), default=list(df['SalesRep'].unique()))

mask = (df['Date'].dt.date >= min_date) & (df['Date'].dt.date <= max_date) & df['Channel'].isin(channel) & df['SalesRep'].isin(rep)
st.dataframe(df.loc[mask].reset_index(drop=True))
