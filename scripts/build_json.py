#!/usr/bin/env python3
"""
Parse all MkDocs markdown files into structured JSON for the WeChat Mini Program.
Outputs: docs/assets/data/version.json, departments.json, courses.json
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
OUTPUT_DIR = DOCS_DIR / "assets" / "data"

# Department metadata from mkdocs.yml nav
DEPARTMENTS = [
    {"id": "bus", "code": "BUS", "name": "商学系", "nameEn": "Business"},
    {"id": "chi", "code": "CHI", "name": "中文系", "nameEn": "Chinese"},
    {"id": "comp", "code": "COMP", "name": "计算机系", "nameEn": "Computer Science"},
    {"id": "econ", "code": "ECON", "name": "经济系", "nameEn": "Economics"},
    {"id": "eng", "code": "ENG", "name": "英文系", "nameEn": "English"},
    {"id": "fin", "code": "FIN", "name": "金融系", "nameEn": "Finance"},
    {"id": "fren", "code": "FREN", "name": "法语系", "nameEn": "French"},
    {"id": "hist", "code": "HIST", "name": "历史系", "nameEn": "History"},
    {"id": "jour", "code": "JOUR", "name": "新传系", "nameEn": "Journalism"},
    {"id": "law", "code": "LAW", "name": "法律系", "nameEn": "Law"},
    {"id": "mdit", "code": "MDIT", "name": "媒体设计与虚拟现实科技", "nameEn": "Media Design & IT"},
    {"id": "pe", "code": "PE", "name": "体育", "nameEn": "Physical Education"},
    {"id": "phil", "code": "PHIL", "name": "哲学系", "nameEn": "Philosophy"},
    {"id": "pra", "code": "PRA", "name": "公共关系与广告", "nameEn": "PR & Advertising"},
    {"id": "soc", "code": "SOC", "name": "社会系", "nameEn": "Sociology"},
]

GE_CATEGORIES = [
    {"id": "gea", "code": "GEA", "name": "通识课 A 类", "nameEn": "GE Category A", "parent": "ge"},
    {"id": "geb", "code": "GEB", "name": "通识课 B 类", "nameEn": "GE Category B", "parent": "ge"},
    {"id": "gec", "code": "GEC", "name": "通识课 C 类", "nameEn": "GE Category C", "parent": "ge"},
    {"id": "ged", "code": "GED", "name": "通识课 D 类", "nameEn": "GE Category D", "parent": "ge"},
]


def parse_rating(rating_str: str) -> float | None:
    """Extract numeric rating from strings like '★★★★ (4 / 5)' or 'N/A'"""
    if not rating_str or rating_str.strip() == "N/A":
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*5", rating_str)
    if match:
        return float(match.group(1))
    return None


def parse_update_time(content: str) -> str | None:
    """Extract update time from gb-update-time div"""
    match = re.search(r'<div class="gb-update-time">最后更新于：(.+?)</div>', content)
    if match:
        return match.group(1).strip()
    return None


def parse_department_index(md_path: Path) -> list[dict]:
    """Parse department index page to get course list with ratings"""
    content = md_path.read_text(encoding="utf-8")
    courses = []

    # Find table rows: | CODE | [Name](link) | Chinese | Teacher | Rating |
    rows = re.findall(
        r"\|\s*([A-Z]{2,4}\d{2,4})\s*\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
        content,
    )
    for code, name, link, name_cn, teacher, rating in rows:
        course_id = Path(link).stem.lower()
        courses.append(
            {
                "id": course_id,
                "code": code.strip(),
                "name": name.strip(),
                "nameCn": name_cn.strip(),
                "teacher": teacher.strip(),
                "rating": parse_rating(rating),
            }
        )
    return courses


def parse_course_detail(md_path: Path) -> dict | None:
    """Parse a course detail page into structured data"""
    content = md_path.read_text(encoding="utf-8")
    course_id = md_path.stem.lower()

    # Extract title
    title_match = re.match(r"#\s+(.+)", content)
    if not title_match:
        return None

    # Extract update time
    last_updated = parse_update_time(content)

    # Extract basic info table
    info = {}
    info_section = re.search(r"## 课程基本信息\s*\n((?:\|.+\|\n?)+)", content)
    if info_section:
        for row in info_section.group(1).strip().split("\n"):
            cells = [c.strip() for c in row.split("|") if c.strip()]
            if len(cells) >= 2 and cells[0] != "字段":
                info[cells[0]] = cells[1]

    # Extract stats table
    stats = {"reviewCount": 0, "avgRating": None, "sd": None, "note": None}
    stats_section = re.search(r"## 综合信息\s*\n((?:\|.+\|\n?)+)", content)
    if stats_section:
        stats_text = stats_section.group(1)
        # Review count
        count_match = re.search(r"\|\s*(\d+)\s*\|", stats_text)
        if count_match:
            stats["reviewCount"] = int(count_match.group(1))

        # Check for multi-teacher note
        if "综合评分不适用" in stats_text:
            stats["note"] = "因存在多位老师，综合评分不适用"
        else:
            # Average rating
            rating_match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*5", stats_text)
            if rating_match:
                stats["avgRating"] = float(rating_match.group(1))

            # SD
            if "NaN" in stats_text:
                stats["sd"] = None
            else:
                sd_match = re.search(r"\|\s*(\d+(?:\.\d+)?)\s*\|", stats_text.split("\n")[0])
                # SD is in the third column - try a different approach
                sd_rows = stats_text.strip().split("\n")
                if len(sd_rows) >= 2:
                    sd_cells = [c.strip() for c in sd_rows[1].split("|") if c.strip()]
                    if len(sd_cells) >= 3:
                        sd_val = re.search(r"(\d+(?:\.\d+)?)", sd_cells[2])
                        if sd_val:
                            stats["sd"] = float(sd_val.group(1))

    # Extract reviews
    reviews = []
    review_sections = re.finditer(
        r"###\s+(\d{4}/\d{2}/\d{2})\s*\n(<div class=\"review-card\">.*?)((?=###\s+\d{4}/\d{2}/\d{2})|$)",
        content,
        re.DOTALL,
    )
    for match in review_sections:
        date_str = match.group(1)
        review_html = match.group(2)

        review = {
            "date": date_str.replace("/", "-"),
            "reviewer": None,
            "grade": None,
            "rating": None,
            "teacher": None,
            "content": None,
        }

        # Extract meta fields
        meta_rows = re.findall(
            r'<td class="meta-label">([^<]+)</td>\s*<td>([^<]+)</td>', review_html
        )
        for label, value in meta_rows:
            label = label.strip()
            value = value.strip()
            if label == "评价人":
                review["reviewer"] = value
            elif label == "授课老师":
                review["teacher"] = value
            elif label == "成绩":
                review["grade"] = value
            elif label == "总体评价":
                review["rating"] = parse_rating(value)

        # Extract review content - grab text between review-content div tags
        content_match = re.search(
            r'<div class="review-content">\s*\n(.*?)\n\s*</div>', review_html, re.DOTALL
        )
        if content_match:
            review["content"] = content_match.group(1).strip()

        reviews.append(review)

    return {
        "id": course_id,
        "code": info.get("课程编号", md_path.stem.upper()),
        "name": info.get("课程名称", ""),
        "nameCn": info.get("中文名称", ""),
        "type": info.get("所属类型", ""),
        "teacher": info.get("任课老师", ""),
        "language": info.get("老师上课使用的语言", ""),
        "lastUpdated": last_updated,
        "stats": stats,
        "reviews": reviews,
    }


def build_data():
    """Build all JSON data files"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_departments = []
    all_courses = []

    # Process regular departments
    for dept in DEPARTMENTS:
        dept_dir = DOCS_DIR / dept["id"]
        index_path = dept_dir / "index.md"

        if not index_path.exists():
            print(f"Warning: {index_path} not found, skipping")
            continue

        course_summaries = parse_department_index(index_path)
        last_updated = parse_update_time(index_path.read_text(encoding="utf-8"))

        dept_entry = {
            "id": dept["id"],
            "code": dept["code"],
            "name": dept["name"],
            "nameEn": dept["nameEn"],
            "parent": None,
            "courseCount": len(course_summaries),
            "lastUpdated": last_updated,
            "courses": course_summaries,
        }
        all_departments.append(dept_entry)

        # Process course files
        for md_file in sorted(dept_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            course = parse_course_detail(md_file)
            if course:
                course["departmentId"] = dept["id"]
                all_courses.append(course)

    # Add GE parent entry
    ge_entry = {
        "id": "ge",
        "code": "GE",
        "name": "通识课",
        "nameEn": "General Education",
        "parent": None,
        "courseCount": 0,
        "lastUpdated": None,
        "courses": [],
    }
    all_departments.append(ge_entry)

    # Process GE subcategories
    for ge_cat in GE_CATEGORIES:
        cat_dir = DOCS_DIR / "ge" / ge_cat["id"]
        index_path = cat_dir / "index.md"

        if not index_path.exists():
            print(f"Warning: {index_path} not found, skipping")
            continue

        course_summaries = parse_department_index(index_path)
        last_updated = parse_update_time(index_path.read_text(encoding="utf-8"))

        cat_entry = {
            "id": ge_cat["id"],
            "code": ge_cat["code"],
            "name": ge_cat["name"],
            "nameEn": ge_cat["nameEn"],
            "parent": ge_cat["parent"],
            "courseCount": len(course_summaries),
            "lastUpdated": last_updated,
            "courses": course_summaries,
        }
        all_departments.append(cat_entry)

        # Update GE parent course count
        ge_entry["courseCount"] += len(course_summaries)

        # Process GE course files
        for md_file in sorted(cat_dir.glob("*.md")):
            if md_file.name == "index.md":
                continue
            course = parse_course_detail(md_file)
            if course:
                course["departmentId"] = ge_cat["id"]
                all_courses.append(course)

    # Sort departments: regular first, then GE
    all_departments.sort(key=lambda d: (d["parent"] is not None, d["code"]))

    # Generate version
    version = datetime.now(timezone.utc).strftime("%Y%m%d01")
    version_data = {
        "version": version,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "courseCount": len(all_courses),
        "departmentCount": len(all_departments),
    }

    # Write output files
    (OUTPUT_DIR / "version.json").write_text(
        json.dumps(version_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUTPUT_DIR / "departments.json").write_text(
        json.dumps({"departments": all_departments}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "courses.json").write_text(
        json.dumps({"courses": all_courses}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Generated data for {len(all_departments)} departments, {len(all_courses)} courses")
    print(f"Output: {OUTPUT_DIR}")
    print(f"  version.json")
    print(f"  departments.json")
    print(f"  courses.json")


if __name__ == "__main__":
    build_data()
