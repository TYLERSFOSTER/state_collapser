# state_collapser mathematical model rewrite - first serious draft

This bundle contains a first serious LaTeX rewrite proposal for the `state_collapser` mathematical-model document.

## Files

- `state_collapser_mathematical_model_rewrite_first_draft.tex` - the rewritten LaTeX document.
- `state_collapser_mathematical_model_rewrite_first_draft.bib` - bibliography file.
- `assets/images/mathematical_model/*.png` - figure images extracted from the attached current PDF and named to match the repository figure filenames.
- `diagrams/main_light.xml` - the uploaded draw.io XML source for the larger diagram.
- `compile.sh` - local build script.

## Build

From inside this directory:

```bash
./compile.sh
```

The TeX file first looks for figures in `assets/images/mathematical_model/`, then falls back to `../../assets/images/mathematical_model/`. This means it should compile from this standalone bundle and can also be dropped into `docs/design/` inside the repository.

## Scope note

This draft is theorem-forward. It recasts the current document around reward-labelled path space, finite-horizon path-volume `P-Vol`, quotient-tower construction, liftability, reward descent, and a scoped logarithmic/multilevel address theorem. It intentionally avoids claiming an unconditional training-time speedup; the speedup is stated under explicit coverage, reward-compatibility, liftability, and balanced-addressability assumptions.
