"""从固定的公开来源读取真实岗位与本人公开简历。"""

import asyncio
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

JOB_SOURCES = {"palantir": "Palantir", "spotify": "Spotify"}
RESUME_USERS = [
    "thomasdavis",
    "alifeee",
    "nfriend",
    "spidiweb",
    "ianchanning",
    "sshilko",
    "mhite",
    "jorgeas80",
]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"p", "br", "li", "div"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def clean_text(value):
    parser = PlainText()
    parser.feed(str(value or ""))
    text = "".join(parser.parts)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[联系方式已移除]", text)
    text = re.sub(
        r"(?:\+\d{1,3}[ -])?(?:\(\d{2,4}\)|\d{3})[ -]\d{3}[ -]\d{4}", "[联系方式已移除]", text
    )
    return text.strip()


def normalize_resume(data):
    """只保留职业背景字段，不导入联系方式、地址、头像或第三方评价。"""
    basics = data.get("basics", {})
    if not basics.get("name") or not (data.get("work") or data.get("skills")):
        raise ValueError("来源没有可导入的本人职业履历")

    def text(value):
        return clean_text(value)[:20000]

    def description(item):
        return "\n".join(
            filter(
                None, [text(item.get("summary")), *[text(x) for x in item.get("highlights", [])]]
            )
        )

    return {
        "name": text(basics["name"]),
        "summary": text(basics.get("summary")),
        "professional_title": text(basics.get("label")),
        "skills": [
            {"name": text(name)}
            for item in data.get("skills", [])
            for name in ([item.get("name")] + item.get("keywords", []))
            if name
        ],
        "educations": [
            {
                "school": text(item.get("institution")),
                "degree": text(item.get("studyType")),
                "field": text(item.get("area")),
                "start_date": text(item.get("startDate")),
                "end_date": text(item.get("endDate")),
            }
            for item in data.get("education", [])
        ],
        "work_experiences": [
            {
                "company": text(item.get("name") or item.get("company")),
                "title": text(item.get("position")),
                "description": description(item),
                "start_date": text(item.get("startDate")),
                "end_date": text(item.get("endDate")),
                "is_current": not bool(item.get("endDate")),
            }
            for item in data.get("work", [])
        ],
        "projects": [
            {
                "name": text(item.get("name")),
                "description": text(item.get("description")),
                "tech_stack": [text(x) for x in item.get("keywords", [])],
            }
            for item in data.get("projects", [])
        ],
    }


async def fetch_public_jobs():
    records, errors = [], []
    async with httpx.AsyncClient(timeout=35, follow_redirects=True) as client:
        for site, company in JOB_SOURCES.items():
            try:
                response = await client.get(
                    f"https://api.lever.co/v0/postings/{site}", params={"mode": "json", "limit": 30}
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, list):
                    raise ValueError("Invalid jobs response")
                for item in payload[:30]:
                    url = item.get("hostedUrl", "")
                    if urlparse(url).hostname != "jobs.lever.co" or not item.get("text"):
                        continue
                    description = [item.get("descriptionPlain") or item.get("description", "")]
                    for section in item.get("lists", []):
                        description += [section.get("text", ""), section.get("content", "")]
                    description += [item.get("additionalPlain") or item.get("additional", "")]
                    records.append(
                        {
                            "title": clean_text(item["text"])[:255],
                            "company": company,
                            "description": clean_text("\n".join(description)),
                            "location": clean_text(item.get("categories", {}).get("location")),
                            "source_url": url,
                            "source_name": f"{company} · Lever 官方招聘",
                        }
                    )
            except (httpx.HTTPError, ValueError, TypeError):
                errors.append(f"{company} 来源暂时不可用，请稍后重试。")
    return records, errors


async def fetch_public_resumes():
    async with httpx.AsyncClient(timeout=35, follow_redirects=True) as client:
        semaphore = asyncio.Semaphore(4)

        async def fetch(username):
            source = f"https://registry.jsonresume.org/{username}"
            try:
                async with semaphore:
                    response = await client.get(source + ".json")
                response.raise_for_status()
                parsed = normalize_resume(response.json())
                if parsed["name"].lower() in {"richard hendricks", "john doe", "jane doe"}:
                    raise ValueError("Example resume")
                return {
                    "parsed": parsed,
                    "source_url": source,
                    "source_name": "JSON Resume · 本人公开简历",
                }, None
            except (httpx.HTTPError, ValueError, TypeError, KeyError):
                return None, f"{username} 的公开简历暂时不可用。"

        outcomes = await asyncio.gather(*[fetch(username) for username in RESUME_USERS])
    return [item for item, error in outcomes if item], [error for item, error in outcomes if error]
