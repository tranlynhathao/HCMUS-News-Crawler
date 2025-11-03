from bs4 import BeautifulSoup as bs
import requests
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
import logging

from .config import config, ProgramType
from .models import NewsItem, NewsSection, CrawlerReport
from .utils import setup_logging, create_session, safe_request, clean_text, normalize_url


class NewsCrawler:

    def __init__(self, program_type: ProgramType = ProgramType.APCS):
        self.logger = setup_logging()
        self.session = create_session()
        self.report_errors = []
        self.program_type = program_type
        # Update config program type
        config.program_type = program_type

    def crawl_ctda(self) -> NewsSection:
        try:
            page = requests.get(config.ctda_url, headers=config.headers, timeout=config.timeout)
            soup = bs(page.content, features="lxml")
            sections = soup.find_all(class_="display-posts-listing")[:4]

            all_items = []
            for i, section in enumerate(sections):
                if i >= len(config.ctda_section_titles):
                    break

                try:
                    news_elements = section.find_all(class_="listing-item")
                    for element in news_elements:
                        try:
                            link_element = element.contents[0]
                            title = clean_text(link_element.text)
                            url = link_element.attrs.get("href", "")
                            date = (
                                clean_text(element.contents[-1].text)
                                if len(element.contents) > 1
                                else ""
                            )

                            if title and url:
                                all_items.append(
                                    NewsItem(
                                        title=title,
                                        url=url,
                                        date=date,
                                        category=config.ctda_section_titles[i],
                                    )
                                )
                        except (IndexError, KeyError, AttributeError):
                            continue
                except Exception:
                    continue

            return NewsSection("APCS", all_items)

        except Exception as e:
            self.logger.warning(f"Error crawling CTDA: {str(e)}")
            return NewsSection("APCS", [], f"Error loading APCS news: {str(e)}")

    def crawl_fit(self) -> NewsSection:
        try:
            page = requests.get(config.fit_url, headers=config.headers, timeout=config.timeout)
            soup = bs(page.content, features="lxml")
            news_raw = soup.select("#dnn_ctr989_ModuleContent > table")

            items = []
            for news in news_raw:
                try:
                    day = news.select_one("tr:first-child > .day_month").text.strip()
                    month = news.select_one("tr:last-child > .day_month").text.strip()
                    year = news.select_one(".post_year").text.strip()
                    title = news.select_one("a").text.strip()
                    href = news.select_one("a").attrs["href"]

                    if title and href:
                        full_url = f"https://www.fit.hcmus.edu.vn/vn/{href}"
                        date = f"{day}-{month}-{year}"
                        items.append(NewsItem(title=title, url=full_url, date=date))

                except (AttributeError, KeyError):
                    continue

            return NewsSection("FIT", items)

        except Exception as e:
            self.logger.warning(f"Error crawling FIT: {str(e)}")
            return NewsSection("FIT", [], f"Error loading FIT news: {str(e)}")

    def crawl_hcmus(self) -> NewsSection:
        try:
            page = safe_request(self.session, config.hcmus_url, self.logger)

            if not page:
                return NewsSection("Student Information", [], "Failed to load HCMUS news")

            soup = bs(page.content, features="xml")
            items_elements = soup.find_all("item")

            items = []
            for item_element in items_elements:
                try:
                    title_element = item_element.find("title")
                    link_element = item_element.find("link")
                    pub_date_element = item_element.find("pubDate")

                    if not all([title_element, link_element, pub_date_element]):
                        continue

                    title = clean_text(title_element.text)
                    link = clean_text(link_element.text)
                    pub_date = clean_text(pub_date_element.text)

                    if title and link and pub_date:
                        try:
                            date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                            formatted_date = date_obj.strftime("%d/%m/%Y")
                        except ValueError:
                            formatted_date = pub_date

                        items.append(NewsItem(title=title, url=link, date=formatted_date))

                except (AttributeError, ValueError):
                    continue

            return NewsSection("Student Information", items)

        except Exception as e:
            return NewsSection("Student Information", [], f"Error loading HCMUS news: {str(e)}")

    def crawl_old_hcmus(self) -> NewsSection:
        try:
            page = requests.get(
                config.old_hcmus_url, headers=config.headers, timeout=config.timeout
            )
            soup = bs(page.content, features="lxml")

            ctkt_elements = soup.find_all(class_="feed-link")
            items = []
            rule_position = [5, 10, 13]

            for i, news_element in enumerate(ctkt_elements):
                try:
                    title_text = re.sub(r"(\t|\n)", "", news_element.text)
                    title = title_text.strip()

                    link_match = re.findall('http.*" ', str(news_element))
                    link = link_match[0][:-2] if link_match else ""  # [:-2] để loại bỏ '" '

                    if title and link:
                        category = "Important" if i in rule_position else None
                        items.append(NewsItem(title=title, url=link, date="", category=category))

                except (AttributeError, TypeError, IndexError):
                    continue

            return NewsSection("Exam Announcements", items)

        except Exception as e:
            self.logger.warning(f"Error crawling old HCMUS: {str(e)}")
            return NewsSection(
                "Exam Announcements", [], f"Error loading exam announcements: {str(e)}"
            )

    def _crawl_rss_feed(
        self, url: str, section_title: str, keywords: List[str] = None
    ) -> NewsSection:
        """Generic method to crawl RSS feeds with optional keyword filtering"""
        try:
            page = safe_request(self.session, url, self.logger)

            if not page:
                return NewsSection(section_title, [], f"Failed to load {section_title}")

            soup = bs(page.content, features="xml")
            items_elements = soup.find_all("item")

            items = []
            for item_element in items_elements:
                try:
                    title_element = item_element.find("title")
                    link_element = item_element.find("link")
                    pub_date_element = item_element.find("pubDate")
                    description_element = item_element.find("description")

                    if not all([title_element, link_element, pub_date_element]):
                        continue

                    title = clean_text(title_element.text)
                    link = clean_text(link_element.text)
                    pub_date = clean_text(pub_date_element.text)
                    description = (
                        clean_text(description_element.text) if description_element else ""
                    )

                    # Cải thiện keyword filtering cho Khoa CNTT
                    if keywords:
                        content_to_check = f"{title} {description}".lower()
                        # Kiểm tra xem có chứa bất kỳ keyword nào không
                        has_keyword = any(
                            keyword.lower() in content_to_check for keyword in keywords
                        )
                        if not has_keyword:
                            continue

                    if title and link and pub_date:
                        try:
                            date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                            formatted_date = date_obj.strftime("%d/%m/%Y")
                        except ValueError:
                            formatted_date = pub_date

                        items.append(NewsItem(title=title, url=link, date=formatted_date))

                except (AttributeError, ValueError):
                    continue

            return NewsSection(section_title, items)

        except Exception as e:
            return NewsSection(section_title, [], f"Error loading {section_title}: {str(e)}")

    def crawl_standard_course_info(self) -> NewsSection:
        """Crawl thông tin môn học cho chương trình chuẩn"""
        return self._crawl_rss_feed(
            config.main_feed_url,
            config.standard_section_titles["course_info"],
            config.standard_keywords["course_info"],
        )

    def crawl_standard_talented_bachelor(self) -> NewsSection:
        """Crawl cử nhân tài năng cho chương trình chuẩn"""
        return self._crawl_rss_feed(
            config.main_feed_url,
            config.standard_section_titles["talented_bachelor"],
            config.standard_keywords["talented_bachelor"],
        )

    def crawl_standard_ai(self) -> NewsSection:
        """Crawl trí tuệ nhân tạo cho chương trình chuẩn"""
        return self._crawl_rss_feed(
            config.main_feed_url,
            config.standard_section_titles["ai"],
            config.standard_keywords["ai"],
        )

    def crawl_standard_course_chain(self) -> NewsSection:
        """Crawl chuỗi môn học cho chương trình chuẩn"""
        return self._crawl_rss_feed(
            config.main_feed_url,
            config.standard_section_titles["course_chain"],
            config.standard_keywords["course_chain"],
        )

    def crawl_clc(self) -> NewsSection:
        """Crawl chương trình chất lượng cao (CLC)"""
        return self._crawl_rss_feed(
            config.main_feed_url, "Chất lượng cao (CLC)", config.clc_keywords
        )

    def generate_report(self) -> CrawlerReport:
        """Generate report based on program type"""
        sections = []

        if self.program_type == ProgramType.APCS:
            # APCS sections
            sections = [
                self.crawl_ctda(),
                self.crawl_fit(),
                self.crawl_hcmus(),
                self.crawl_old_hcmus(),
            ]
        elif self.program_type == ProgramType.STANDARD:
            # Standard program sections
            sections = [
                self.crawl_standard_course_info(),
                self.crawl_standard_talented_bachelor(),
                self.crawl_standard_ai(),
                self.crawl_standard_course_chain(),
                self.crawl_hcmus(),  # General student info
                self.crawl_old_hcmus(),  # Exam announcements
            ]
        elif self.program_type == ProgramType.CLC:
            # CLC sections
            sections = [
                self.crawl_clc(),
                self.crawl_hcmus(),  # General student info
                self.crawl_old_hcmus(),  # Exam announcements
            ]

        timestamp = datetime.now(tz=ZoneInfo(config.timezone))

        section_errors = []
        for section in sections:
            if section.has_errors():
                section_errors.append(f"{section.title}: {section.error_message}")

        report = CrawlerReport(
            sections=sections, timestamp=timestamp, errors=section_errors + self.report_errors
        )

        return report

    def save_report(self, report: CrawlerReport) -> bool:
        try:
            output_filename = config.get_output_filename()
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(report.to_markdown())
            self.logger.info(f"Report saved to {output_filename}")
            return True
        except IOError as e:
            self.logger.error(f"Failed to save report: {str(e)}")
            return False
