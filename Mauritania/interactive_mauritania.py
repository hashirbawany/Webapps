import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Load ADM3 shapefile
shapefile_path = "datafiles/mrt_admbnda_adm3_ansade_20240327.shp"
gdf = gpd.read_file(shapefile_path)
gdf = gdf[~((gdf['ADM3_EN'] == 'Beneamane') & (gdf['ADM2_EN'] == 'Aïoun'))]



# Clean up
gdf["adm3_clean"] = gdf["ADM3_EN"].str.strip().str.lower()
gdf["adm2_clean"] = gdf["ADM2_EN"].str.strip().str.lower()

# Sidebar: select multiple departments
departments = sorted(gdf["ADM2_EN"].unique())
selected_depts = st.multiselect("Select departments (ADM2):", departments, default=["Djiguenni", "Bassiknou"])

# Filter communes from selected departments
communes_in_selected = gdf[gdf["ADM2_EN"].isin(selected_depts)]["ADM3_EN"].sort_values().unique()
selected_communes = st.multiselect("Select communes to highlight:", communes_in_selected, default=list(communes_in_selected))

# Base map
m = folium.Map(location=[20.0, -10.0], zoom_start=6)

# All ADM3 outlines (gray)
folium.GeoJson(gdf.geometry, name="All Communes", style_function=lambda x: {
    'fillOpacity': 0.0,
    'color': 'gray',
    'weight': 0.5
}).add_to(m)

# Selected departments (ADM2) dissolved + highlighted
for dept_name in selected_depts:
    # Filter communes from this department
    dept_communes = gdf[gdf["ADM2_EN"] == dept_name]

    # Separate selected vs non-selected communes
    selected_in_dept = dept_communes[dept_communes["ADM3_EN"].isin(selected_communes)]
    non_selected_in_dept = dept_communes[~dept_communes["ADM3_EN"].isin(selected_communes)]

    # Plot non-selected communes in department (Color 1)
    folium.GeoJson(non_selected_in_dept.geometry, style_function=lambda x: {
        'fillColor': '#ccebc5',  # light green
        'color': 'green',
        'weight': 1,
        'fillOpacity': 0.5
    }).add_to(m)

    # Plot selected communes in department (Color 2)
    folium.GeoJson(selected_in_dept.geometry, style_function=lambda x: {
        'fillColor': 'orange',
        'color': 'black',
        'weight': 1.5,
        'fillOpacity': 0.7
    }).add_to(m)

    # Draw full ADM2 boundary outline
    dept_outline = dept_communes.dissolve(by="ADM2_EN")
    folium.GeoJson(dept_outline.geometry, style_function=lambda x: {
        'fillOpacity': 0,
        'color': 'darkgreen',
        'weight': 2
    }).add_to(m)

    # Add label for department
    centroid = dept_outline.geometry.centroid.iloc[0]
    folium.Marker(
        location=[centroid.y, centroid.x],
        icon=folium.DivIcon(html=f"""<div style="font-size:11pt; color:darkgreen;">{dept_name}</div>""")
    ).add_to(m)


# Plot selected communes
if selected_communes:
    highlight_gdf = gdf[gdf["ADM3_EN"].isin(selected_communes)]
    folium.GeoJson(highlight_gdf.geometry, name="Selected Communes", style_function=lambda x: {
        'fillColor': 'orange',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.6
    }).add_to(m)

    # Commune labels
    for _, row in highlight_gdf.iterrows():
        centroid = row.geometry.centroid
        folium.Marker(
            location=[centroid.y, centroid.x],
            popup=row["ADM3_EN"],
            icon=folium.DivIcon(html=f"""<div style="font-size:10pt; color:darkred;">{row["ADM3_EN"]}</div>""")
        ).add_to(m)

# Show map
st.title("Interactive Commune & Department Map – Mauritania")
st_data = st_folium(m, width=800, height=600)



#################################
