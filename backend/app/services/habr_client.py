from datetime import datetime
from typing import Any

import httpx

from app.schemas.vacancy import VacancyCreate


class HabrClient:
    BASE_URL = "https://career.habr.com"
    API_URL = "https://career.habr.com/api/frontend/vacancies"

    def __init__(self, cookies: dict[str, str] | None = None):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) "
                "Gecko/20100101 Firefox/148.0"
            ),
            "Accept": "application/json",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://career.habr.com/vacancies",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
        self.cookies = cookies or {}

    @staticmethod
    def _parse_published_at(date_val: str | None) -> datetime | None:
        if not date_val:
            return None
        try:
            return datetime.fromisoformat(date_val.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

    def transform_raw_to_schema(self, item: dict[str, Any]) -> VacancyCreate:
        company = item.get("company") or {}
        pub_date = item.get("publishedDate") or {}
        salary = item.get("salary") or {}
        pred_salary = item.get("predictedSalary") or {}

        s_from = salary.get("from")
        s_to = salary.get("to")
        p_from = pred_salary.get("from")
        p_to = pred_salary.get("to")
        eff_max = s_to or s_from or p_to or p_from

        skills_raw = item.get("skills") or []
        locations_raw = item.get("locations") or []

        skills = [
            str(s["title"]).strip().lower()
            for s in skills_raw
            if isinstance(s, dict) and s.get("title")
        ]
        locations = [
            str(loc["title"]).strip()
            for loc in locations_raw
            if isinstance(loc, dict) and loc.get("title")
        ]

        raw_pub_date = pub_date.get("date")
        published_at = self._parse_published_at(raw_pub_date)

        quick_resp = bool(item.get("quickResponseHref"))
        cover_letter_required = bool(item.get("coverLetterRequired", not quick_resp))

        qualification = item.get("qualification") or (
            item.get("salaryQualification") or {}
        ).get("title")

        return VacancyCreate(
            habr_id=item["id"],
            title=item.get("title", "Без названия"),
            company_title=company.get("title", "Не указана"),
            company_href=company.get("href"),
            is_accredited=bool(company.get("accredited", False)),
            remote_work=bool(item.get("remoteWork", False)),
            relocation=bool(item.get("relocation", False)),
            salary_min=s_from,
            salary_max=s_to,
            salary_currency=salary.get("currency"),
            effective_max_salary=eff_max,
            qualification=str(qualification).lower() if qualification else None,
            skills=skills,
            locations=locations,
            url=f"{self.BASE_URL}{item.get('href', '')}",
            cover_letter_required=cover_letter_required,
            published_at=published_at,
            description_text=item.get("description"),
            raw_payload=item,
        )

    async def fetch_vacancies_page(
        self,
        page: int = 1,
        v_type: str = "suitable",
    ) -> list[VacancyCreate]:
        params = {
            "type": v_type,
            "page": str(page),
        }

        async with httpx.AsyncClient(
            headers=self.headers,
            cookies=self.cookies,
            timeout=15.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(self.API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        raw_list = (
            data.get("list") or data.get("vacancies")
            if isinstance(data, dict)
            else data
        )
        if not raw_list:
            return []

        return [self.transform_raw_to_schema(item) for item in raw_list]
