import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium


# Load ADM3 shapefile
def launch_commune_map_app(
    shapefile_path: str,
    adm3_col: str,
    adm2_col: str,
    default_depts: list = None,
    map_center: tuple = (20.0, -10.0),
    map_zoom: int = 6
):
    # Load shapefile
    @st.cache_resource
    def load_shapefile(path):
        return gpd.read_file(path)

    gdf = load_shapefile(shapefile_path)

    gdf["geometry"] = gdf["geometry"].simplify(0.01, preserve_topology=True)
    
    # Clean column names
    gdf["adm3_clean"] = gdf[adm3_col].astype(str).str.strip().str.lower()
    gdf["adm2_clean"] = gdf[adm2_col].astype(str).str.strip().str.lower()
    
    # Sidebar: department selector
    departments = sorted(gdf[adm2_col].unique())
    default_depts = default_depts if default_depts else departments[:2]
    selected_depts = st.sidebar.multiselect("Select departments (ADM2):", departments, default=default_depts)
    
    # Sidebar: commune selector
    communes_in_selected = gdf[gdf[adm2_col].isin(selected_depts)][adm3_col].sort_values().unique()
    selected_communes = st.sidebar.multiselect("Select communes to highlight:", communes_in_selected, default=list(communes_in_selected))
    
    # Create base map
    m = folium.Map(location=map_center, zoom_start=map_zoom)

    # All outlines
    folium.GeoJson(gdf.geometry, name="All Communes", style_function=lambda x: {
        'fillOpacity': 0.0,
        'color': 'gray',
        'weight': 0.5
    }).add_to(m)

    for dept_name in selected_depts:
        dept_communes = gdf[gdf[adm2_col] == dept_name]
        selected_in_dept = dept_communes[dept_communes[adm3_col].isin(selected_communes)]
        non_selected_in_dept = dept_communes[~dept_communes[adm3_col].isin(selected_communes)]

        # Plot non-selected
        folium.GeoJson(non_selected_in_dept.geometry, style_function=lambda x: {
            'fillColor': '#ccebc5',
            'color': 'green',
            'weight': 1,
            'fillOpacity': 0.5
        }).add_to(m)

        # Plot selected
        folium.GeoJson(selected_in_dept.geometry, style_function=lambda x: {
            'fillColor': 'orange',
            'color': 'black',
            'weight': 1.5,
            'fillOpacity': 0.7
        }).add_to(m)

        # Outline of department
        dept_outline = dept_communes.dissolve(by=adm2_col)
        folium.GeoJson(dept_outline.geometry, style_function=lambda x: {
            'fillOpacity': 0,
            'color': 'darkgreen',
            'weight': 2
        }).add_to(m)

        # Label
        projected = dept_outline.to_crs(epsg=32630)  # Example: UTM zone 30N (adjust based on region)
        centroid = projected.geometry.centroid.iloc[0]= dept_outline.geometry.centroid.iloc[0]
        folium.Marker(
            location=[centroid.y, centroid.x],
            icon=folium.DivIcon(html=f"""<div style="font-size:11pt; color:darkgreen;">{dept_name}</div>""")
        ).add_to(m)

    # Highlight selected communes
    if selected_communes:
        highlight_gdf = gdf[gdf[adm3_col].isin(selected_communes)]
        folium.GeoJson(highlight_gdf.geometry, name="Selected Communes", style_function=lambda x: {
            'fillColor': 'orange',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.6
        }).add_to(m)

        for _, row in highlight_gdf.iterrows():
            centroid = row.geometry.centroid
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=row[adm3_col],
                icon=folium.DivIcon(html=f"""<div style="font-size:10pt; color:darkred;">{row[adm3_col]}</div>""")
            ).add_to(m)

    st.title("Interactive Commune & Department Map")
    st_folium(m, width=800, height=600)


launch_commune_map_app(
    shapefile_path=Senegal/datafiles/sen_admbnda_adm3_anat_20240520.shp",
    adm3_col="ADM3_FR",
    adm2_col="ADM2_FR",
    map_center=(16.0, -9.5),
    map_zoom=6
)    
