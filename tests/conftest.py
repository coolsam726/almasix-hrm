"""Shared test setup."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

os.environ.setdefault("BCRYPT_ROUNDS", "4")

from almasix.testing import restore_fakes


@pytest.fixture(autouse=True)
def _no_fake_outlives_its_test() -> Iterator[None]:
    yield
    restore_fakes()
