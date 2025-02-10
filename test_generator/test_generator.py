import json
from pathlib import Path
from typing import Any

import click
import yaml


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


@click.command()
@click.option("--spec", type=str, required=True, help="Path to OpenAPI spec file")
@click.option(
    "--output", type=str, default="conformance", help="Output directory for tests"
)
def cli(spec: str, output: str):
    """Generate Tavern tests from OpenAPI spec."""
    with open(spec) as f:
        spec_data = json.load(f)

    Path(output).mkdir(exist_ok=True)
    click.echo(f"\nGenerating tests to output path {output}")

    # Generate tests for each path
    for path, methods in spec_data["paths"].items():
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
                            example = generate_example_from_schema(schema, spec_data)
                            endpoint_request["json"] = example
                        elif "application/x-www-form-urlencoded" in content:
                            schema = content["application/x-www-form-urlencoded"][
                                "schema"
                            ]
                            example = generate_example_from_schema(schema, spec_data)
                            endpoint_request["data"] = example

                    stages.append(
                        {
                            "name": details["summary"],
                            "request": endpoint_request,
                            "response": {"status_code": [200, 409]},
                        }
                    )
            else:
                request = {"url": "{host}" + path, "method": method.upper()}

                if "requestBody" in details:
                    content = details["requestBody"]["content"]
                    if "application/json" in content:
                        schema = content["application/json"]["schema"]
                        example = generate_example_from_schema(schema, spec_data)
                        request["json"] = example
                    elif "application/x-www-form-urlencoded" in content:
                        schema = content["application/x-www-form-urlencoded"]["schema"]
                        example = generate_example_from_schema(schema, spec_data)
                        request["data"] = example

                stages = [
                    {
                        "name": details["summary"],
                        "request": request,
                        "response": {"status_code": 200},
                    }
                ]

            test = {
                "test_name": test_name,
                "marks": ["auth"] if requires_auth else ["public"],
                "stages": stages,
            }

            # Write test file
            output_path = Path(output) / f"test_{test_name}.tavern.yaml"
            save_yaml(test, output_path)

    click.echo("\nTest generation complete!")


if __name__ == "__main__":
    cli()
