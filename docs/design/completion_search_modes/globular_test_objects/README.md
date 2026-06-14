# Globular Test Objects

Design folder for globular-category and globular-test-object
completion/search modes.

The motivating shapes are globular rather than simplicial or cubical. A
globular object is organized by iterated source and target data:

```text
0-cells
1-cells between 0-cells
2-cells between parallel 1-cells
3-cells between parallel 2-cells
...
```

This folder is a holding place for designs where the package should search for,
recognize, or complete globular diagrams rather than only simplex words,
horns, squares, or cubes.

## Initial Intuition

The combinatorial address of a globular cell is not just a tuple of vertices.
It has boundary data:

- a source lower cell;
- a target lower cell;
- parallelism or compatibility between those lower cells;
- possibly a pasting diagram built from lower globes.

For example:

- a `1`-globe is an arrow between two objects;
- a `2`-globe is a 2-cell between two parallel arrows;
- a `3`-globe is a 3-cell between two parallel 2-cells;
- higher globes repeat this source/target recursion.

## Relationship To Existing Modes

Globular modes should not be collapsed too early into one of the other shapes:

- simplicial small-object mode uses ordered simplex addresses;
- weak Kan and full Kan modes use horn/filler data;
- commutative square/cube mode uses products of directed intervals;
- globular mode uses iterated source/target cells and parallel boundary pairs.

There may be translations between these worlds, but the globular address should
remain visible if it is the mathematical object being searched or completed.

## Questions To Settle

Before implementation, this folder should clarify:

- what the base graph supplies as `0`- and `1`-cell data;
- whether higher globular cells are recognized from existing simplex/cubical
  records or formally added as completion cells;
- what "parallel" means for lower cells in the current package;
- whether globular test objects are represented directly or via a schema;
- how degeneracy/identity cells are represented in each dimension;
- how downstairs globular boundaries index upstairs fiber search;
- what artifacts should record: globes, boundaries, fillers, witnesses, or all
  of these.

## Tower And Fiber Principle

The expected speed-up principle is the same broad one used elsewhere:

```text
search only over upstairs globular data lying over valid downstairs globular
boundaries or cells
```

not:

```text
generate arbitrary upstairs pasting diagrams and filter afterward
```

The exact fiber key may be a lower-dimensional boundary pair rather than the
last edge of a simplex.

## Boundary

This folder is not yet an implementation plan. It is the design home for
globular-category and globular-test-object ideas so they remain distinct from:

- cofibrant small-object simplex search;
- weak Kan inner-horn completion;
- full Kan all-horn completion;
- commutative square/cube product-diagram completion.
