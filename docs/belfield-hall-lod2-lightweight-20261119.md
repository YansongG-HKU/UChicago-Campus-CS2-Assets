# Belfield Hall #98: corrected distant facade and lightweight import candidate

This work is limited to the separate Belfield double-tower asset, using original source SHA-256 08a1398f590dc78a6e4ca8c9746f0dc7fff3777c091cf02b061291e0c4621ca8. See [first-pass assessment](belfield-hall-first-pass-20261119.md) for open architectural and placement work.

- The near and mid facade use two floor-level rows. The old distant atlas drew three on both end and side tile regions. The candidate restores two rows, including the pointed lower windows, preserving three columns on ends and four on the sides. Those two atlas regions are referenced only by their 16 corresponding wall triangles. No geometry or UV changed. The new image pixels are restricted to the two tile strips of the distant BaseColor, MaskMap, and Emissive maps. Other maps, including the existing Normal and ControlMask, are byte-identical.
- Import tree drops from 5,116,940 to 3,434,637 bytes (32.88% reduction). PNGs go from 18 to 10; the main and LOD1 share the same five maps and LOD2 retains five. The reduction is for these offline import files, not VRAM or game package size.
- Blender source reopened from a clean copy; mesh topology/vertex positions and UV fingerprints agree. The three rewritten actual 7500 FBXs are read back at 26,132 / 7,188 / 320 triangles. The decoded FBX property trees differ only in image filenames; closed-off automatic image search round-trip verified the references against the actual named PNGs. Rewritten image paths are relative; project settings retain all five shared-map links. Candidate model hashes are recorded below.

| Candidate | SHA-256 |
|---|---|
| BelfieldHall.blend | 1ec59a0f7a4b9ce27c465eb5beea7331acb552b3e1854639a4af8e445aa33ff2 |
| BelfieldHall.fbx | f8b10f94189ab736e0194fe131f4c545fd8e4a39b20e69170c2a3463d849f25e |
| BelfieldHall_LOD1.fbx | 1e78680d019f8e7da3f13c813df1ec89d60002d0a7b04f8b6f0ec7d4d76609f0 |
| BelfieldHall_LOD2.fbx | 260deb732bc02c2d86001e9a6115211975b285ea6068beaf3989998059bc8cbc |

The distant atlas is still a stylized procedural representation. No rescaling, change to the building's shape, or incompatible reuse of either art hall or historic workshop was performed. Modern glass corridor fit, last-mile architectural dimensions, the far silhouette without finials, Autodesk profile acceptance, and actual Cities: Skylines II prefab validation remain open. Source, import candidate and same-camera Blender renders are separately delivered; this commit contains no model binaries.
