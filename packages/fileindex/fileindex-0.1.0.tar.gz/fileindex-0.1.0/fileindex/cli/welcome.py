from .style import Style


BANNER = [
    "███████╗██╗██╗     ███████╗██╗███╗   ██╗██████╗ ███████╗██╗  ██╗",
    "██╔════╝██║██║     ██╔════╝██║████╗  ██║██╔══██╗██╔════╝╚██╗██╔╝",
    "█████╗  ██║██║     █████╗  ██║██╔██╗ ██║██║  ██║█████╗   ╚███╔╝ ",
    "██╔══╝  ██║██║     ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝   ██╔██╗ ",
    "██║     ██║███████╗███████╗██║██║ ╚████║██████╔╝███████╗██╔╝ ██╗",
    "╚═╝     ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝",
]


def show_welcome():
    style = Style()

    banner_style = Style.apply(Style.BOLD, Style.BRIGHT_GREEN)
    subtitle_style = Style.apply(Style.DIM, Style.BRIGHT_YELLOW)
    section_style = Style.apply(Style.BOLD, Style.BRIGHT_CYAN)
    item_style = Style.apply(Style.CYAN)
    hint_style = Style.apply(Style.DIM)

    print()

    # Banner
    for line in BANNER:
        style.pretty(line, width=90, char=" ", style=banner_style)

    print()

    # Subtitle
    style.pretty(
        " Fast Local Indexing And Search ",
        width=90,
        char="-",
        style=subtitle_style,
    )

    print()

    # Commands
    style.pretty(" Commands ", 90, " ", section_style)
    style.pretty(" scan <path>                     → index a directory", 90, " ", item_style)
    style.pretty(" search <query>                  → search cached index", 90, " ", item_style)
    style.pretty(" status                          → show cache status", 90, " ", item_style)
    style.pretty(" cache clear                     → clear cached index", 90, " ", item_style)

    print()

    # Search filters
    style.pretty(" Search Filters ", 90, " ", section_style)
    style.pretty(" --ext <ext>                     → filter by extension", 90, " ", item_style)
    style.pretty(" --path <substring>              → filter by path", 90, " ", item_style)
    style.pretty(" --min-size <bytes>              → minimum file size", 90, " ", item_style)
    style.pretty(" --max-size <bytes>              → maximum file size", 90, " ", item_style)
    style.pretty(" --limit <n>                     → limit output (default: 10)", 90, " ", item_style)

    print()

    # Examples
    style.pretty(" Examples ", 90, " ", section_style)
    style.pretty(" fileindex scan ~/projects", 90, " ", hint_style)
    style.pretty(" fileindex search main", 90, " ", hint_style)
    style.pretty(" fileindex search main --ext py --limit 20", 90, " ", hint_style)
    style.pretty(" fileindex search main --path src --min-size 1000", 90, " ", hint_style)
    style.pretty(" fileindex status", 90, " ", hint_style)

    print()

    # Footer
    style.pretty(
        " Tip: run scan once, then search instantly using cache ",
        90,
        " ",
        hint_style,
    )

    print()
