# Baker Dining #97B: courtyard and clerestory control line

Read-only deliverable. Previous [court and clerestory evidence](baker-dining-court-and-clerestory-evidence-20261119.md) and main-roof repair remain valid at their stated scope. No .blend, .fbx, materials, dorm, or terrain were modified.

## Trace and section check

On the [2025 county orthophoto](https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer), trace only the visible dark rim of the northwest court, following a straight west reach, curve, and diagonal. The trace is not a surveyed glass or mullion centerline. Do not extrapolate obscured endpoints. Registration: EPSG:26916 bounds E450170–450332/N4627060–4627222, 900 px square, centers at 0.18 m, same Baker local origin E450224.5011/N4627134.5186 and four-point RMS 0.53 m.

Cross-section probe on exact Blender roof candidate SHA256 `6635418b57e4c2c099e842b5012c6ccddd1c11632a295ea63892e428efb5daaf`: ten trace stations, five ray offsets each, three LODs (150 rays). At 1 m toward the court, all 30 first hits are still 5.800 m; at 1 m toward the green roof, all hits vary from 6.192 m to 8.462 m. These are geometry measurements, not site elevations. Independent hardscape point heights are 4.876, 4.668, and 5.006 m from [ISGS 2022 DSM](https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer) minus [DTM](https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer). They constrain local paving but do not identify the sill, roof flashing or a constant court plane.

| Trace station | Pixel (col,row) | 1m court / 1m roof (m), near |
|---:|---|---|
|1|119,483|5.800 / 6.192|
|2|171,483|5.800 / 6.641|
|3|224,482|5.800 / 7.101|
|4|262,478|5.800 / 7.250|
|5|279,466|5.800 / 7.608|
|6|301,444|5.800 / 7.805|
|7|325,419|5.800 / 8.018|
|8|351,392|5.800 / 8.248|
|9|375,366|5.800 / 8.462|
|10|389,350|5.800 / 8.327|

Geometry scope for the next edit: preserve the main roof away from the edge and the known ground-door vertices; distinguish the courtyard finish, metal head/sill, transparent clerestory and dorm seam. The [architect's documented section and interior](https://aiachicago.awardsplatform.com/gallery/dLgYJPQR/OeXxaYoe?search=c5b2f2c77c415f2f-100) establishes real glazing over a two-storey hall and visible support, not exact opening height or end closure. Do not infer traversable openings, demolish visible supports, or translate the entire old near-level surface by a single offset. Validate independently exported LODs, staging both buildings together when testing the seam.
