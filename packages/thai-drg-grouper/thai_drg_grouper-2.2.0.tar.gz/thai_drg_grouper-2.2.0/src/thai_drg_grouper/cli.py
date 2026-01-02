"""
Thai DRG Grouper - CLI
"""

import argparse
import json
import sys

from .manager import ThaiDRGGrouperManager


def main():
    parser = argparse.ArgumentParser(
        prog="thai-drg-grouper", description="Thai DRG Grouper - Multi-Version Support"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list
    list_parser = subparsers.add_parser("list", help="List available versions")
    list_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # add
    add_parser = subparsers.add_parser("add", help="Add new version")
    add_parser.add_argument("--version", "-v", required=True, help="Version string")
    add_parser.add_argument("--source", "-s", required=True, help="Source path (zip or folder)")
    add_parser.add_argument("--name", "-n", help="Display name")
    add_parser.add_argument("--set-default", action="store_true", help="Set as default")
    add_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # download
    dl_parser = subparsers.add_parser("download", help="Download version from tcmc.or.th")
    dl_parser.add_argument("--version", "-v", help="Version to download")
    dl_parser.add_argument("--set-default", action="store_true", help="Set as default")
    dl_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # remove
    rm_parser = subparsers.add_parser("remove", help="Remove a version")
    rm_parser.add_argument("--version", "-v", required=True, help="Version to remove")
    rm_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # group
    group_parser = subparsers.add_parser("group", help="Group a case")
    group_parser.add_argument("--pdx", required=True, help="Principal diagnosis")
    group_parser.add_argument("--sdx", help="Secondary diagnoses (comma-separated)")
    group_parser.add_argument("--proc", help="Procedures (comma-separated)")
    group_parser.add_argument("--age", type=int, help="Patient age (required)")
    group_parser.add_argument("--sex", help="Patient sex (M/F)")
    group_parser.add_argument("--los", type=int, default=1, help="Length of stay")
    group_parser.add_argument("--version", "-v", help="DRG version to use")
    group_parser.add_argument("--json", action="store_true", help="Output as JSON")
    group_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # compare
    cmp_parser = subparsers.add_parser("compare", help="Compare across versions")
    cmp_parser.add_argument("--pdx", required=True, help="Principal diagnosis")
    cmp_parser.add_argument("--sdx", help="Secondary diagnoses")
    cmp_parser.add_argument("--proc", help="Procedures")
    cmp_parser.add_argument("--age", type=int, help="Patient age")
    cmp_parser.add_argument("--sex", help="Patient sex (M/F)")
    cmp_parser.add_argument("--los", type=int, default=1, help="Length of stay")
    cmp_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # serve
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port number")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host")
    serve_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--version", "-v", help="Specific version")
    stats_parser.add_argument("--path", "-p", default="./data/versions", help="Versions path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        manager = ThaiDRGGrouperManager(args.path)
    except Exception as e:
        print(f"Error initializing: {e}", file=sys.stderr)
        return 1

    if args.command == "list":
        versions = manager.list_versions()
        if not versions:
            print("No versions installed.")
            print("Run: thai-drg-grouper download --version 6.3")
        else:
            print(f"\nAvailable versions ({len(versions)}):")
            print("-" * 50)
            for v in versions:
                default = " (default)" if v.is_default else ""
                print(f"  {v.version}{default}")
                print(f"    Name: {v.name}")
                print(f"    Rights: {', '.join(v.rights)}")

    elif args.command == "add":
        success = manager.add_version(
            version=args.version,
            source_path=args.source,
            name=args.name,
            set_default=args.set_default,
        )
        if success:
            print(f"✅ Added version {args.version}")
        else:
            print(f"❌ Failed to add version {args.version}")
            return 1

    elif args.command == "download":
        if not args.version:
            print("Available versions to download:")
            for v in manager.DOWNLOAD_URLS:
                print(f"  - {v}")
            return
        success = manager.download_version(args.version, set_default=args.set_default)
        if success:
            print(f"✅ Downloaded version {args.version}")
        else:
            print("❌ Failed to download")
            return 1

    elif args.command == "remove":
        if manager.remove_version(args.version):
            print(f"✅ Removed version {args.version}")
        else:
            print(f"❌ Version {args.version} not found")
            return 1

    elif args.command == "group":
        version = args.version or manager.get_default_version()
        if not version:
            print("No versions available")
            return 1

        sdx = args.sdx.split(",") if args.sdx else []
        procedures = args.proc.split(",") if args.proc else []

        result = manager.group(
            version,
            pdx=args.pdx,
            sdx=sdx,
            procedures=procedures,
            age=args.age,
            sex=args.sex,
            los=args.los,
        )

        if args.json:
            print(result.to_json())
        else:
            print(f"\n📋 Grouping Result (v{version})")
            print("-" * 40)
            print(f"PDx: {result.pdx}")
            print(f"MDC: {result.mdc} - {result.mdc_name}")
            print(f"DC:  {result.dc}")
            print(f"DRG: {result.drg} - {result.drg_name}")
            print(f"RW:  {result.rw:.4f}")
            print(f"AdjRW: {result.adjrw:.4f}")
            print(f"PCL: {result.pcl}")
            print(f"Surgical: {result.is_surgical}")

    elif args.command == "compare":
        sdx = args.sdx.split(",") if args.sdx else []
        procedures = args.proc.split(",") if args.proc else []

        results = manager.group_all_versions(
            pdx=args.pdx, sdx=sdx, procedures=procedures, age=args.age, sex=args.sex, los=args.los
        )

        print("\n📊 Version Comparison")
        print("-" * 50)
        for version, result in results.items():
            if result:
                print(f"  {version}: DRG={result.drg} RW={result.rw:.4f} AdjRW={result.adjrw:.4f}")
            else:
                print(f"  {version}: Error")

    elif args.command == "serve":
        try:
            import uvicorn

            from .api import create_api

            app = create_api(manager)
            print(f"\n🚀 Starting API server on {args.host}:{args.port}")
            print(f"   Docs: http://{args.host}:{args.port}/docs")
            uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("Please install: pip install fastapi uvicorn")
            return 1

    elif args.command == "stats":
        stats = manager.get_stats(args.version)
        print(json.dumps(stats, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
