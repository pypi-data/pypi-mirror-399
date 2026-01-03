#!/usr/bin/env python3
import sys
import time

from .cli.welcome import show_welcome
from .cli.style import Style
from .core.scan import Scan
from .core.search import Search
from .core.cache import IndexCache


style = Style()
cache = IndexCache()


def dup_cmd():
    data = cache.load()
    if not data:
        style.pretty(
            " No cache found. Run: fileindex scan <path> ",
            70,
            "!",
            Style.ERROR,
        )
        return

    search = Search(data["records"])
    duplicates = search.find_duplicates()

    if not duplicates:
        style.pretty(
            " No duplicate files found ",
            70,
            " ",
            Style.SUCCESS,
        )
        return

    style.pretty(
        f" Found {len(duplicates)} duplicate groups ",
        70,
        " ",
        Style.INFO,
    )

    for h, files in duplicates.items():
        print(f"\nHash: {h[:12]}…")
        for f in files:
            print(f"  {f['path']}")


def scan_cmd(args):
    if not args:
        style.pretty(
            " Usage: fileindex scan <path> ",
            width=70,
            char=" ",
            style=Style.WARNING,
        )
        return

    path = args[0]

    try:
        previous = cache.get_records()
        records = Scan(path, previous_records=previous).run()
        cache.save(path, records)

        style.pretty(
            f" Indexed {len(records)} files ",
            width=70,
            char=" ",
            style=Style.SUCCESS,
        )

    except (FileNotFoundError, NotADirectoryError) as e:
        style.pretty(f" {e} ", 70, "!", Style.ERROR)


def search_cmd(args):
    if not args:
        style.pretty(
            " Usage: fileindex search <query>  OR  fileindex search <path> <query> ",
            width=70,
            char=" ",
            style=Style.WARNING,
        )
        return
    # defaults
    query = None
    ext = None
    min_size = None
    max_size = None
    limit = 10
    path_filter = None

    # parse args (explicit)
    i = 0
    while i < len(args):
        if args[i] == "--ext":
            ext = args[i + 1]
            i += 2
        elif args[i] == "--min-size":
            min_size = int(args[i + 1])
            i += 2
        elif args[i] == "--max-size":
            max_size = int(args[i + 1])
            i += 2
        elif args[i] == "--limit":
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--path":
            path_filter = args[i + 1]
            i += 2
        else:
            if query is None:
                query = args[i]
            i += 1

    if not query:
        style.pretty(" Missing search query ", 70, "!", Style.ERROR)
        return

    path = cache.get_last_root()
    if not path:
        style.pretty(
                " No cached index found. Run: fileindex scan <path> ",
                70,
                "!",
                Style.ERROR,
            )
        return

    try:
        data = cache.load()
        records = data["records"]

        search = Search(records)

        results = search.by_name(query)

        if path_filter:
            results = Search(results).by_path(path_filter)

        if ext:
            results = Search(results).by_extension(ext)

        if min_size is not None or max_size is not None:
            results = Search(results).by_size(min_size, max_size)

        style.pretty(
                f" Found {len(results)} results ",
                70,
                " ",
                Style.INFO,
            )
        for r in results[:limit]:
            print(r["path"])

        if len(results) > limit:
            print(f" ... and {len(results) - limit} more ")

    except Exception as e:
        style.pretty(f" {e} ", 70, " ", Style.ERROR)


def status_cmd():
    data = cache.load()

    if not data:
        style.pretty(
            " No cache found ",
            width=70,
            char="!",
            style=Style.ERROR,
        )
        return

    scanned_time = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(data["scanned_at"]),
    )

    style.pretty(" Cache Status ", 70, "-", Style.INFO)
    print(f"Root        : {data['root']}")
    print(f"Files       : {data['file_count']}")
    print(f"Scanned At  : {scanned_time}")


def cache_clear_cmd():
    if not cache.has_cache():
        style.pretty(" Cache is already empty ", 70, " ", Style.WARNING)
        return

    cache.clear()
    style.pretty(
            " cache cleared successfully ",
            70,
            " ",
            Style.SUCCESS,
        )


def dispatch():
    args = sys.argv[1:]

    if not args:
        show_welcome()
        return 0

    command = args[0]
    command_args = args[1:]

    try:
        if command == "scan":
            scan_cmd(command_args)
            return 0
        elif command == "search":
            search_cmd(command_args)
            return 0
        elif command == "status":
            status_cmd()
            return 0
        elif command == "dup":
            dup_cmd()
            return 0
        elif command == "cache" and command_args == ["clear"]:
            cache_clear_cmd()
            return 0
        else:
            style.pretty(
                f" Unknown command: {command} ",
                width=70,
                char="!",
                style=Style.ERROR,
            )
            return 1
    except Exception as e:
        style.pretty(f" Error: {e} ", 70, "!", Style.ERROR)
        return 1


def main():
    return dispatch()


if __name__ == "__main__":
    sys.exit(main())
