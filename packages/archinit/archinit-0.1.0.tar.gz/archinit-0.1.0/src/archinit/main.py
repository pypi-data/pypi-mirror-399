import re
from pathlib import Path
from typer import Typer, Option, Argument, secho, colors, Exit

app = Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def create_project_structure(project_name: str) -> None:
    modules = ("api", "core", "domain", "infrastructure", "services", "schemas")

    src_dir = Path("src")
    project_dir = src_dir / project_name

    for module in modules:
        module_path = project_dir / module
        module_path.mkdir(parents=True, exist_ok=True)
        (module_path / "__init__.py").touch(exist_ok=True)

    for folder in [src_dir, project_dir]:
        (folder / "__init__.py").touch(exist_ok=True)


def create_tests_structure() -> None:
    tests_modules = ("unit", "integration")

    src_dir = Path("src")
    project_dir = src_dir / "tests"

    for module in tests_modules:
        module_path = project_dir / module
        module_path.mkdir(parents=True, exist_ok=True)
        (module_path / "__init__.py").touch(exist_ok=True)


def check_project_name(project_name: str) -> None:
    project_name_re = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

    if not project_name_re.match(project_name):
        secho(
            "❗️Project name must contain only Latin letters, digits, and underscores",
            fg=colors.BRIGHT_RED,
            err=True,
        )
        raise Exit(code=1)


@app.command()
def arch_init(
    project_name: str = Argument(help="Project name to create"),
    tests: bool = Option(
        False,
        "--tests",
        "-t",
        help="Create test folder along with src.",
    ),
) -> None:
    check_project_name(project_name)

    create_project_structure(project_name=project_name)

    if tests:
        create_tests_structure()

    secho("Project ", fg=colors.BRIGHT_CYAN, bold=True, nl=False)
    secho(project_name, fg=colors.BRIGHT_MAGENTA, bold=True, italic=True, nl=False)
    secho(" created 😎", fg=colors.BRIGHT_CYAN, bold=True)


if __name__ == "__main__":
    app()
