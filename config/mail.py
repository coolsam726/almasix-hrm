"""Mailers and from address."""

from almasix.config import env

config = {
    "default": env("MAIL_MAILER", "log"),
    "from": {
        "address": env("MAIL_FROM_ADDRESS", "hr@northwind.test"),
        "name": env("MAIL_FROM_NAME", "Almasix HRM"),
    },
    "mailers": {
        "log": {"transport": "log"},
        "array": {"transport": "array"},
    },
}
