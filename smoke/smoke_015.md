# smoke_015 count argument

Command:

```text
uv run python smoke/smoke_015.py
```

Output:

```text
tier | dim 0 | dim 1 | dim 2 | dim 3 | dim 4
-----+-------+-------+-------+-------+------
   0 |     2 |     3 |     4 |     5 |     6
```

No error found under the current normalization policy.

The input graph contains:

```text
a -> a
a -> b
```

First-scope normalization strips input loops and then adds exactly one formal
identity at every vertex. Therefore the input loop `a -> a` does not create an
extra simplex witness or a second loop. The normalized graph behaves like the
single-edge graph:

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

Meaningful non-identity input-loop semantics are intentionally deferred.
