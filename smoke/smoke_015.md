# smoke_015 count argument

Command:

```text
uv run python smoke/smoke_015.py
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
positive addresses |     2 |     2 |     2 |     2 |     2
     total H-lifts |     2 |     2 |     2 |     2 |     2
```

No error found under the current H-to-G skeletonization and H-lift policy.

The input graph contains:

```text
a -> a
a -> b
```

Skeleton search strips the input loop from the live skeleton edge set and then
adds one formal identity at every vertex. Therefore the skeleton graph behaves
like the single-edge graph:

```text
a -> b
```

with formal identities at `a` and `b`.

For dimension `d`, the count is:

```text
2 + d
```

For dimensions `0..4`, this gives:

```text
2, 3, 4, 5, 6
```

The H-lift table records the original loop separately. The degenerate faces at
`a` lift through the actual input loop `a -> a`, while degenerate faces at `b`
have no H-lift because there is no loop at `b`. This leaves two positive
addresses in every positive dimension: the totally `a`-degenerate address and
the address with repetitions at `a` followed by `b`.
