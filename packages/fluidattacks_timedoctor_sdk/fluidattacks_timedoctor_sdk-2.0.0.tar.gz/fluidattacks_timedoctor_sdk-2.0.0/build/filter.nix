path_filter: src:
path_filter {
  root = src;
  include = [
    "fluidattacks_timedoctor_sdk"
    "tests"
    "pyproject.toml"
    "mypy.ini"
    "ruff.toml"
    "uv.lock"
  ];
}
