path_filter: src:
path_filter {
  root = src;
  include = [
    "fluidattacks_target_warehouse"
    "tests"
    "pyproject.toml"
    "mypy.ini"
    "ruff.toml"
    "uv.lock"
  ];
}
