import pandas as pd
import geopandas as gpd
import folium
import sys

try:
    print("1. Loading CSV master data...")
    # Load the architectural master data, ensuring PNU is read as string
    df_csv = pd.read_csv('송파구_필지별_건축마스터.csv', encoding='cp949', dtype={'PNU': str})
    print(f"   Loaded master CSV: {df_csv.shape}")

    print("\n2. Loading Shapefile (Loading only 'A0' column for speed and memory efficiency)...")
    # Load shapefile using only the PNU column ('A0') and geometries
    gdf_shp = gpd.read_file(
        'AL_D154_11_20260412/AL_D154_11_20260412.shp', 
        columns=['A0'],
        encoding='euc-kr'
    )
    print(f"   Loaded shapefile features: {gdf_shp.shape}")

    # Ensure both join keys are of the same type (string)
    gdf_shp['A0'] = gdf_shp['A0'].astype(str)
    df_csv['PNU'] = df_csv['PNU'].astype(str)

    print("\n3. Merging Shapefile with Master CSV on PNU...")
    # Merge on A0 (Shapefile) and PNU (CSV)
    gdf_merged = gdf_shp.merge(df_csv, left_on='A0', right_on='PNU', how='inner')
    print(f"   Merged matched features: {gdf_merged.shape}")

    if gdf_merged.empty:
        print("[ERROR] No matching features found between shapefile and CSV. Check PNU format!")
        sys.exit(1)

    print("\n4. Setting up Vworld map tiles...")
    # Use official Vworld WMTS URL with API key
    VWORLD_API_KEY = "791131E9-8829-31E7-97AD-78468E8E50F6"
    layer = "Base"
    vworld_url = f"https://api.vworld.kr/req/wmts/1.0.0/{VWORLD_API_KEY}/{layer}/{{z}}/{{y}}/{{x}}.png"

    # Create base map centered at the center of Songpa-gu with appropriate zoom level
    m = folium.Map(location=[37.503, 127.116], zoom_start=13, tiles=None)

    # Add Vworld tile layer as the background
    folium.TileLayer(
        tiles=vworld_url,
        attr="Vworld",
        name="Vworld Base Map",
        overlay=False,
        control=True
    ).add_to(m)

    print("\n5. Rendering land use visualization on interactive map...")
    # Use geopandas explore function
    m = gdf_merged.explore(
        m=m,
        column='주용도코드명',            # Color based on main building use
        cmap='Set3',                    # Pastel colormap
        tooltip=['PNU', '주용도코드명', '대지면적(㎡)', '용적률(%)'], # Hover details
        popup=True,
        legend=True,                    # Legend at bottom right
        style_kwds={'fillOpacity': 0.7, 'weight': 1, 'color': 'gray'} # Polygon styling
    )

    # Add layer control to toggle map layers
    folium.LayerControl().add_to(m)

    print("\n6. Saving final interactive map to '송파구_토지이용_시각화.html'...")
    output_filename = '송파구_토지이용_시각화.html'
    m.save(output_filename)
    print(f"[SUCCESS] Completed: '{output_filename}' file has been created successfully!")

except Exception as e:
    print(f"[ERROR] Error occurred: {e}", file=sys.stderr)
    sys.exit(1)
