"""Database seeder entrypoint."""

from __future__ import annotations

from almasix.orm import Seeder

from database.seeders.company_seeder import CompanySeeder


class DatabaseSeeder(Seeder):
    async def run(self) -> None:
        await self.call([CompanySeeder])
