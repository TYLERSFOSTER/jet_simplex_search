# smoke_014 count argument

Command:

```text
uv run python smoke/smoke_014.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     2 |     3 |     4 |     5 |     6

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     2 |     1 |     0 |     0 |     0
     total H-lifts |     2 |     2 |     0 |     0 |     0
```

No error found under the current package semantics.

The graph has two parallel edges from `a` to `b`:

```text
a => b
```

The skeleton search counts one simplex per vertex address. Parallel H edges are
collapsed to one skeleton edge in `G`, so the skeleton simplex table is the same
as the one-edge graph.

Therefore the count is the same as the one-edge graph:

```text
2 + d
```

The `2` counts the two totally degenerate simplices, and `d` counts the
nonconstant degeneracies over the support `{a,b}`.

For dimensions `0..4`, this gives:

```text
2, 3, 4, 5, 6
```

The H-lift table is different. The one positive nondegenerate edge address
`(a,b)` has two distinct H-lifts, one for each parallel H edge. The degenerate
edge addresses `(a,a)` and `(b,b)` have no H-lifts because this input has no
loops. Higher-dimensional skeleton addresses all require at least one loop
face, so their H-lift counts are zero.
