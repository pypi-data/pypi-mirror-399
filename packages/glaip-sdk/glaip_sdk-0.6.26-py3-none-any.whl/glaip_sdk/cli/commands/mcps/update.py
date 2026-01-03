"""Update MCP command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import display_update_success, handle_json_output, handle_rich_output
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context

from ._common import (
    _assemble_update_data_from_cli_options,
    _assemble_update_data_from_import_payload,
    _handle_cli_error,
    _handle_update_preview_and_confirmation,
    _load_import_ready_payload,
    _resolve_mcp,
    _validate_import_payload_fields,
    _validate_update_inputs,
    console,
    mcps_group,
)


@mcps_group.command()
@click.argument("mcp_ref")
@click.option("--name", help="New MCP name")
@click.option("--transport", type=click.Choice(["http", "sse"]), help="New transport protocol")
@click.option("--description", help="New description")
@click.option(
    "--config",
    help="JSON configuration string or @file reference (e.g., @config.json)",
)
@click.option(
    "--auth",
    "--authentication",
    "auth",
    help="JSON authentication object or @file reference (e.g., @auth.json)",
)
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Import MCP configuration from JSON or YAML export",
)
@click.option("-y", is_flag=True, help="Skip confirmation prompt when using --import")
@output_flags()
@click.pass_context
def update(
    ctx: Any,
    mcp_ref: str,
    name: str | None,
    transport: str | None,
    description: str | None,
    config: str | None,
    auth: str | None,
    import_file: str | None,
    y: bool,
) -> None:
    r"""Update an existing MCP with new configuration values.

    You can update an MCP by providing individual fields via CLI options, or by
    importing from a file and optionally overriding specific fields.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)
        name: New MCP name (optional)
        transport: New transport protocol (optional)
        description: New description (optional)
        config: New JSON configuration string or @file reference (optional)
        auth: New JSON authentication object or @file reference (optional)
        import_file: Optional path to import configuration from export file.
            CLI options override imported values.
        y: Skip confirmation prompt when using --import

    Raises:
        ClickException: If MCP not found, JSON invalid, or no fields specified

    Note:
        Must specify either --import OR at least one CLI field.
        CLI options override imported values when both are specified.
        Uses PATCH for import-based updates, PUT/PATCH for CLI-only updates.

    \b
    Examples:
        Update with CLI options:
            aip mcps update my-mcp --name new-name --transport sse

        Import from file:
            aip mcps update my-mcp --import mcp-export.json

        Import with overrides:
            aip mcps update my-mcp --import mcp-export.json --name new-name -y
    """
    try:
        client = get_client(ctx)

        # Validate that at least one update method is provided
        _validate_update_inputs(name, transport, description, config, auth, import_file)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Load and validate import data if provided
        import_payload = None
        if import_file:
            import_payload = _load_import_ready_payload(import_file)
            if not _validate_import_payload_fields(import_payload):
                return

        # Build update_data from import payload and CLI options
        update_data = _assemble_update_data_from_import_payload(import_payload)
        update_data = _assemble_update_data_from_cli_options(
            update_data, name, transport, description, config, auth, import_payload, mcp
        )

        if not update_data:
            raise click.ClickException("No update fields specified")

        # Show confirmation preview for import-based updates (unless -y flag)
        if not _handle_update_preview_and_confirmation(
            import_payload, y, mcp, update_data, name, transport, description, config, auth
        ):
            return

        # Update MCP
        with spinner_context(
            ctx,
            "[bold blue]Updating MCP…[/bold blue]",
            console_override=console,
        ):
            updated_mcp = client.mcps.update_mcp(mcp, **update_data)

        handle_json_output(ctx, updated_mcp.model_dump())
        handle_rich_output(ctx, display_update_success("MCP", updated_mcp.name))

    except Exception as e:
        _handle_cli_error(ctx, e, "MCP update")
