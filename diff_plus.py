#!/usr/bin/env python3
"""
Advanced Diff Tool - Enhanced Version
Compares files with beautiful syntax highlighting and multiple viewing modes
"""
from __future__ import annotations

import sys
import argparse
import difflib
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
from pathlib import Path
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

console = Console()


# ==========================================================
# ===================== ENUMS ==============================
# ==========================================================

class ViewMode(Enum):
    UNIFIED = "unified"
    SIDE_BY_SIDE = "side"
    INLINE = "inline"
    STATS = "stats"


class ChangeType(Enum):
    ADD = "add"
    DELETE = "delete"
    MODIFY = "modify"
    EQUAL = "equal"


# ==========================================================
# ===================== DATA MODEL =========================
# ==========================================================

@dataclass
class DiffOptions:
    context: int = 3
    ignore_whitespace: bool = False
    ignore_case: bool = False
    show_line_numbers: bool = False
    word_diff: bool = False


@dataclass
class DiffResult:
    opcodes: List[Tuple[str, int, int, int, int]]
    a: List[str]
    b: List[str]
    a_name: str
    b_name: str


@dataclass
class DiffStats:
    additions: int = 0
    deletions: int = 0
    modifications: int = 0
    total_lines_a: int = 0
    total_lines_b: int = 0
    similarity: float = 0.0


# ==========================================================
# ===================== CORE ===============================
# ==========================================================

def read_file(path: str) -> List[str]:
    """Read file with multiple encoding fallback"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                return [line.rstrip("\n") for line in f]
        except UnicodeDecodeError:
            continue
        except Exception as e:
            console.print(f"[bold red]Error reading {path}:[/bold red] {e}")
            sys.exit(2)
    
    console.print(f"[bold red]Could not decode {path} with any supported encoding[/bold red]")
    sys.exit(2)


def preprocess_lines(lines: List[str], opts: DiffOptions) -> List[str]:
    """Preprocess lines based on options"""
    result = lines
    
    if opts.ignore_whitespace:
        result = [line.strip() for line in result]
    
    if opts.ignore_case:
        result = [line.lower() for line in result]
    
    return result


def compute_diff(a: List[str], b: List[str], a_name: str, b_name: str, opts: DiffOptions) -> DiffResult:
    """Compute diff with preprocessing"""
    a_processed = preprocess_lines(a, opts)
    b_processed = preprocess_lines(b, opts)
    
    sm = difflib.SequenceMatcher(None, a_processed, b_processed)
    return DiffResult(sm.get_opcodes(), a, b, a_name, b_name)


def compute_stats(result: DiffResult) -> DiffStats:
    """Calculate statistics about the diff"""
    stats = DiffStats()
    stats.total_lines_a = len(result.a)
    stats.total_lines_b = len(result.b)
    
    for tag, i1, i2, j1, j2 in result.opcodes:
        if tag == "insert":
            stats.additions += (j2 - j1)
        elif tag == "delete":
            stats.deletions += (i2 - i1)
        elif tag == "replace":
            stats.modifications += max(i2 - i1, j2 - j1)
    
    # Calculate similarity ratio
    sm = difflib.SequenceMatcher(None, result.a, result.b)
    stats.similarity = sm.ratio() * 100
    
    return stats


def detect_language(filename: str) -> Optional[str]:
    """Auto-detect programming language from file extension"""
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.tsx': 'tsx',
        '.php': 'php',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sql': 'sql',
        '.sh': 'bash',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.md': 'markdown',
    }
    
    ext = Path(filename).suffix.lower()
    return ext_map.get(ext)


def get_file_info(path: str) -> str:
    """Get file size and modification time"""
    try:
        stat = os.stat(path)
        size = stat.st_size
        
        # Format file size
        if size < 1024:
            size_str = f"{size}B"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f}KB"
        else:
            size_str = f"{size/(1024*1024):.1f}MB"
        
        return f"{size_str}"
    except:
        return "N/A"


# ==========================================================
# ===================== WORD DIFF ==========================
# ==========================================================

def highlight_word_diff(old_line: str, new_line: str) -> Tuple[Text, Text]:
    """Highlight word-level differences within lines"""
    old_words = old_line.split()
    new_words = new_line.split()
    
    sm = difflib.SequenceMatcher(None, old_words, new_words)
    
    old_text = Text()
    new_text = Text()
    
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            old_text.append(" ".join(old_words[i1:i2]) + " ")
            new_text.append(" ".join(new_words[j1:j2]) + " ")
        elif tag == "replace":
            old_text.append(" ".join(old_words[i1:i2]) + " ", style="bold red on dark_red")
            new_text.append(" ".join(new_words[j1:j2]) + " ", style="bold green on dark_green")
        elif tag == "delete":
            old_text.append(" ".join(old_words[i1:i2]) + " ", style="bold red on dark_red")
        elif tag == "insert":
            new_text.append(" ".join(new_words[j1:j2]) + " ", style="bold green on dark_green")
    
    return old_text, new_text


# ==========================================================
# ===================== STATS VIEW =========================
# ==========================================================

def render_stats(result: DiffResult, stats: DiffStats):
    """Render comprehensive statistics view"""
    
    # Header
    header_text = f"[bold cyan]Diff Statistics: {result.a_name} ↔ {result.b_name}[/]"
    console.print(Panel(header_text, style="white on black"))
    
    # Create statistics table (expanded but compact)
    stats_table = Table(show_header=False, box=box.ROUNDED, expand=True, padding=(0, 2))
    stats_table.add_column(style="cyan bold", no_wrap=True)
    stats_table.add_column(style="white", justify="left")
    
    stats_table.add_row("📄 File A Lines", f"{stats.total_lines_a:,}")
    stats_table.add_row("📄 File B Lines", f"{stats.total_lines_b:,}")
    stats_table.add_row("➕ Additions", f"[green]{stats.additions:,}[/]")
    stats_table.add_row("➖ Deletions", f"[red]{stats.deletions:,}[/]")
    stats_table.add_row("🔄 Modifications", f"[yellow]{stats.modifications:,}[/]")
    stats_table.add_row("📊 Total Changes", f"[bold]{stats.additions + stats.deletions + stats.modifications:,}[/]")
    stats_table.add_row("✨ Similarity", f"[bold magenta]{stats.similarity:.1f}%[/]")
    
    # File info
    info_a = get_file_info(result.a_name)
    info_b = get_file_info(result.b_name)
    stats_table.add_row("💾 File A Size", info_a)
    stats_table.add_row("💾 File B Size", info_b)
    
    console.print(Panel(stats_table, title="[bold]Statistics[/]", border_style="cyan", padding=(0, 1)))
    
    # Visual change distribution
    if stats.additions + stats.deletions + stats.modifications > 0:
        console.print("\n[bold cyan]Change Distribution:[/]")
        
        total = stats.additions + stats.deletions + stats.modifications
        add_bar = "█" * int((stats.additions / total) * 50)
        del_bar = "█" * int((stats.deletions / total) * 50)
        mod_bar = "█" * int((stats.modifications / total) * 50)
        
        console.print(f"[green]+ {add_bar}[/] {stats.additions}")
        console.print(f"[red]- {del_bar}[/] {stats.deletions}")
        console.print(f"[yellow]~ {mod_bar}[/] {stats.modifications}")


# ==========================================================
# ===================== UNIFIED VIEW =======================
# ==========================================================

def render_unified(result: DiffResult, opts: DiffOptions, lang: Optional[str] = None):
    """Render unified diff view"""
    
    console.print(
        Panel(f"[bold cyan]{result.a_name}[/] ↔ [bold cyan]{result.b_name}[/]",
              style="white on black")
    )

    diff = difflib.unified_diff(
        result.a,
        result.b,
        fromfile=result.a_name,
        tofile=result.b_name,
        lineterm="",
        n=opts.context
    )

    line_num_a = 0
    line_num_b = 0

    for line in diff:
        line_nums = ""
        
        if line.startswith("+++ ") or line.startswith("--- "):
            console.print(Text(line, style="bold cyan"))

        elif line.startswith("@@"):
            console.print(Text(line, style="bold yellow"))
            # Parse line numbers from @@ -1,7 +1,7 @@
            parts = line.split()
            if len(parts) >= 3:
                try:
                    line_num_a = int(parts[1].split(',')[0].replace('-', ''))
                    line_num_b = int(parts[2].split(',')[0].replace('+', ''))
                except:
                    pass

        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:]
            if opts.show_line_numbers:
                line_nums = f"[dim]{line_num_b:4d}[/] "
                line_num_b += 1
            
            if lang:
                syntax = Syntax(content, lang, line_numbers=False, background_color="default")
                console.print(line_nums, Text("+", style="green"), syntax)
            else:
                console.print(line_nums, Text(line, style="green"))

        elif line.startswith("-") and not line.startswith("---"):
            content = line[1:]
            if opts.show_line_numbers:
                line_nums = f"[dim]{line_num_a:4d}[/] "
                line_num_a += 1
            
            if lang:
                syntax = Syntax(content, lang, line_numbers=False, background_color="default")
                console.print(line_nums, Text("-", style="red"), syntax)
            else:
                console.print(line_nums, Text(line, style="red"))

        else:
            if opts.show_line_numbers and line.strip():
                line_nums = f"[dim]{line_num_a:4d}[/] "
                line_num_a += 1
                line_num_b += 1
            console.print(line_nums, line)


# ==========================================================
# ===================== SIDE BY SIDE =======================
# ==========================================================

def render_side_by_side(result: DiffResult, opts: DiffOptions, lang: Optional[str] = None):
    """Render side-by-side diff view with enhancements"""
    
    table = Table.grid(expand=True)
    
    if opts.show_line_numbers:
        table.add_column(width=5, style="dim")  # Line numbers A
    table.add_column(ratio=1, style="dim")      # Symbol A
    table.add_column(ratio=6)                    # Content A
    
    if opts.show_line_numbers:
        table.add_column(width=5, style="dim")  # Line numbers B
    table.add_column(ratio=1, style="dim")      # Symbol B
    table.add_column(ratio=6)                    # Content B
    
    table.box = box.SIMPLE

    console.print(
        Panel(
            f"[bold cyan]{result.a_name}[/] ({get_file_info(result.a_name)})    "
            f"[bold cyan]{result.b_name}[/] ({get_file_info(result.b_name)})",
            style="white on black"
        )
    )

    line_num_a = 1
    line_num_b = 1

    for tag, i1, i2, j1, j2 in result.opcodes:

        if tag == "equal":
            for a_line, b_line in zip(result.a[i1:i2], result.b[j1:j2]):
                left = Syntax(a_line, lang, background_color="default") if lang else a_line
                right = Syntax(b_line, lang, background_color="default") if lang else b_line
                
                row = []
                if opts.show_line_numbers:
                    row.extend([str(line_num_a), "", left, str(line_num_b), "", right])
                else:
                    row.extend(["", left, "", right])
                
                table.add_row(*row)
                line_num_a += 1
                line_num_b += 1

        elif tag == "replace":
            max_lines = max(i2 - i1, j2 - j1)
            a_lines = result.a[i1:i2]
            b_lines = result.b[j1:j2]
            
            for idx in range(max_lines):
                a_line = a_lines[idx] if idx < len(a_lines) else ""
                b_line = b_lines[idx] if idx < len(b_lines) else ""
                
                if opts.word_diff and a_line and b_line:
                    left, right = highlight_word_diff(a_line, b_line)
                else:
                    if lang and a_line:
                        left = Text(a_line, style="white on dark_red")
                    else:
                        left = Text(a_line, style="red") if a_line else ""
                    
                    if lang and b_line:
                        right = Text(b_line, style="black on dark_green")
                    else:
                        right = Text(b_line, style="green") if b_line else ""
                
                row = []
                if opts.show_line_numbers:
                    num_a = str(line_num_a) if a_line else ""
                    num_b = str(line_num_b) if b_line else ""
                    row.extend([num_a, "~" if a_line else "", left, num_b, "~" if b_line else "", right])
                else:
                    row.extend(["~" if a_line else "", left, "~" if b_line else "", right])
                
                table.add_row(*row)
                
                if a_line:
                    line_num_a += 1
                if b_line:
                    line_num_b += 1

        elif tag == "delete":
            for a_line in result.a[i1:i2]:
                left = Text(a_line, style="white on red")
                
                row = []
                if opts.show_line_numbers:
                    row.extend([str(line_num_a), "-", left, "", "", ""])
                else:
                    row.extend(["-", left, "", ""])
                
                table.add_row(*row)
                line_num_a += 1

        elif tag == "insert":
            for b_line in result.b[j1:j2]:
                right = Text(b_line, style="black on green")
                
                row = []
                if opts.show_line_numbers:
                    row.extend(["", "", "", str(line_num_b), "+", right])
                else:
                    row.extend(["", "", "+", right])
                
                table.add_row(*row)
                line_num_b += 1

    console.print(table)


# ==========================================================
# ===================== INLINE VIEW ========================
# ==========================================================

def render_inline(result: DiffResult, opts: DiffOptions, lang: Optional[str] = None):
    """Render inline diff view (compact single column)"""
    
    console.print(
        Panel(f"[bold cyan]{result.a_name}[/] → [bold cyan]{result.b_name}[/]",
              style="white on black")
    )
    
    line_num = 1
    
    for tag, i1, i2, j1, j2 in result.opcodes:
        
        if tag == "equal":
            for line in result.a[i1:i2]:
                prefix = f"[dim]{line_num:4d}[/] " if opts.show_line_numbers else ""
                content = Syntax(line, lang, background_color="default") if lang else line
                console.print(prefix, "  ", content)
                line_num += 1
        
        elif tag == "delete":
            for line in result.a[i1:i2]:
                prefix = f"[dim]{line_num:4d}[/] " if opts.show_line_numbers else ""
                console.print(prefix, Text("- " + line, style="red"))
                line_num += 1
        
        elif tag == "insert":
            for line in result.b[j1:j2]:
                prefix = f"[dim]{line_num:4d}[/] " if opts.show_line_numbers else ""
                console.print(prefix, Text("+ " + line, style="green"))
                line_num += 1
        
        elif tag == "replace":
            for line in result.a[i1:i2]:
                prefix = f"[dim]{line_num:4d}[/] " if opts.show_line_numbers else ""
                console.print(prefix, Text("- " + line, style="red"))
                line_num += 1
            for line in result.b[j1:j2]:
                prefix = f"[dim]{line_num:4d}[/] " if opts.show_line_numbers else ""
                console.print(prefix, Text("+ " + line, style="green"))
                line_num += 1


# ==========================================================
# ===================== CLI ================================
# ==========================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="diff_plus",
        description="""
╔═══════════════════════════════════════════════════════╗
║  Advanced Diff Tool - Compare files beautifully      ║
╚═══════════════════════════════════════════════════════╝

Features:
  • Multiple view modes (unified, side-by-side, inline, stats)
  • Syntax highlighting with auto-detection
  • Word-level diff highlighting
  • Line numbers
  • Ignore whitespace/case options
  • File statistics and similarity metrics
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.py file2.py                    # Basic unified diff
  %(prog)s file1.py file2.py -s                 # Side-by-side view
  %(prog)s file1.py file2.py --stats            # Show statistics
  %(prog)s file1.py file2.py -l python -n       # With syntax and line numbers
  %(prog)s file1.py file2.py -w --word-diff     # Ignore whitespace + word diff
        """
    )

    parser.add_argument("a", help="First file to compare")
    parser.add_argument("b", help="Second file to compare")

    # View modes (mutually exclusive)
    view_group = parser.add_mutually_exclusive_group()
    view_group.add_argument(
        "-s", "--side",
        action="store_true",
        help="Side-by-side view"
    )
    view_group.add_argument(
        "-i", "--inline",
        action="store_true",
        help="Inline/compact view"
    )
    view_group.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only"
    )

    # Syntax highlighting
    parser.add_argument(
        "-l", "--lang",
        metavar="LANG",
        help="Syntax highlight language (auto-detected if not specified)"
    )

    # Display options
    parser.add_argument(
        "-n", "--line-numbers",
        action="store_true",
        help="Show line numbers"
    )

    parser.add_argument(
        "-c", "--context",
        type=int,
        default=3,
        metavar="N",
        help="Number of context lines (default: 3)"
    )

    # Processing options
    parser.add_argument(
        "-w", "--ignore-whitespace",
        action="store_true",
        help="Ignore whitespace differences"
    )

    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Ignore case differences"
    )

    parser.add_argument(
        "--word-diff",
        action="store_true",
        help="Show word-level differences (side-by-side mode only)"
    )

    # Output options
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode - only show if files differ"
    )

    return parser


# ==========================================================
# ===================== MAIN ===============================
# ==========================================================

def main():
    parser = build_parser()
    args = parser.parse_args()

    # Check if files exist
    if not os.path.exists(args.a):
        console.print(f"[bold red]Error: File '{args.a}' not found[/bold red]")
        sys.exit(1)
    if not os.path.exists(args.b):
        console.print(f"[bold red]Error: File '{args.b}' not found[/bold red]")
        sys.exit(1)

    # Disable colors if requested
    if args.no_color:
        console._color_system = None

    # Create options
    opts = DiffOptions(
        context=args.context,
        ignore_whitespace=args.ignore_whitespace,
        ignore_case=args.ignore_case,
        show_line_numbers=args.line_numbers,
        word_diff=args.word_diff
    )

    # Read files
    a_lines = read_file(args.a)
    b_lines = read_file(args.b)

    # Check if files are identical
    if a_lines == b_lines:
        if not args.quiet:
            console.print("[green]✓ Files are identical[/green]")
        sys.exit(0)

    # Compute diff
    result = compute_diff(a_lines, b_lines, args.a, args.b, opts)

    # Auto-detect language if not specified
    lang = args.lang
    if not lang:
        lang = detect_language(args.a)

    # Quiet mode - just exit with code 1 if different
    if args.quiet:
        sys.exit(1)

    # Render based on mode
    if args.stats:
        stats = compute_stats(result)
        render_stats(result, stats)
    elif args.side:
        render_side_by_side(result, opts, lang)
    elif args.inline:
        render_inline(result, opts, lang)
    else:
        render_unified(result, opts, lang)

    # Show quick stats at the end (except in stats mode)
    if not args.stats:
        stats = compute_stats(result)
        console.print(f"\n[dim]Changes: [green]+{stats.additions}[/] "
                     f"[red]-{stats.deletions}[/] "
                     f"[yellow]~{stats.modifications}[/] | "
                     f"Similarity: {stats.similarity:.1f}%[/]")


if __name__ == "__main__":
    main()