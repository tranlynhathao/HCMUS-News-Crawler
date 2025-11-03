"""Main entry point for the HCMUS News Crawler package."""

import argparse
from .crawler import NewsCrawler
from .config import ProgramType, config


def main():
    """Main function to run the news crawler - đơn giản hóa theo tính thần tnapcs_crawler."""
    parser = argparse.ArgumentParser(
        description="HCMUS News Crawler - Crawl tin tức CNTT từ HCMUS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Các chương trình hỗ trợ:
  apcs     - APCS (Advanced Program in Computer Science)
  standard - Chương trình chuẩn CNTT (có keyword filtering)
  clc      - Chương trình chất lượng cao CNTT

Ví dụ sử dụng:
  python -m hcmus_crawler --program standard
  python -m hcmus_crawler -p clc -v

Output:
  NEWS-APCS.md, NEWS-STANDARD.md, NEWS-CLC.md
""",
    )

    parser.add_argument(
        "-p",
        "--program",
        type=str,
        choices=["apcs", "standard", "clc"],
        default="apcs",
        help="Chọn chương trình để crawl (mặc định: apcs)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Hiển thị thông tin chi tiết khi crawl"
    )

    args = parser.parse_args()

    # Map program types
    program_type_map = {
        "apcs": ProgramType.APCS,
        "standard": ProgramType.STANDARD,
        "clc": ProgramType.CLC,
    }

    program_type = program_type_map[args.program]

    print(f"Crawling {args.program.upper()} news from HCMUS...")
    if args.verbose:
        print(f"Nguồn: CTDA, FIT, HCMUS main feeds")
        print(f"Filtering: Chỉ tin tức Khoa CNTT")

    try:
        crawler = NewsCrawler(program_type=program_type)
        report = crawler.generate_report()

        # Hiển thị thống kê nhanh
        if args.verbose:
            total_items = sum(len(section.items) for section in report.sections)
            print(f"Đã crawl {total_items} tin tức từ {len(report.sections)} nguồn")

        success = crawler.save_report(report)

        if success:
            filename = config.get_output_filename()
            print(f"Hoàn thành! Kết quả lưu tại: {filename}")
        else:
            print("Lỗi khi lưu báo cáo!")
            exit(1)

    except Exception as e:
        print(f"Lỗi khi crawl: {str(e)}")
        if args.verbose:
            raise
        exit(1)


if __name__ == "__main__":
    main()
