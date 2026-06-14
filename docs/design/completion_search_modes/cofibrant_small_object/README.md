# Cofibrant Small-Object Mode

This folder is for design notes that change or refactor the already implemented
static tower small-object / computational cofibrant-replacement search mode.

Do not duplicate the existing design spine here unless the mode abstraction
requires a compatibility update.

Existing authoritative design spine:

- `docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md`
- `docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md`
- `docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md`
- `docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md`

Current intent:

- preserve the implemented static tower simplex search;
- expose it as one completion/search mode;
- change it only where the new protocol boundary requires it.
