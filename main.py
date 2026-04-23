from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from simple_term_menu import TerminalMenu

from src.common.analysis import Analysis
from src.common.indexer import Indexer
from src.common.util import package_data
from src.common.util.strings import snake_to_title


def analyze(name: str | None = None, **kwargs):
    """Run analysis by name or show interactive menu."""
    analyses = Analysis.load()

    if not analyses:
        print("No analyses found in src/analysis/")
        return

    output_dir = Path("output")

    # If name provided, run that specific analysis
    if name:
        if name == "all":
            print("\nRunning all analyses...\n")
            for analysis_cls in analyses:
                instance = analysis_cls()
                print(f"Running: {instance.name}")
                saved = instance.save(output_dir, formats=["png", "pdf", "csv", "json", "gif"])
                for fmt, path in saved.items():
                    print(f"  {fmt}: {path}")
            print("\nAll analyses complete.")
            return

        # Find matching analysis
        for analysis_cls in analyses:
            instance = analysis_cls()
            if instance.name == name:
                print(f"\nRunning: {instance.name}\n")
                saved = instance.save(output_dir, formats=["png", "pdf", "csv", "json", "gif"])
                print("Saved files:")
                for fmt, path in saved.items():
                    print(f"  {fmt}: {path}")
                return

        # No match found
        print(f"Analysis '{name}' not found. Available analyses:")
        for analysis_cls in analyses:
            instance = analysis_cls()
            print(f"  - {instance.name}")
        sys.exit(1)

    # Interactive menu mode
    options = ["[All] Run all analyses"]
    for analysis_cls in analyses:
        instance = analysis_cls()
        options.append(f"{snake_to_title(instance.name)}: {instance.description}")
    options.append("[Exit]")

    menu = TerminalMenu(
        options,
        title="Select an analysis to run (use arrow keys):",
        cycle_cursor=True,
        clear_screen=False,
    )
    choice = menu.show()

    if choice is None or choice == len(options) - 1:
        print("Exiting.")
        return

    if choice == 0:
        # Run all analyses
        print("\nRunning all analyses...\n")
        for analysis_cls in analyses:
            instance = analysis_cls()
            print(f"Running: {instance.name}")
            saved = instance.save(output_dir, formats=["png", "pdf", "csv", "json", "gif"])
            for fmt, path in saved.items():
                print(f"  {fmt}: {path}")
        print("\nAll analyses complete.")
    else:
        # Run selected analysis
        analysis_cls = analyses[choice - 1]
        instance = analysis_cls()
        print(f"\nRunning: {instance.name}\n")
        saved = instance.save(output_dir, formats=["png", "pdf", "csv", "json", "gif"])
        print("Saved files:")
        for fmt, path in saved.items():
            print(f"  {fmt}: {path}")


def index(
    source: str | None = None,
    schema: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    max_records: int | None = None,
):
    """
    Select an indexer and run data fetching.

    Args:
        source: Source to use (e.g., 'kalshi' or 'polymarket'). Used when interactive mode isn't provided.
        schema: Type of data to fetch (e.g., 'trades' or 'markets'). Used when interactive mode isn't provided.
        start_date: Start date in YYYY-MM-DD format. Converted to datetime if provided.
        end_date: End date in YYYY-MM-DD format. Converted to datetime if provided.
        max_records: Maximum number of records to fetch (converted to int if provided).
    """
    indexers = Indexer.load()

    if not indexers:
        print("No indexers found in src/indexers/")
        return

    if source is None and schema is None:
        # Interactive mode
        # Build menu options
        options = []
        for indexer_cls in indexers:
            instance = indexer_cls()
            options.append(f"{snake_to_title(instance.name)}: {instance.description}")
        options.append("[Exit]")

        menu = TerminalMenu(
            options,
            title="Select an indexer to run (use arrow keys):",
            cycle_cursor=True,
            clear_screen=False,
        )
        choice = menu.show()

        if choice is None or choice == len(options) - 1:
            print("Exiting.")
            return

        indexer_cls = indexers[choice]
        instance = indexer_cls()
        print(f"\nRunning: {instance.name}\n")
        instance.run()
        print("\nIndexer complete.")
    else:
        # Non-interactive mode with source and type provided
        if not source:
            print("Source is required when passing command arguments.")
            return

        if not schema:
            print("Schema is required when passing command arguments.")
            return

        # Convert date strings to datetime objects
        start_date_dt = datetime.fromisoformat(start_date) if start_date else None
        end_date_dt = datetime.fromisoformat(end_date) if end_date else None

        # Find the right indexer class
        indexer: Indexer = None
        for cls in indexers:
            instance = cls()
            if instance.name == f"{source}_{schema}":
                indexer = instance
                break

        if indexer is None:
            print(f"No indexer found with source={source} and type={schema}")
            return

        print(f"\nRunning: {str(indexer)}\n")
        indexer.run(start_date=start_date_dt, end_date=end_date_dt, max_records=max_records)
        print("\nIndexer complete.")


def package():
    """Package the data directory into a zstd-compressed tar archive."""
    success = package_data()
    sys.exit(0 if success else 1)


def main():
    parser = argparse.ArgumentParser(prog="main.py", description="Run analysis command")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Run an analysis")
    analyze_parser.add_argument("--name", type=str, help="Name of the analysis script")

    # Index subcommand
    index_parser = subparsers.add_parser("index", help="Run an indexer")
    index_parser.add_argument("--source", type=str, dest="source", help="Source to use (e.g. kalshi, polymarket)")
    index_parser.add_argument("--schema", type=str, dest="schema", help="Type of data to fetch (e.g. trades, markets)")
    index_parser.add_argument("--start-date", type=str, dest="start_date", help="Start date in YYYY-MM-DD format")
    index_parser.add_argument("--end-date", type=str, dest="end_date", help="End date in YYYY-MM-DD format")
    index_parser.add_argument("--max-records", type=int, dest="max_records", help="Maximum number of records to fetch")

    # Package subcommand
    subparsers.add_parser("package", help="Package the data")

    args = parser.parse_args()

    if not args.command or args.command not in ["analyze", "index", "package"]:
        print(f"Unknown command: {args.command}")
        print("Commands: analyze, index, package")
        sys.exit(1)

    if args.command == "analyze":
        analyze(args.name)

    elif args.command == "index":
        index(
            args.source,
            args.schema,
            args.start_date,
            args.end_date,
            args.max_records,
        )

    elif args.command == "package":
        package()


if __name__ == "__main__":
    main()
