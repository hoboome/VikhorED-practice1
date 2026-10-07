"""Базовый класс тестов с подготовкой окружения перед каждым тестом."""

import unittest


class FixtureCase(unittest.TestCase):
    """Тест, который перед запуском вызывает метод ``prepare``.

    Используется вместо ``setUp``, чтобы имена методов соответствовали
    PEP8 (snake_case).
    """

    def prepare(self):
        """Подготовить окружение теста (по умолчанию ничего не делает)."""

    def run(self, result=None):
        """Подготовить окружение и выполнить тест."""
        self.prepare()
        return super().run(result)
