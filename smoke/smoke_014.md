# smoke_014 count argument

Command:

```text
uv run python smoke/smoke_014.py
```

Output:

```text
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     2 |     3 |     4 |     5 |     6
```

No error found under the current package semantics.

The graph has two parallel edges from `a` to `b`:

```text
a => b
```

The current first implementation counts one simplex per vertex address, not
one simplex per edge-witness choice. Parallel edge ids are preserved as
witnesses on the same simplex record, but they do not create duplicate
simplex addresses.

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

If the intended future semantics are "one simplex per multigraph witness
choice", this smoke would need to change. That track is currently deferred.
