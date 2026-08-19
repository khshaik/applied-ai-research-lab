# Verified Delivery Capacity Communication Package

This package translates the VDCM research into platform-neutral communication material for technical, management, and research audiences.

## Contents

- [`END_TO_END_WORKFLOW.md`](END_TO_END_WORKFLOW.md): detailed guide to the ten-step operating workflow.
- [`LONG_FORM_NARRATIVE.md`](LONG_FORM_NARRATIVE.md): publication-ready long-form article.
- [`SHORT_FORM_SUMMARY.md`](SHORT_FORM_SUMMARY.md): concise announcement and discussion copy.
- [`EDITORIAL_AND_RELEASE_GUIDE.md`](EDITORIAL_AND_RELEASE_GUIDE.md): audience, claim, accessibility, and release controls.
- [`assets/06-end-to-end-verified-delivery-workflow.png`](assets/06-end-to-end-verified-delivery-workflow.png): high-resolution raster visual.
- [`assets/06-end-to-end-verified-delivery-workflow.svg`](assets/06-end-to-end-verified-delivery-workflow.svg): editable vector visual.
- [`scripts/build_workflow.py`](scripts/build_workflow.py): deterministic renderer.

## Rebuild

From the repository root:

```bash
python3 communications/verified-delivery-capacity/scripts/build_workflow.py
```

The renderer rewrites the PNG, SVG, and checksum manifest. It performs no network, Git, or external-system operation.

## Interpretation boundary

The workflow is a conceptual explanation of the proposed planning artifact. It is not an empirical result, a validated organizational process, a cognitive-load measure, or proof that VDCM outperforms Story Points. Analytical statements in the communication material remain bounded by the D17-confirmed claims and the manuscript.
