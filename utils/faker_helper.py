"""
Utility functions for generating unique random data for tests.

Key QA Concepts Implemented:
- Test Data Management: Centralizes generation logic to ensure data consistency.
- Parallelism Safety: Uses UUID suffixes to ensure zero collisions when tests run concurrently on multiple workers.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import List

from faker import Faker

faker = Faker()


def _unique_suffix() -> str:
    """Return a short unique suffix derived from a UUID to prevent data collisions."""
    return uuid.uuid4().hex[:8]


def random_username() -> str:
    """Return a random username with a unique suffix."""
    return f"{faker.user_name()}_{_unique_suffix()}"


def random_email() -> str:
    """Return a random email address with a unique suffix."""
    return f"{faker.user_name()}.{_unique_suffix()}@example.com"


def random_password(min_length: int = 12) -> str:
    """Return a random secure password."""
    return faker.password(length=max(min_length, 12), special_chars=True)


@dataclass
class ArticleData:
    """Data Transfer Object (DTO) for article fields."""
    title: str
    description: str
    body: str
    tags: List[str]


def random_article(title_prefix: str = "") -> ArticleData:
    """
    Returns a randomly generated article object.

    QA Concept - Data Independence:
    Appends a unique suffix to the title to prevent slug collisions in the backend,
    which often cause 422 or 500 errors during parallel test execution.
    """
    base_title = title_prefix or faker.sentence(nb_words=4).rstrip(".")
    unique_title = f"{base_title}_{_unique_suffix()}"

    return ArticleData(
        title=unique_title,
        description=faker.sentence(nb_words=10),
        body="\n\n".join(faker.paragraphs(nb=3)),
        tags=[faker.word() for _ in range(3)]
    )