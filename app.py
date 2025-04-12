
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_excel("GGI Jan 2025.xlsx")
st.set_page_config(page_title="NextRise - Property Investment Dashboard", layout="wide")
st.title("🏡 NextRise: Property Investment Dashboard")

st.sidebar.header("🔍 Filter Areas")
area_options = df['Area'].unique()
selected_areas = st.sidebar.multiselect("Select Area(s)", area_options, default=area_options[:5])

growth_range = st.sidebar.slider("Average Annual Growth (10Y)",
                                  float(df['Av Annual Growth (10Y)'].min()),
                                  float(df['Av Annual Growth (10Y)'].max()),
                                  (0.03, 0.10))

pop_growth_range = st.sidebar.slider("Population Growth PA",
                                      float(df['Population Growth PA'].min()),
                                      float(df['Population Growth PA'].max()),
                                      (0.01, 0.07))

gap_pct_range = st.sidebar.slider("Growth Gap (%)",
                                   float(df['Growth gap (%)'].min()),
                                   float(df['Growth gap (%)'].max()),
                                   (-0.5, -0.1))

top_n = st.sidebar.number_input("Show Top N Areas by Rank", min_value=1, max_value=50, value=10)

filtered_df = df[
    (df['Area'].isin(selected_areas)) &
    (df['Av Annual Growth (10Y)'].between(*growth_range)) &
    (df['Population Growth PA'].between(*pop_growth_range)) &
    (df['Growth gap (%)'].between(*gap_pct_range))
]
filtered_df = filtered_df.sort_values("Rank").head(top_n)

st.subheader("📊 Filtered Suburb Data")
st.dataframe(filtered_df, use_container_width=True)

st.subheader("📉 Growth Gap by Area")
fig = px.bar(filtered_df, x='Area', y='Growth gap ($)', color='Av Annual Growth (10Y)',
             labels={'Growth gap ($)': 'Growth Gap ($)'})
st.plotly_chart(fig, use_container_width=True)

st.subheader("🕸️ Radar Chart of Key Metrics")
radar_metrics = ['Av Annual Growth (10Y)', 'Population Growth PA', '6Y Growth Rate from 2014', 'CMGR 2014 to 2020']
radar_fig = go.Figure()
for _, row in filtered_df.iterrows():
    radar_fig.add_trace(go.Scatterpolar(
        r=[row[metric] for metric in radar_metrics],
        theta=radar_metrics,
        fill='toself',
        name=row['Area']
    ))
radar_fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
st.plotly_chart(radar_fig, use_container_width=True)

st.subheader("🧠 AI Investment Summary")
for _, row in filtered_df.iterrows():
    summary = f"**{row['Area']}** has shown promising trends with an average annual growth of {row['Av Annual Growth (10Y)']:.2%} and population growth of {row['Population Growth PA']:.2%}. The growth gap of ${row['Growth gap ($)']:.0f} suggests underperformance relative to projections."
    st.markdown(summary)

if 'Latitude' in df.columns and 'Longitude' in df.columns:
    st.subheader("🗺️ Geo Map of Selected Areas")
    map_fig = px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', hover_name='Area',
                                color='Av Annual Growth (10Y)', size='Growth gap ($)',
                                zoom=4, height=500)
    map_fig.update_layout(mapbox_style="carto-positron")
    st.plotly_chart(map_fig, use_container_width=True)

st.download_button("📥 Download Filtered Data", data=filtered_df.to_csv(index=False), file_name="filtered_ggi_data.csv")
