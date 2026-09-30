# LIS-ACCESS MVP

## Run locally

1. Open Terminal in this folder.
2. Install dependencies:
   pip install -r requirements.txt
3. Run:
   streamlit run app.py

## Included datasets
- data/obstacles_lisbon_final.geojson
- data/essential_services_lisbon.geojson
- data/streetco_pois_normalized.geojson

## MVP capabilities
- Portuguese/English interface
- obstacle filters by parish, street and type
- points / clusters / heatmap
- essential services and StreetNav POI layers
- custom-radius proximity analysis
- multi-service selection
- polygon/rectangle drawing and area analysis
- intervention proposal per obstacle
- responsible entity assignment
- task locking simulation
- editable cost/time/complexity fields
- criterion-by-criterion prioritisation once data exists
- task status and monitoring summary

Note: proximity is straight-line distance in this MVP. Walking-network distance is not yet implemented.

## MVP v2 visual/navigation improvements
- New Home tab with Jobs to be Done cards
- Essential services have distinct pictograms and colours:
  - hospital red
  - school blue
  - station purple
- StreetNav POIs have category pictograms
- Obstacles use orange points, clearly separated from services and POIs
- Main and proximity maps can be hidden/minimised with a toggle
- Key-free OpenStreetMap is now the default basemap
- Alternative light and satellite basemaps are available from the map layer control
