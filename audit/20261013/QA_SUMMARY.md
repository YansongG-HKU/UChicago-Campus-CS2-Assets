# Public QA summary

## Verified in the completed offline review

1. Manual register: 136 unique source/family rows; 133 full LOD families and three context/Main-only rows. All rows have an actual final source hash. Zero recorded missing manual evidence or image-hash mismatches at final register validation.
2. Integration: 31 saved source files and 54 target named meshes. Target geometry signatures matched the reviewed repair candidates. Non-target meshes in shared source scenes retained geometry, UVs, corner normals, material slots and transforms. Final saved-source signatures were checked separately from intermediate merge hashes.
3. Final visual evidence: 36 repaired family occurrences were manually rechecked using the final source's original materials at 45°, 135°, 225° and 315°, for Main/LOD1/LOD2. For 84 unchanged-source occurrences, original same-SHA evidence applies. Another 16 unchanged families in modified shared sources rely on explicit non-target preservation evidence. Generated diagnostic images do not themselves establish manual visual approval.
4. FBX: 76 unique final files actually imported, plus one auxiliary source comparison. Geometry, polygon correspondence, source/imported vertex errors, winding, defined corner normals, UVs, material indices, transforms, file versions and relative dependencies are recorded in actual_fbx_import_checks.json. Normal comparisons use double-precision local face cross products transformed by the inverse-transpose world matrix; the strict defined-normal dot threshold remains greater than 0.99998.
5. Materials and textures: original object-referenced slots/graphs/image semantics retained; original texture byte payloads available. Blender save may omit unused duplicated datablocks: 10 material and 74 image datablocks are disclosed.
6. Packaging: 21 data ZIP envelopes plus the starter ZIP passed CRC and SHA checks. Reconstructed output matched 8,032 asset hashes; the 7,940 baseline manifest assets stayed intact. Guard tests rejected an existing output, nested output, wrong baseline, and corrupted part.

## Explicit exceptions and interpretation

- The Saieh original microsliver faces have preserved undefined corner-normal exceptions, listed individually with affected exports, objects, areas and counts. They are not silently treated as ordinary valid corner normals.
- Harper's tiny-face precision diagnostic distinguishes inaccurate normals recomputed from rounded world coordinates from the matching local-geometry comparison. No normal threshold was loosened.
- A “source file changed” is not proof that every family in that source changed. Shared-source evidence is linked at the named-mesh level.
- Whole-source hash equality, mesh signature equality and image generation are technical evidence, not substitutes for the manual observations recorded for their stated views.
- Reconstruction and byte checks do not establish in-engine behavior. CS2 editor/runtime, _Gls/_Wat material dispatch, LOD transitions, collision/navigation, performance and Paradox Mods tests remain unperformed.

## Public packaging verification

This documentation preparation independently rehashed the 101 final sources and 76 unique final FBX paths. It copied the 23 original PDFs unchanged only after inspecting their extracted page text, metadata and decoded PDF object dictionaries for private workspace references, credential-shaped strings and private delivery references. See public_packaging_checks.json for per-PDF results. No new Blender or engine execution is claimed.
