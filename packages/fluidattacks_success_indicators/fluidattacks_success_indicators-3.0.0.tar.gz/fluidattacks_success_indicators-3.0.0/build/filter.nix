path_filter: src:
path_filter {
  root = src;
  include = [
    "fluidattacks_success_indicators"
    "tests"
    "pyproject.toml"
    "ruff.toml"
    "mypy.ini"
    "uv.lock"
  ];
}
