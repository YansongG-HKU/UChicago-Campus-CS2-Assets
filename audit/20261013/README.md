# UChicago campus LOD: final strict offline audit

Release date: 2026-10-13. This is the public, portable extract of the completed strict source-asset review. It is an offline source/FBX quality record, not a Cities: Skylines II or Paradox Mods certification.

## Result and scope

- 136 separately identified family occurrences across 101 Blender sources: 133 complete Main/LOD1/LOD2 families, two Main-only groups, and one context scene. These are not 136 unique buildings.
- 23 building names were repaired in 36 family occurrences, affecting 31 source files and 54 named meshes.
- All 36 repaired occurrences had final-source, original-material, four-corner contact images manually rechecked. The other 100 occurrences reuse documented original manual evidence: 84 have identical whole-source SHA-256; 16 are unchanged families in modified shared sources, linked by non-target mesh/UV/normal/material/transform preservation checks. We do not claim that all 136 were freshly rerendered and manually rereviewed.
- Current dispositions: 36 repaired and manually reviewed with limits; 14 no repair needed with a documented boundary; 83 body-intact reviews with declared simplifications; three Main-only/context groups. No recorded original finding remains without a current disposition. This does not close unperformed engine checks.
- 76 unique final FBX exports were actually reimported in Blender during the completed verification, plus one auxiliary source comparison. There are 58 replacements of original export paths/versions and 18 additional validation files. Single-object validation exports are not full assembly exports.
- Strict reconstruction restored and SHA-256 checked all 8,032 final asset files. All 7,940 baseline manifest assets remained unchanged. The strict delta records 89 modified and 92 added files.

## Read the evidence

- [136-group audit CSV](review_register_136.csv): concise current conclusions, source paths, original/final hashes, limits and atlas links. Chinese observations are retained without inventing translations.
- [136-group audit JSON](review_register_136.json): original review evidence and final review records are separate; candidate hashes are explicitly non-final.
- [Disposition history](disposition_ledger_136.json): original findings, current outcome, and retained boundaries. Old provisional findings describe history, not the current result.
- [101 final-source hashes](final_source_sha256_manifest.json): final source identities were independently rehashed while preparing this public extract. “Original reviewed source” is the source used in the strict review, which is not necessarily the original public r1 release.
- [Public QA summary](QA_SUMMARY.md) and [verification data](verification/): completed merge, save, FBX reimport, material-preservation and reconstruction records. Public packaging rechecked bytes; it did not rerun Blender imports or visual reviews.
- [View the 23 PDFs](../../atlas/20261013/README.md): 20 visual atlas volumes covering R001-R136, complete written review notes, a Harper courtyard appendix and a directory/review brief.
- [Retained notices](licenses/README.md): exact 16 OSM-attributed technical groups and the unchanged DejaVu notice.

Paths beginning with assets/ resolve from the reconstructed asset release root. Other raw image/report paths are relative provenance labels from the review evidence set; not all raw evidence is duplicated in this compact public bundle. Public PDFs provide the contact sheets. SHA values in evidence_provenance.json identify the original inputs; FILES_SHA256.json identifies these public extracts.

## Important boundaries

Acceptance focused on recognizable building bodies, silhouette and major appendages, without broken/missing major faces in reviewed views. Small mullions, moldings, tiny steps and decorative details may be simplified. Author-defined shared-wall interfaces and ground-contact bottom openings remain where documented; no survey-grade watertightness claim is made.

Original material conventions were preserved, including glass objects with no Blender material slot and original opaque LOD atlases. These may produce visible color/appearance differences. They were not recolored to conceal missing geometry. Original active material semantics and all original texture payloads remain available; saving removed 10 unused duplicate material datablocks and 74 unused image datablocks.

Preexisting Saieh micrometre-scale thin triangles retain explicitly reported undefined corner-normal exceptions. “PASS” in individual numeric checks is bounded by the check's scope, not an assertion that every normal or all game behavior is perfect.

No CS2 editor/game runtime, automatic _Gls/_Wat shader dispatch, in-game LOD switching, collision/navigation, memory/performance or Paradox Mods publication/acceptance test was performed for this release.
