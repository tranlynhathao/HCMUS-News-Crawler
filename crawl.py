#!/usr/bin/env python3
"""
Simple runner script for HCMUS News Crawler
Inspired by the simplicity of tnapcs_crawler but with full functionality of the main repo
"""

import sys
import argparse
from hcmus_crawler.crawler import NewsCrawler
from hcmus_crawler.config import ProgramType


def main():
    """Main runner function - đơn giản như tnapcs_crawler nhưng đầy đủ tính năng"""

    parser = argparse.ArgumentParser(
        description="🎓 HCMUS News Crawler for Computer Science Faculty",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quick Examples:
  python crawl.py --program apcs      # APCS program
  python crawl.py --program standard  # Standard CNTT program
  python crawl.py --program clc       # CLC program
  python crawl.py -p standard -v      # With verbose output

Output Files:
  NEWS-APCS.md      → APCS news
  NEWS-STANDARD.md  → Standard program news (CNTT filtered)
  NEWS-CLC.md       → CLC program news (CNTT filtered)

All results are filtered for Computer Science Faculty relevance
        """,
    )

    parser.add_argument(
        "-p",
        "--program",
        type=str,
        choices=["apcs", "standard", "clc"],
        default="apcs",
        help="Program to crawl news for (default: apcs)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed progress information"
    )

    args = parser.parse_args()

    # Program mapping
    programs = {"apcs": ProgramType.APCS, "standard": ProgramType.STANDARD, "clc": ProgramType.CLC}

    # Start crawling
    print(f"Crawling {args.program.upper()} news for HCMUS Computer Science Faculty...")

    if args.verbose:
        print("Sources: CTDA, FIT, HCMUS feeds with CNTT keyword filtering")

    try:
        # Create and run crawler
        crawler = NewsCrawler(program_type=programs[args.program])
        report = crawler.generate_report()

        # Show stats if verbose
        if args.verbose:
            total_items = sum(len(section.items) for section in report.sections)
            error_count = len([s for s in report.sections if s.has_errors()])
            print(f"Found {total_items} news items from {len(report.sections)} sources")
            if error_count > 0:
                print(f"{error_count} sources had errors")

        # Save results
        success = crawler.save_report(report)

        if success:
            filename = f"NEWS-{args.program.upper()}.md"
            print(f"Success! Results saved to: {filename}")
            if args.verbose:
                print(f"Open {filename} to view the crawled news")
        else:
            print("❌ Failed to save report!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error during crawling: {str(e)}")
        if args.verbose:
            import traceback

            print("Full error trace:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
