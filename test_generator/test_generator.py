import json
from enum import Enum
from pathlib import Path
from typing import Any

import click
import yaml


class TestType(str, Enum):
    ALL = "all"
    AUTH = "auth"
    PUBLIC = "public"


class NoAliasDumper(yaml.SafeDumper):
    """Custom YAML dumper that prevents creation of aliases for duplicate values."""

    def ignore_aliases(self, data):
        return True


def save_yaml(data: dict, file_path: Path) -> None:
    """Save data to YAML file without aliases."""
    with open(file_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, Dumper=NoAliasDumper)


def generate_example_from_schema(schema: dict, spec: dict) -> dict:
    """Generate example data from schema."""
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")[1:]  # Skip '#'
        resolved = spec
        for part in ref_path:
            resolved = resolved[part]
        schema = resolved

    if "example" in schema:
        return schema["example"]
    elif schema.get("examples"):
        return schema["examples"][0]

    # If no explicit type but has properties, treat as object
    if "properties" in schema:
        result = {}
        for prop_name, prop in schema["properties"].items():
            if prop_name in schema.get("required", []):
                if "example" in prop:
                    result[prop_name] = prop["example"]
                elif prop.get("examples"):
                    result[prop_name] = prop["examples"][0]
                else:
                    result[prop_name] = generate_default_value(prop)
        return result

    # If type is specified
    if "type" in schema:
        if schema["type"] == "object":
            result = {}
            if "properties" in schema:
                for prop_name, prop in schema["properties"].items():
                    if prop_name in schema.get("required", []):
                        if "example" in prop:
                            result[prop_name] = prop["example"]
                        else:
                            result[prop_name] = generate_default_value(prop)
            return result
        return generate_default_value(schema)

    # Fallback for unknown schemas
    return {}


def generate_default_value(prop: dict) -> Any:
    """Generate default value based on property type."""
    type_map = {
        "string": "test_string",
        "integer": 1,
        "number": 1.0,
        "boolean": True,
        "array": [],
    }
    return type_map.get(prop.get("type", "string"))


def create_auth_stage() -> dict:
    """Create a clean auth stage with only form data."""
    return {
        "name": "Get auth token",
        "request": {
            "url": "{host}/auth/token",
            "method": "POST",
            "data": {"username": "{username}", "password": "{password}"},
        },
        "response": {"status_code": 200, "save": {"json": {"token": "access_token"}}},
    }


def generate_tavern_tests(
    spec_path: str,
    output_dir: str,
    has_auth: bool = False,
    test_type: TestType = TestType.ALL,
):
    """Generate Tavern tests from OpenAPI spec."""
    with open(spec_path) as f:
        spec = json.load(f)

    Path(output_dir).mkdir(exist_ok=True)

    click.echo(f"\nGenerating {test_type.value} tests...")

    # Track statistics
    stats = {"auth": 0, "public": 0, "skipped": 0}

    # Generate tests for each path
    for path, methods in spec["paths"].items():
        for method, details in methods.items():
            # Debug logging
            operation_id = details.get("operationId", "")
            click.echo(f"\nProcessing endpoint: {method.upper()} {path}")

            # Skip auth endpoints and auth-required endpoints based on test type
            is_auth_endpoint = (
                path == "/auth/token"
                or operation_id == "login_for_access_token_auth_token_post"
            )
            requires_auth = bool(details.get("security")) or "users" in details.get(
                "tags", []
            )

            click.echo(f"Is auth endpoint? {is_auth_endpoint}")
            click.echo(f"Requires auth? {requires_auth}")
            click.echo(f"Current test type: {test_type}")
            click.echo(f"Has auth credentials? {has_auth}")

            # Skip if auth is needed but not provided
            if (is_auth_endpoint or requires_auth) and not has_auth:
                click.echo(
                    f"Skipping {method.upper()} {path} - auth required but no credentials provided"
                )
                stats["skipped"] += 1
                continue

            # Skip based on test type
            if test_type == TestType.PUBLIC and (is_auth_endpoint or requires_auth):
                click.echo(
                    f"Skipping {method.upper()} {path} - auth endpoint for public tests"
                )
                stats["skipped"] += 1
                continue

            if test_type == TestType.AUTH and not (is_auth_endpoint or requires_auth):
                click.echo(
                    f"Skipping {method.upper()} {path} - public endpoint for auth tests"
                )
                stats["skipped"] += 1
                continue

            test_name = operation_id
            stages = []

            if requires_auth:
                stages.append(create_auth_stage())

                # Don't create a second stage for the login endpoint itself
                if not is_auth_endpoint:
                    endpoint_request = {
                        "url": "{host}" + path,
                        "method": method.upper(),
                        "headers": {"Authorization": "Bearer {token}"},
                    }

                    if "requestBody" in details:
                        content = details["requestBody"]["content"]
                        if "application/json" in content:
                            schema = content["application/json"]["schema"]
                            example = generate_example_from_schema(schema, spec)
                            endpoint_request["json"] = example
                        elif "application/x-www-form-urlencoded" in content:
                            schema = content["application/x-www-form-urlencoded"][
                                "schema"
                            ]
                            example = generate_example_from_schema(schema, spec)
                            endpoint_request["data"] = example

                    stages.append(
                        {
                            "name": details["summary"],
                            "request": endpoint_request,
                            "response": {"status_code": [200, 409]},
                        }
                    )

                stats["auth"] += 1
            else:
                request = {"url": "{host}" + path, "method": method.upper()}

                if "requestBody" in details:
                    content = details["requestBody"]["content"]
                    if "application/json" in content:
                        schema = content["application/json"]["schema"]
                        example = generate_example_from_schema(schema, spec)
                        request["json"] = example
                    elif "application/x-www-form-urlencoded" in content:
                        schema = content["application/x-www-form-urlencoded"]["schema"]
                        example = generate_example_from_schema(schema, spec)
                        request["data"] = example

                stages = [
                    {
                        "name": details["summary"],
                        "request": request,
                        "response": {"status_code": 200},
                    }
                ]

                stats["public"] += 1

            test = {
                "test_name": test_name,
                "marks": ["auth"] if requires_auth else ["public"],
                "stages": stages,
            }

            # Write test file
            output_path = Path(output_dir) / f"test_{test_name}.tavern.yaml"
            save_yaml(test, output_path)

    click.echo("\nTest generation complete!")
    click.echo(f"Generated {stats['auth']} auth tests")
    click.echo(f"Generated {stats['public']} public tests")
    click.echo(f"Skipped {stats['skipped']} tests")


@click.command()
@click.option("--spec", type=str, required=True, help="Path to OpenAPI spec file")
@click.option("--output", type=str, default="tests", help="Output directory for tests")
@click.option(
    "--host", type=str, required=True, help="API host (e.g., http://localhost:8000)"
)
@click.option(
    "--testid",
    type=int,
    required=False,
    default=1,
    help="Existing test user ID (defaults to 1)",
)
@click.option("--username", type=str, help="Existing test username for auth tests")
@click.option("--password", type=str, help="Existing test password for auth tests")
@click.option(
    "--solution",
    type=int,
    required=False,
    default=1,
    help="Existing test solution ID (defaults to 1)",
)
@click.option(
    "--test-type",
    type=click.Choice(["all", "auth", "public"]),
    default="all",
    help="Type of tests to generate",
)
def cli(
    spec: str,
    output: str,
    host: str,
    testid: int,
    username: str,
    password: str,
    solution: int,
    test_type: str,
):
    """Generate Tavern tests from OpenAPI spec."""
    # Create common config
    config = {"variables": {"host": host}}
    config["variables"].update({"user_id": testid})
    config["variables"].update({"solution_id": solution})
    has_auth = bool(username and password)
    if has_auth:
        config["variables"].update({"username": username, "password": password})

    # Write common config
    Path(output).mkdir(exist_ok=True)
    save_yaml(config, Path(output) / "common.yaml")

    generate_tavern_tests(spec, output, has_auth, TestType(test_type))

    click.echo(
        "\nTo use these tests with pytest, add the following to your pyproject.toml:"
    )
    click.echo(f"""
[tool.pytest.ini_options]
addopts = ["--tavern-global-cfg={output}/common.yaml"]
markers = [
    "auth: marks tests that require authentication",
    "public: marks tests that don't require authentication"
]
    """)
    click.echo("\nThen you can run specific test types with:")
    click.echo(f"   pytest {output}/ -v -m auth    # Only auth tests")
    click.echo(f"   pytest {output}/ -v -m public  # Only public tests")
    click.echo(f"   pytest {output}/ -v            # All tests")


if __name__ == "__main__":
    cli()
