# Completion Search Modes

Design area for separating `jet_simplex_search` into shared graph/tower/fiber
machinery plus mode-specific completion or search protocols.

The current implemented mode is the static tower small-object / computational
cofibrant-replacement simplex search. Future modes include weak Kan inner-horn
completion and full Kan all-horn completion.

## Subfolders

- `cofibrant_small_object/`: notes for the existing small-object mode, only
  when that mode needs refactor or compatibility changes.
- `weak_kan_inner_horn/`: design notes for weak Kan / inner-horn completion.
- `kan_all_horn/`: design notes for full Kan / all-horn completion.
- `commutative_squares_cubes/`: design notes for commutative squares, cubes,
  and higher cubical/product-of-intervals completion objects.
- `globular_test_objects/`: design notes for globular categories, globes, and
  globular test objects.

## Boundary

Shared infrastructure should stay in the main package design unless a mode
requires a specific change:

- H-to-G skeletonization;
- formal identities and degenerate records;
- static `state_collapser` tower adaptation;
- fiber indexes;
- diagnostics and artifacts;
- release-facing public API constraints.
