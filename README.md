# 🚀 Advanced Diff Tool

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Rich](https://img.shields.io/badge/rich-13.0+-orange.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**A beautiful, feature-rich file comparison tool with syntax highlighting and multiple viewing modes**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Documentation](#-documentation)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎨 **Multiple View Modes**
- **Unified** - Traditional diff format
- **Side-by-Side** - Horizontal comparison
- **Inline** - Compact single column
- **Statistics** - Detailed metrics

### 🔍 **Smart Analysis**
- Auto language detection (20+ languages)
- Word-level diff highlighting
- Similarity percentage
- Change distribution charts

</td>
<td width="50%">

### 🛡️ **Robust Processing**
- Multi-encoding support
- Whitespace ignore option
- Case-insensitive comparison
- Configurable context lines

### 📊 **Rich Information**
- Line numbers display
- File size comparison
- Addition/deletion/modification counts
- Visual progress indicators

</td>
</tr>
</table>

---

## 🎬 Demo
![ScreenShot](https://htdark.com/images/uploads/2026/02/KEeL4aTQ.png)

### 📈 Statistics View
```bash
python diff_plus.py old_file.php new_file.php --stats
```

```
╭──────────────────────────────────────────────────────╮
│ Diff Statistics: old_file.php ↔ new_file.php        │
╰──────────────────────────────────────────────────────╯
╭─────────────────── Statistics ───────────────────────╮
│ 📄 File A Lines      │ 70                            │
│ 📄 File B Lines      │ 143                           │
│ ➕ Additions         │ 31                            │
│ ➖ Deletions         │ 1                             │
│ 🔄 Modifications     │ 74                            │
│ 📊 Total Changes     │ 106                           │
│ ✨ Similarity        │ 41.3%                         │
│ 💾 File A Size       │ 1.6KB                         │
│ 💾 File B Size       │ 4.1KB                         │
╰──────────────────────────────────────────────────────╯

Change Distribution:
+ ██████████████ 31
-  1
~ ██████████████████████████████████ 74
```

### 🎨 Side-by-Side View
Perfect for reviewing code changes with syntax highlighting:
```bash
python diff_plus.py old.py new.py -s -n -l python
```

### 📝 Unified View
Classic diff format with beautiful colors:
```bash
python diff_plus.py config_v1.json config_v2.json
```

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install rich
```

### Download
```bash
# Clone or download diff_plus.py
wget https://raw.githubusercontent.com/LvL23HT/diff_plus/main/diff_plus.py
chmod +x diff_plus.py
```

---

## 🚀 Quick Start

### Basic Usage
```bash
# Simple comparison
python diff_plus.py file1.txt file2.txt

# Side-by-side view
python diff_plus.py file1.py file2.py -s

# Show statistics
python diff_plus.py old.js new.js --stats
```

### With Line Numbers
```bash
python diff_plus.py old_code.php new_code.php -s -n
```

### Ignore Whitespace
```bash
python diff_plus.py config1.yaml config2.yaml -w
```

---

## 💡 Usage Examples

### 🔧 Development Workflow

#### Compare Git Changes
```bash
# Compare current file with last commit
git show HEAD:src/app.py > /tmp/old_app.py
python diff_plus.py /tmp/old_app.py src/app.py -s -n
```

#### Review Pull Request
```bash
# Side-by-side with word-level diff
python diff_plus.py feature-old.js feature-new.js -s --word-diff
```

#### Code Refactoring
```bash
# See what changed after refactoring
python diff_plus.py before_refactor.py after_refactor.py --stats
```

### 📄 Configuration Management

#### Compare Config Files
```bash
# Ignore whitespace differences
python diff_plus.py production.conf staging.conf -w
```

#### Environment Comparison
```bash
# Compare .env files (ignore case)
python diff_plus.py .env.development .env.production --ignore-case
```

### 📚 Documentation Review

#### Track Documentation Changes
```bash
# Inline view for markdown files
python diff_plus.py README_v1.md README_v2.md -i -n
```

---

## 🎯 All Command Line Options

```
positional arguments:
  a                     First file to compare
  b                     Second file to compare

View Modes (mutually exclusive):
  -s, --side           Side-by-side view
  -i, --inline         Inline/compact view
  --stats              Show statistics only

Syntax Highlighting:
  -l LANG, --lang LANG Language (auto-detected if not specified)
                       Supported: python, php, javascript, java,
                       cpp, go, rust, html, css, sql, json, etc.

Display Options:
  -n, --line-numbers   Show line numbers
  -c N, --context N    Number of context lines (default: 3)

Processing Options:
  -w, --ignore-whitespace    Ignore whitespace differences
  --ignore-case              Ignore case differences
  --word-diff                Word-level diff (side-by-side only)

Output Options:
  --no-color           Disable colored output
  -q, --quiet          Quiet mode (exit code only)
  -h, --help           Show help message
```

---

## 🌈 Supported Languages

| Category | Languages |
|----------|-----------|
| **Web** | HTML, CSS, SCSS, JavaScript, TypeScript, PHP |
| **Systems** | C, C++, Rust, Go |
| **Application** | Python, Java, C#, Ruby, Swift, Kotlin |
| **Data** | JSON, YAML, XML, SQL |
| **Shell** | Bash, Shell Script |
| **Docs** | Markdown |

*Auto-detection works based on file extension*

---

## 📊 Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Files are identical |
| `1` | Files differ |
| `2` | Error reading files |

### Script Integration Example
```bash
#!/bin/bash
if python diff_plus.py file1.txt file2.txt -q; then
    echo "✓ Files match - deploying..."
    ./deploy.sh
else
    echo "✗ Files differ - review needed"
    exit 1
fi
```

---

## 🎓 Advanced Examples

### 1. **Full-Featured Comparison**
```bash
python diff_plus.py src/old_api.py src/new_api.py \
  -s \              # Side-by-side view
  -n \              # Show line numbers
  -l python \       # Force Python syntax
  --word-diff       # Highlight word changes
```

### 2. **Minimal Context for Large Files**
```bash
python diff_plus.py large_log_1.txt large_log_2.txt -c 0
# Shows only changed lines, no context
```

### 3. **Case-Insensitive Configuration Check**
```bash
python diff_plus.py Config.ini config.ini --ignore-case -w
# Ignores case and whitespace
```

### 4. **Statistics Pipeline**
```bash
# Get similarity score for automation
python diff_plus.py old.js new.js --stats | grep Similarity
```

### 5. **Batch Comparison**
```bash
# Compare multiple file pairs
for file in *.php; do
    if [ -f "backup/$file" ]; then
        echo "Checking $file..."
        python diff_plus.py "backup/$file" "$file" -q || echo "  ↳ Changed"
    fi
done
```

---

## 🔬 Technical Details

### Architecture
- **Parser**: Python `difflib.SequenceMatcher`
- **Rendering**: Rich library for terminal output
- **Encoding**: Multi-fallback (UTF-8, Latin-1, CP1252, ISO-8859-1)

### Performance
- **Memory**: Line-by-line streaming
- **Speed**: Optimized for files up to 10MB
- **Complexity**: O(n*m) where n,m are file line counts

### Color Scheme
- 🟢 **Green** - Additions
- 🔴 **Red** - Deletions  
- 🟡 **Yellow** - Modifications
- 🔵 **Cyan** - Headers/Metadata
- ⚪ **Dim** - Line numbers

---

## 🤝 Contributing

Contributions are welcome! Here are some ideas:

- [ ] Add directory comparison mode
- [ ] Export to HTML/PDF
- [ ] Git integration
- [ ] Custom color themes
- [ ] Search within diff
- [ ] Bookmark changes

---

## 📝 License

MIT License - feel free to use in your projects!

---

## 🙏 Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) - Amazing terminal formatting
- Inspired by classic `diff`, `git diff`, and modern diff tools

---

## 📬 Support

Found a bug? Have a feature request?
- Open an issue
- Submit a pull request
- Share your use case!

---

<div align="center">

**Made with ❤️ for developers who love beautiful diffs**

⭐ Star this repo if you find it useful!

[↑ Back to Top](#-advanced-diff-tool)

</div>
