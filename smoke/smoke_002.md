# smoke_002 count argument

Command:

```text
uv run python smoke/smoke_002.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |    16 |    31 |    46 |    61 |    76
   1 |     8 |    15 |    22 |    29 |    36

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |    16 |    15 |     0 |     0 |     0
     total H-lifts |    16 |    15 |     0 |     0 |     0
```

No error found.

Tier 0 is a directed path on 16 vertices with 15 nonidentity edges.

For a directed path with formal identities and no longer face edges, every
degree `m` simplex is either:

- a totally degenerate word at one vertex; or
- a degenerate word over one nonidentity edge, with exactly one transition from
  source to target.

Thus:

```text
dim m count = vertex_count + m * edge_count
```

For tier 0 this gives:

```text
16 + m * 15
```

so the displayed counts are:

```text
16, 31, 46, 61, 76
```

The collapse labels identify every other path edge, producing a tier 1 path on
8 vertices with 7 nonidentity edges. The same formula gives:

```text
8 + m * 7
```

so the displayed counts are:

```text
8, 15, 22, 29, 36
```

For tier-0 H-lifts, degree 0 vertices lift positively and the 15 nonidentity
edges lift positively. There are no original H loops, so every higher
degenerate path simplex contains a loop factor with zero original choices.
That gives:

```text
dim 0: 16
dim 1: 15
dim 2, 3, 4: 0
```
