# smoke_003 count argument

Command:

```text
uv run python smoke/smoke_003.py
```

Output:

```text
Skeleton simplex counts
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     1 |     1 |     1 |     1 |     1

Tier-0 H-lift counts
            metric | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-------------------+-------+-------+-------+-------+------
positive addresses |     1 |     0 |     0 |     0 |     0
     total H-lifts |     1 |     0 |     0 |     0 |     0
```

No error found.

The graph has one vertex `a` and no nonidentity edges. After normalization,
there is one formal identity `a -> a`.

A dimension `d` simplex has `d + 1` vertices. The only possible word is:

```text
(a, a, ..., a)
```

So there is exactly one simplex in every dimension shown. This gives:

```text
1, 1, 1, 1, 1
```
