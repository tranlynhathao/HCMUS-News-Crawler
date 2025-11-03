# 🎓 HCMUS News Crawler - **Improved & Simplified**

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![BeautifulSoup](https://img.shields.io/badge/beautifulsoup4-4.12.0%2B-green)
![Requests](https://img.shields.io/badge/requests-2.31.0%2B-orange)
![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-improved-success)

**Automation Schedule:**

- **Main Crawler**: Runs every hour (all programs: APCS, Standard, CLC)
- **Intensive Crawler**: Runs every 30 minutes when needed
- **Manual Trigger**: Available via GitHub Actions interface

## News Sources

1. **APCS (CTDA)** - Advanced Program in Computer Science
   - Academic plans, academic affairs, student support, accounting
   - Source: <https://www.ctda.hcmus.edu.vn/vi/>

2. **FIT** - Faculty of Information Technology
   - Department news and announcements
   - Source: <https://www.fit.hcmus.edu.vn/vn/>

3. **HCMUS Main Site** - Student Information
   - General student announcements and updates
   - Source: <https://hcmus.edu.vn/>

4. **Old HCMUS Site** - Exam Announcements
   - Exam schedules and testing information
   - Source: <https://old.hcmus.edu.vn/sinh-vien>

## Supported Programs

### APCS - Advanced Program in Computer Science

- Academic Planning
- Academic Affairs
- Student Support
- Accounting & Finance

### STANDARD - Standard Program

- Course Information
- Talented Bachelor Program
- Artificial Intelligence
- Course Sequences

### CLC - High-Quality Program

- CLC Program News
- General Student Information
- Exam Announcements

## Installation

### Requirements

- Python 3.9 or higher
- pip package manager

### Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:

- `beautifulsoup4>=4.12.0,<5.0.0`
- `requests>=2.31.0,<3.0.0`
- `lxml>=4.9.0,<5.0.0`

### Install Package

```bash
pip install -e .
```

## 🚀 Quick Start (New Simplified Way)

### Method 1: Simple Script (Recommended)

```bash
# APCS program
python crawl.py --program apcs -v

# Standard Computer Science program (with CNTT filtering)
python crawl.py --program standard -v

# CLC program (with CNTT filtering)
python crawl.py --program clc -v
```

### Method 2: Traditional Package Usage

```bash
# Install package first
pip install -e .

# Then use traditional command
hcmus-crawler --program standard -v
```

## Usage (Traditional)

### Basic Syntax

```bash
hcmus-crawler [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-p, --program {apcs,standard,clc}` | Select program to crawl | apcs |
| `-v, --verbose` | Display detailed output | False |
| `-h, --help` | Show help message | - |

### Examples

#### 1. Crawl APCS (default)

```bash
hcmus-crawler
# or
hcmus-crawler --program apcs
```

#### 2. Crawl Standard Program

```bash
hcmus-crawler --program standard
# or
hcmus-crawler -p standard
```

#### 3. Crawl CLC Program

```bash
hcmus-crawler --program clc -v
```

#### 4. Show Help

```bash
hcmus-crawler --help
```

## Output Files

Each program generates its own markdown file:

| Program | Output File |
|---------|-------------|
| APCS | `NEWS-APCS.md` |
| Standard | `NEWS-STANDARD.md` |
| CLC | `NEWS-CLC.md` |

## Automation (GitHub Actions)

### Main Crawler Workflow

- **File**: `.github/workflows/auto-crawl.yml`
- **Schedule**: Every hour (`0 */1 * * *`)
- **Function**: Crawls all programs and commits changes
- **Trigger**: Automatic + Manual

### Intensive Crawler Workflow

- **File**: `.github/workflows/intensive-crawl.yml`
- **Schedule**: Every 30 minutes (`*/30 * * * *`)
- **Function**: Quick updates when needed
- **Condition**: Only runs if no updates in last 30 minutes

### Manual Crawler Workflow

- **File**: `.github/workflows/manual-crawl.yml`
- **Schedule**: Manual trigger only
- **Function**: Selective crawling with options
- **Features**: Choose specific program or all programs

### Workflow Features

- Automatic detection of changes
- Smart commit messages with summary
- Timezone support (Asia/Ho_Chi_Minh)
- Comprehensive logging and reporting
- Error handling and retry logic

## Configuration

### Modify Settings

Edit `src/hcmus_crawler/config.py` to customize:

```python
# Example: Add new URL
main_feed_url: str = "https://hcmus.edu.vn/feed/"

# Example: Modify keywords for filtering
clc_keywords: List[str] = [
    "chất lượng cao", "CLC", "high quality",
    "tốt nghiệp", "học bổng", "quốc tế"
]
```

### Logging

- All operations are logged to `crawler.log`
- Verbose mode provides detailed console output
- GitHub Actions logs available in repository

## Project Structure

```
hcmus-news-crawler/
├── src/
│   └── hcmus_crawler/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py
│       ├── crawler.py
│       ├── models.py
│       └── utils.py
├── .github/
│   └── workflows/
│       ├── auto-crawl.yml
│       ├── intensive-crawl.yml
│       └── manual-crawl.yml
├── NEWS-APCS.md
├── NEWS-STANDARD.md
├── NEWS-CLC.md
├── requirements.txt
├── pyproject.toml
├── USAGE.md
└── README.md
```

## Notes

- Some sections may be empty if no recent updates are available
- The crawler automatically retries on network errors
- Markdown output supports GitHub preview rendering
- All times are in Vietnam timezone (Asia/Ho_Chi_Minh)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Reporting Issues

If you encounter bugs, broken links, or incorrect data extraction, please open an issue in the GitHub repository with:

- Detailed description
- Error logs (if available)
- Steps to reproduce
- Expected vs actual behavior
