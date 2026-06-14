# Commutative Squares And Cubes

Design folder for commutative square, commutative cube, and higher
product-of-directed-interval completion/search modes.

The motivating shape is cubical rather than purely simplicial:

```text
(Delta^1)^n
```

For `n = 2`, this gives a directed square. For `n = 3`, this gives a directed
cube. Higher `n` gives higher commutativity data over products of directed
1-simplices.

## Initial Intuition

The expected object is not just a larger simplex. It is a structured diagram
whose faces are lower-dimensional product diagrams:

- a square has four vertices, four directed interval edges, and a comparison of
  the two directed paths from the initial corner to the terminal corner;
- a cube has eight vertices, twelve directed interval edges, six square faces,
  and compatibility among those square faces;
- higher cubes repeat the same product-of-intervals pattern.

In a graph-only setting, "commutativity" needs an explicit package-level
meaning. It might mean:

- equality of composed path witnesses if a categorical composition surface is
  present;
- existence of compatible fillers across a chosen triangulation;
- equality of endpoint-preserving path classes;
- a directed fiber-product condition across independent edge directions;
- or a formal replacement/completion rule that adds missing comparison data.

This folder should settle that meaning before implementation.

## Relationship To Simplices

Products such as `Delta^1 x Delta^1` can be related to simplicial data by
triangulation, but the cubical address should not be erased too early.

For this package, the design question is whether a commutative square/cube mode
should:

- store genuine cubical records;
- lower cubical records to compatible simplex records;
- emit both cubical and simplicial views;
- or treat cubical records as a separate completion protocol sharing only the
  graph/tower/fiber substrate.

## Tower And Fiber Questions

The key quotient-tower question is analogous to the simplex modes:

- what is the downstairs cubical object;
- which upstairs corner, edge, face, or filler fibers are searched;
- when does an upstairs square/cube lie over a downstairs square/cube;
- how do degenerate interval directions behave;
- how do missing downstairs faces prevent upstairs search;
- and whether completion adds formal cells or only recognizes existing ones.

The speed-up principle should remain:

```text
search only inside fibers indexed by valid downstairs product diagrams
```

not:

```text
generate arbitrary upstairs cubes and filter afterward
```

## Boundary

This folder is not yet an implementation plan. It is a design home for the
cubical/commutativity mode so it does not get confused with:

- the existing cofibrant small-object simplex mode;
- weak Kan inner-horn completion;
- full Kan all-horn completion.
