from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class ProgramType(Enum):
    APCS = "apcs"
    STANDARD = "standard"
    CLC = "clc"


@dataclass
class CrawlerConfig:
    # URLs cho các chương trình
    ctda_url: str = "https://www.ctda.hcmus.edu.vn/vi/"  # APCS
    fit_url: str = "https://www.fit.hcmus.edu.vn/vn/"
    hcmus_url: str = (
        "https://hcmus.edu.vn/category/dao-tao/dai-hoc/thong-tin-danh-cho-sinh-vien/feed/"
    )
    old_hcmus_url: str = "https://old.hcmus.edu.vn/sinh-vien"

    # URLs cho chương trình chuẩn (fallback to main feeds vì specific feeds trống)
    main_feed_url: str = "https://hcmus.edu.vn/feed/"  # Main news feed

    # Keywords để filter nội dung cho từng chương trình
    standard_keywords: Dict[str, List[str]] = None
    clc_keywords: List[str] = None

    ctda_section_titles: List[str] = None

    # Section titles cho các chương trình
    standard_section_titles: Dict[str, str] = None
    program_type: ProgramType = ProgramType.APCS

    timeout: int = 15
    max_retries: int = 3
    retry_delay: float = 1.0

    output_file: str = "NEWS-APCS.md"
    timezone: str = "Asia/Ho_Chi_Minh"

    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
    )

    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "crawler.log"

    headers: dict = None

    def __post_init__(self):
        if self.ctda_section_titles is None:
            self.ctda_section_titles = [
                "Academic Planning",
                "Academic Affairs",
                "Student Support",
                "Accounting & Finance",
            ]

        if self.standard_section_titles is None:
            self.standard_section_titles = {
                "course_info": "Thông tin môn học",
                "talented_bachelor": "Cử nhân tài năng",
                "ai": "Trí tuệ nhân tạo",
                "course_chain": "Chuỗi môn học",
            }

        if self.standard_keywords is None:
            self.standard_keywords = {
                "course_info": [
                    "môn học",
                    "học phần",
                    "chương trình học",
                    "giáo trình",
                    "kỳ học",
                    "công nghệ thông tin",
                    "khoa cntt",
                    "computer science",
                    "IT",
                    "lập trình",
                    "cơ sở dữ liệu",
                    "mạng máy tính",
                    "phần mềm",
                ],
                "talented_bachelor": [
                    "cử nhân tài năng",
                    "học bổng",
                    "thầy cô ưu tú",
                    "sinh viên giỏi",
                    "công nghệ thông tin",
                    "khoa cntt",
                    "computer science",
                    "IT",
                    "tài năng cntt",
                    "ưu tú cntt",
                ],
                "ai": [
                    "trí tuệ nhân tạo",
                    "AI",
                    "machine learning",
                    "deep learning",
                    "công nghệ 4.0",
                    "công nghệ thông tin",
                    "khoa cntt",
                    "computer science",
                    "IT",
                    "data science",
                    "big data",
                    "neural network",
                    "automation",
                ],
                "course_chain": [
                    "chuỗi môn học",
                    "liên kết môn",
                    "tích hợp",
                    "liên ngành",
                    "công nghệ thông tin",
                    "khoa cntt",
                    "computer science",
                    "IT",
                ],
            }

        if self.clc_keywords is None:
            self.clc_keywords = [
                "chất lượng cao",
                "CLC",
                "chương trình CLC",
                "high quality",
                "advanced program",
                "tốt nghiệp",
                "xuất sắc",
                "học bổng",
                "quốc tế",
                "hợp tác",
                "tiên tiến",
                "chất lượng",
                # Thêm keywords cụ thể cho Khoa CNTT
                "công nghệ thông tin",
                "khoa cntt",
                "computer science",
                "IT",
                "CLC CNTT",
                "CLC IT",
                "advanced IT",
                "IT program",
                "lập trình nâng cao",
                "công nghệ phần mềm",
                "hệ thống thông tin",
                "kỹ thuật phần mềm",
                "khoa học máy tính",
                "trí tuệ nhân tạo",
            ]

        if self.headers is None:
            self.headers = {"User-Agent": self.user_agent}

    def get_output_filename(self) -> str:
        """Get output filename based on program type"""
        filename_map = {
            ProgramType.APCS: "NEWS-APCS.md",
            ProgramType.STANDARD: "NEWS-STANDARD.md",
            ProgramType.CLC: "NEWS-CLC.md",
        }
        return filename_map.get(self.program_type, self.output_file)


config = CrawlerConfig()
