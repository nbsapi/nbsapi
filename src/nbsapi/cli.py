import subprocess
import sys
from pathlib import Path

import click


def generate_tests(spec_path=None):
    """
    Generate API conformance verification tests using the test generator script.
    This is a wrapper around the test_generator.py script.
    """
    # Get the root directory of the project
    project_root = Path(__file__).parent.parent.parent

    # Path to the OpenAPI spec
    if spec_path is None:
        spec_path = project_root / "openapi.json"
    else:
        spec_path = Path(spec_path)

    # Check if the OpenAPI spec exists
    if not spec_path.exists():
        print(f"Error: OpenAPI spec not found at {spec_path}")
        print(
            "Please make sure the API server has been run to generate the OpenAPI spec."
        )
        print("You can run the server with: uv run python src/nbsapi/main.py")
        sys.exit(1)

    # Path to the test generator script
    generator_path = project_root / "test_generator" / "test_generator.py"

    # Run the test generator
    cmd = [sys.executable, str(generator_path), "--spec", str(spec_path)]
    result = subprocess.run(cmd, cwd=str(project_root), check=True)  # noqa: S603

    if result.returncode == 0:
        print("\nTest generation completed successfully!")
        print("Generated tests are located in the 'conformance/' directory.")
        print("\nTo complete the update:")
        print("1. Copy the generated Tavern YAML tests to the nbsapi_verify repo")
        print("   From: conformance/")
        print("   To:   src/nbsapi_verify/tests/")
        print("2. Cut a new release of nbsapi")
        print("3. Tag and publish a new release of nbs_verify to PyPI")
    else:
        print("\nTest generation failed.")
        sys.exit(result.returncode)


# Create CLI group that will integrate with uvicorn CLI
@click.group()
def cli():
    """Command line tools for nbsapi."""
    pass


@cli.command()
@click.argument("spec_path", type=click.Path(exists=True), required=False)
def conform(spec_path):
    """Generate conformance tests from OpenAPI spec.

    SPEC_PATH is an optional path to the OpenAPI spec file.
    If not provided, 'openapi.json' in the project root will be used.
    """
    generate_tests(spec_path)


if __name__ == "__main__":
    cli()
