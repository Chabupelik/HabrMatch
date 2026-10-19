from collections.abc import Sequence
from functools import cache

from sqlalchemy import and_, desc, inspect, not_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.models.swipe import Swipe
from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyCreate, VacancyFilter


@cache
def _vacancy_columns() -> frozenset[str]:
    mapper = inspect(Vacancy)
    return frozenset(col.key for col in mapper.column_attrs)


class VacancyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_many(self, vacancies: list[VacancyCreate]) -> int:
        if not vacancies:
            return 0

        valid_columns = _vacancy_columns()

        values = []
        for v in vacancies:
            data = v.model_dump(exclude_unset=True)
            filtered = {k: val for k, val in data.items() if k in valid_columns}
            values.append(filtered)

        if not values:
            return 0

        stmt = insert(Vacancy).values(values)

        update_cols = {
            col.name: col
            for col in stmt.excluded
            if col.name not in ("id", "habr_id", "created_at")
        }

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[Vacancy.habr_id], set_=update_cols
        )

        result = await self.session.execute(upsert_stmt)
        rowcount = getattr(result, "rowcount", None)
        return (
            rowcount if isinstance(rowcount, int) and rowcount > 0 else len(vacancies)
        )

    async def get_unseen_for_user(
        self, user_id: int, filters: VacancyFilter
    ) -> Sequence[Vacancy]:
        swiped_exists = (
            select(Swipe.id)
            .where(Swipe.user_id == user_id, Swipe.vacancy_id == Vacancy.id)
            .correlate(Vacancy)
            .exists()
        )

        conditions: list[ColumnElement[bool]] = [not_(swiped_exists)]

        if filters.is_accredited_only:
            conditions.append(Vacancy.is_accredited.is_(True))

        if filters.remote_only:
            conditions.append(Vacancy.remote_work.is_(True))

        if filters.min_salary:
            conditions.append(
                (Vacancy.effective_max_salary >= filters.min_salary)
                | (Vacancy.effective_max_salary.is_(None))
            )

        if filters.qualification and filters.qualification.value != "all":
            conditions.append(Vacancy.qualification == filters.qualification.value)

        if filters.primary_skill:
            conditions.append(Vacancy.skills.contains([filters.primary_skill]))

        if filters.required_skills:
            conditions.append(Vacancy.skills.overlap(filters.required_skills))

        query = (
            select(Vacancy)
            .where(and_(*conditions))
            .order_by(desc(Vacancy.id))
            .limit(filters.limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        stmt = select(Vacancy).where(Vacancy.id == vacancy_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
