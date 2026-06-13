# smoke_001 count argument

Command:

```text
uv run python smoke/smoke_001.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2
-----+-------+-------+------
   0 |     3 |     6 |    10
   1 |     2 |     3 |     4

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2
-------------------+-------+-------+------
positive addresses |     3 |     3 |     1
     total H-lifts |     3 |     3 |     1
```

No error found.

Tier 0 is the directed transitive triangle:

```text
a -> b -> d
a -> d
```

With formal identities, its degree counts are the monotone words into a
3-vertex chain:

```text
dim 0: 3
dim 1: 6
dim 2: 10
```

The contraction label collapses the edge `a -> b`, so tier 1 has two vertices
and one nonidentity edge to `d`. A one-edge graph has:

```text
dim m count = 2 + m
```

for the displayed dimensions, giving:

```text
2, 3, 4
```

For H-lifts at tier 0, there are no original H loops, so degenerate skeleton
faces do not lift through formal identities. The three vertices, three
nonidentity edges, and one nondegenerate triangle lift, giving:

```text
dim 0: 3
dim 1: 3
dim 2: 1
```
