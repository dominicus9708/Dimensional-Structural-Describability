Strong_interaction benchmark raw layer README
Generated UTC: 2026-06-02T17:37:50+00:00
Script version: 001

This raw layer prepares references and small source tables for a 10,000+ event
strong-interaction benchmark pipeline.

Written directories:
- D:\Paper\Dimensional_Structural_Describability\Strong_interaction\data\raw\references
- D:\Paper\Dimensional_Structural_Describability\Strong_interaction\data\raw\source_tables

Important interpretation rules:
1. PDG and NIST are reference support tables, not event-level benchmark data.
2. arXiv pages are provenance references, not final numerical input.
3. HEPData search JSON files are discovery outputs; selected tables must later be
   cleaned into data/derived/cleaned_tables and then fixed under data/derived/input.
4. Do not place multi-GB event files in GitHub.
5. Do not write directly from this raw script into derived/input.
6. The theory-layer name should be confirmed before creating src/results theory-layer folders.

Recommended next stage:
- Inspect HEPData search outputs.
- Select OPAL/JADE/L3 binned event-shape tables.
- Confirm DELPHI open-data event-file source and file size.
- Create a separate cleaner script under data/derived/script or src/skeleton only after final source selection.
