"""CLI entry point for ai-api-test-generator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .parser import OpenAPIParser
from .generator import AITestGenerator, OfflineTestGenerator
from .formatters import to_postman_collection, to_pytest, to_jest, to_rest_assured

console = Console()

FORMATS = ["postman", "pytest", "jest", "rest-assured", "all"]


@click.command()
@click.argument("spec", type=str)
@click.option(
    "-f", "--format",
    "output_format",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="all",
    help="Output format (default: all).",
)
@click.option("-o", "--output-dir", default="./generated_tests", help="Output directory.")
@click.option("--base-url", default=None, help="Override the base URL from the spec.")
@click.option("--api-key", default=None, help="OpenAI API key (or set OPENAI_API_KEY).")
@click.option("--model", default="gpt-4o-mini", help="OpenAI model to use.")
@click.option("--auth-token", default=None, help="Bearer token for the target API.")
@click.option("--auth-header", default=None, help="Custom auth header (Name:Value).")
@click.option("--offline", is_flag=True, help="Generate tests without AI (rule-based).")
@click.option("--endpoint", multiple=True, help="Filter to specific endpoints (can repeat).")
@click.version_option(version=__version__)
def main(
    spec: str,
    output_format: str,
    output_dir: str,
    base_url: str | None,
    api_key: str | None,
    model: str,
    auth_token: str | None,
    auth_header: str | None,
    offline: bool,
    endpoint: tuple[str, ...],
):
    """Generate API tests from an OpenAPI/Swagger specification.

    SPEC can be a local file path (YAML/JSON) or a URL.

    \b
    Examples:
      ai-test-gen openapi.yaml
      ai-test-gen https://petstore3.swagger.io/api/v3/openapi.json -f pytest
      ai-test-gen spec.json --offline --format postman
    """
    console.print(
        Panel.fit(
            f"[bold cyan]AI API Test Generator[/bold cyan] v{__version__}",
            subtitle="Powered by OpenAI",
        )
    )

    # --- Parse spec ---
    console.print(f"\n[bold]📄 Parsing spec:[/bold] {spec}")
    try:
        parser = OpenAPIParser(spec)
        api_spec = parser.parse()
    except Exception as e:
        console.print(f"[red]Error parsing spec: {e}[/red]")
        sys.exit(1)

    console.print(f"   API: [green]{api_spec.title}[/green] v{api_spec.version}")
    console.print(f"   Endpoints found: [green]{len(api_spec.endpoints)}[/green]")

    api_context = parser.to_prompt_context(api_spec)

    # --- Auth config ---
    auth_config = None
    if auth_token or auth_header:
        auth_config = {"headers": {}}
        if auth_token:
            auth_config["headers"]["Authorization"] = f"Bearer {auth_token}"
        if auth_header and ":" in auth_header:
            k, v = auth_header.split(":", 1)
            auth_config["headers"][k.strip()] = v.strip()

    # --- Generate tests ---
    console.print("\n[bold]🤖 Generating test scenarios...[/bold]")

    endpoints_filter = list(endpoint) if endpoint else None

    if offline:
        gen = OfflineTestGenerator()
        all_tests = gen.generate_tests(api_spec, auth_config, endpoints_filter)
    else:
        try:
            gen = AITestGenerator(  # type: ignore[assignment]
                api_key=api_key,
                model=model,
                base_url_override=base_url,
            )
            all_tests = gen.generate_tests(api_spec, api_context, auth_config, endpoints_filter)
        except ValueError as e:
            console.print(f"[yellow]{e}[/yellow]")
            console.print("[yellow]Falling back to offline (rule-based) generation...[/yellow]")
            gen = OfflineTestGenerator()  # type: ignore[assignment]
            all_tests = gen.generate_tests(api_spec, auth_config, endpoints_filter)

    total = sum(len(v) for v in all_tests.values())
    console.print(f"   Generated [green]{total}[/green] test scenarios")

    # --- Write output ---
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    effective_base = base_url or api_spec.base_url
    formats_to_write = FORMATS[:-1] if output_format == "all" else [output_format]

    console.print(f"\n[bold]📁 Writing tests to:[/bold] {out.resolve()}")

    for fmt in formats_to_write:
        if fmt == "postman":
            data = to_postman_collection(api_spec.title, effective_base, all_tests)
            p = out / "postman_collection.json"
            p.write_text(json.dumps(data, indent=2), encoding="utf-8")
            console.print(f"   ✅ Postman Collection: [cyan]{p}[/cyan]")

        elif fmt == "pytest":
            code = to_pytest(effective_base, all_tests)
            p = out / "test_api.py"
            p.write_text(code, encoding="utf-8")
            console.print(f"   ✅ pytest + requests: [cyan]{p}[/cyan]")

        elif fmt == "jest":
            code = to_jest(effective_base, all_tests)
            p = out / "api.test.js"
            p.write_text(code, encoding="utf-8")
            console.print(f"   ✅ Jest + axios:      [cyan]{p}[/cyan]")

        elif fmt == "rest-assured":
            code = to_rest_assured(effective_base, all_tests)
            p = out / "ApiTests.java"
            p.write_text(code, encoding="utf-8")
            console.print(f"   ✅ REST Assured:      [cyan]{p}[/cyan]")

    console.print("\n[bold green]✨ Done![/bold green]\n")


if __name__ == "__main__":
    main()
