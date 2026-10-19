from typing import Any, Self

import httpx

from app.core.config import settings
from app.schemas.vacancy import VacancyCreate


class HabrClient:
    BASE_URL = "https://career.habr.com"
    API_URL = "https://career.habr.com/api/frontend/vacancies"

    def __init__(self, cookie_str: str | None = None):
        raw_cookie = cookie_str or settings.HABR_SESSION_COOKIE

        self._headers = {
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

        if raw_cookie:
            self._headers["Cookie"] = raw_cookie.strip()

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> Self:
        self._client = httpx.AsyncClient(
            headers=self._headers,
            timeout=15.0,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def transform_raw_to_schema(self, item: dict[str, Any]) -> VacancyCreate:
        company = item.get("company") or {}
        rating = company.get("rating") or {}
        logo = company.get("logo") or {}
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
        divisions_raw = item.get("divisions") or []

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
        divisions = [
            str(d["title"]).strip()
            for d in divisions_raw
            if isinstance(d, dict) and d.get("title")
        ]

        quick_resp = item.get("quickResponseHref")
        company_href = company.get("href")

        return VacancyCreate(
            habr_id=item["id"],
            title=item.get("title", "Без названия"),
            url=f"{self.BASE_URL}{item.get('href', '')}",
            qualification=item.get("qualification")
            or (item.get("salaryQualification") or {}).get("title"),
            employment=item.get("employment"),
            remote_work=bool(item.get("remoteWork", False)),
            is_marked=bool(item.get("isMarked", False)),
            published_date_raw=pub_date.get("date") or pub_date.get("title"),
            company_id=company.get("id"),
            company_title=company.get("title", "Не указана"),
            company_alias=company.get("alias_name"),
            company_url=f"{self.BASE_URL}{company_href}" if company_href else None,
            company_logo=logo.get("src"),
            is_accredited=bool(company.get("accredited", False)),
            company_rating=rating.get("value"),
            salary_from=s_from,
            salary_to=s_to,
            salary_currency=salary.get("currency"),
            salary_formatted=salary.get("formatted"),
            predicted_salary_from=p_from,
            predicted_salary_to=p_to,
            effective_max_salary=eff_max,
            skills=skills,
            locations=locations,
            divisions=divisions,
            can_quick_response=bool(quick_resp),
            quick_response_href=quick_resp,
            raw_data=item,
        )

    async def fetch_vacancies_page(
        self,
        page: int = 1,
        v_type: str = "suitable",
    ) -> list[VacancyCreate]:
        if self._client is None:
            raise RuntimeError(
                "HabrClient должен использоваться как async context manager: "
                "`async with HabrClient() as client:`"
            )

        params = {
            "type": v_type,
            "page": str(page),
        }

        try:
            response = await self._client.get(self.API_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise httpx.HTTPStatusError(
                f"Хабр вернул {exc.response.status_code} на странице {page}",
                request=exc.request,
                response=exc.response,
            ) from exc

        data = response.json()
        raw_list = (
            data.get("list") or data.get("vacancies")
            if isinstance(data, dict)
            else data
        )
        if not raw_list:
            return []

        return [self.transform_raw_to_schema(item) for item in raw_list]
