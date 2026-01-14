#!/usr/bin/env python3
"""
GID Seminars Aggregator - Main Entry Point

Collects seminars from configured sources, generates outputs (ICS, HTML, JSON),
and optionally uploads to LabKey WebDAV.
"""

import sys
from pathlib import Path

import toml
from rich.console import Console

from src.core.database import SeminarDatabase
from src.core.exclusion_filter import ExclusionFilter
from src.deploy.webdav_uploader import upload_to_labkey
from src.generators.html_generator import HTMLGenerator
from src.generators.ics_generator import ICSGenerator
from src.generators.json_generator import JSONGenerator
from src.sources.collector import SourceCollector

console = Console()


def main(skip_upload: bool = False) -> int:
    """
    Main pipeline: collect -> generate -> upload.

    Args:
        skip_upload: If True, skip the upload step (for local testing)

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    console.print("[bold blue]GID Seminars Aggregator[/bold blue]\n")

    base_dir = Path(__file__).parent
    config_dir = base_dir / "config"

    try:
        # Load configurations
        console.print("[bold]Loading configuration...[/bold]")
        sources_config = toml.load(config_dir / "sources.toml")
        settings_config = toml.load(config_dir / "settings.toml")

        # Initialize database
        db_path = base_dir / settings_config.get("database", {}).get(
            "path", "data/seminars.db"
        )
        database = SeminarDatabase(db_path)
        console.print(f"  Database: {db_path}")

        # Step 1: Collect seminars
        console.print("\n[bold]Step 1: Collecting seminars...[/bold]")
        collector = SourceCollector(
            sources_config=sources_config,
            settings_config=settings_config,
            database=database,
            base_dir=base_dir,
        )
        collection_results = collector.collect_all()

        # Check if any sources succeeded
        successful_sources = sum(
            1 for r in collection_results.values() if r["status"] == "success"
        )
        if successful_sources == 0:
            console.print("\n[red]All sources failed. Aborting.[/red]")
            return 1

        # Load exclusion filter
        console.print("\n[bold]Loading exclusion filter...[/bold]")
        exclusions_path = base_dir / "data" / "excluded_events.toml"
        exclusion_filter = ExclusionFilter(exclusions_path)

        # Step 2: Generate outputs
        console.print("\n[bold]Step 2: Generating outputs...[/bold]")
        output_config = settings_config.get("output", {})
        output_dir = base_dir / output_config.get("output_dir", "local-outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate ICS
        ics_generator = ICSGenerator(settings_config, database, exclusion_filter)
        ics_path = output_dir / output_config.get("ics_filename", "gid_seminars.ics")
        ics_generator.generate(ics_path)

        # Generate HTML
        html_generator = HTMLGenerator(settings_config, database, exclusion_filter)
        html_path = output_dir / output_config.get("html_filename", "index.html")
        html_generator.generate(html_path)

        # Generate JSON
        json_generator = JSONGenerator(settings_config, database, exclusion_filter)
        json_path = output_dir / output_config.get("json_filename", "seminars.json")
        json_generator.generate(json_path)

        # Step 3: Upload to LabKey (unless skipped)
        if not skip_upload:
            console.print("\n[bold]Step 3: Uploading to LabKey...[/bold]")
            upload_results = upload_to_labkey(base_dir)

            # Check for upload failures
            if upload_results:
                failed_uploads = sum(1 for v in upload_results.values() if not v)
                if failed_uploads > 0:
                    console.print(
                        f"\n[yellow]Warning: {failed_uploads} file(s) failed to upload[/yellow]"
                    )
        else:
            console.print("\n[dim]Step 3: Upload skipped (--skip-upload)[/dim]")

        # Print database statistics
        stats = database.get_statistics()
        console.print("\n[bold]Database Statistics:[/bold]")
        console.print(f"  Total seminars: {stats['total_seminars']}")
        console.print(f"  By source: {stats['by_source']}")

        console.print("\n[green]Pipeline completed successfully![/green]")
        return 0

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Check for --skip-upload flag
    skip_upload = "--skip-upload" in sys.argv or "--local" in sys.argv
    sys.exit(main(skip_upload=skip_upload))
