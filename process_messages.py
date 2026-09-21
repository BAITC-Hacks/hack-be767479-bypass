"""Classify student requests from messages.txt and print response drafts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CATEGORIES = ("справка", "жалоба", "другое")

CLASSIFICATION_RULES = {
    "жалоба": (
        "очеред",
        "холодн",
        "пропал",
        "не работает",
        "проблем",
        "wi-fi",
        "wifi",
    ),
    "справка": (
        "справк",
        "где",
        "как получить",
        "парковк",
        "расположен",
        "адрес",
        "куда",
    ),
}

REPLY_TEMPLATES = {
    "справка": {
        "справк": (
            "Справку о месте учёбы можно заказать в учебном офисе или через "
            "личный кабинет. Возьмите с собой удостоверение личности."
        ),
        "парковк": (
            "Гостевая парковка расположена у главного входа. Пожалуйста, "
            "уточните на посту охраны доступные места."
        ),
        "где": "Спасибо за вопрос. Подскажем, где это находится, и уточним детали по обращению.",
    },
    "жалоба": {
        "wi-fi": (
            "Спасибо за сообщение. Передадим информацию технической службе "
            "для проверки Wi‑Fi в корпусе B."
        ),
        "столов": (
            "Спасибо за сообщение. Передадим жалобу администрации столовой "
            "для проверки очередей и качества блюд."
        ),
        "очеред": "Спасибо за сообщение. Передадим информацию ответственным сотрудникам для проверки очереди.",
        "холодн": "Спасибо за сообщение. Передадим жалобу в столовую и уточним, как улучшить качество питания.",
        "пропал": "Спасибо за сообщение. Передадим информацию ответственным службам для проверки.",
    },
    "другое": {
        "консультац": (
            "Записаться на консультацию на завтра можно через преподавателя "
            "или учебный офис. Уточните, пожалуйста, предмет и удобное время."
        )
    },
}

DEFAULT_REPLIES = {
    "справка": "Спасибо за вопрос. Уточним информацию и поможем с дальнейшими шагами.",
    "жалоба": "Спасибо за сообщение. Передадим его ответственным сотрудникам для проверки.",
    "другое": "Спасибо за обращение. Уточните, пожалуйста, детали, чтобы мы могли помочь.",
}


def normalize_text(value: str) -> str:
    """Normalize whitespace, case, and Wi‑Fi variants for classification."""
    text = value.strip()
    if not text:
        return ""

    text = (
        text.replace("\u2011", "-")
        .replace("\u2010", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("−", "-")
        .replace("ё", "е")
        .lower()
    )
    text = text.replace("wi-fi", "wi-fi").replace("wifi", "wi-fi")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify(message: str) -> str:
    """Return one of: справка, жалоба, другое."""
    text = normalize_text(message)
    if any(word in text for word in CLASSIFICATION_RULES["жалоба"]):
        return "жалоба"
    if any(word in text for word in CLASSIFICATION_RULES["справка"]):
        return "справка"
    return "другое"


def draft_reply(category: str, message: str) -> str:
    """Prepare a concise Russian reply, tailored to the request when possible."""
    normalized = normalize_text(message)
    templates = REPLY_TEMPLATES.get(category, {})
    for key, template in templates.items():
        if key in normalized:
            return template
    return DEFAULT_REPLIES.get(category, DEFAULT_REPLIES["другое"])


def load_messages(path: Path) -> list[str]:
    """Read messages.txt and validate that it contains exactly five non-empty messages."""
    if not path.exists():
        raise FileNotFoundError(f"Файл {path.name} не найден: {path}")

    raw_lines = path.read_text(encoding="utf-8").splitlines()
    messages = [normalize_text(line) for line in raw_lines if line.strip()]
    if len(messages) != 5:
        raise ValueError(
            f"В файле {path.name} должно быть ровно 5 непустых сообщений, "
            f"найдено: {len(messages)}."
        )
    return messages


def review_result(category: str, reply: str) -> tuple[bool, list[str]]:
    """Run a lightweight quality review for category validity and reply format."""
    issues: list[str] = []
    if category not in CATEGORIES:
        issues.append(f"Категория {category!r} не входит в разрешённый список: {', '.join(CATEGORIES)}.")
    if not reply or not reply.strip():
        issues.append("Ответ пустой.")
    if not re.search(r"[а-яё]", reply.lower()):
        issues.append("Ответ должен быть написан по-русски.")
    return (not issues), issues


def main() -> None:
    # Windows terminals may default to a legacy code page without Cyrillic.
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Обработка обращений студентов.")
    parser.add_argument(
        "--file",
        type=Path,
        default=Path(__file__).with_name("messages.txt"),
        help="Путь к файлу с сообщениями.",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Проверить, что категория допустима и ответ сформирован корректно.",
    )
    args = parser.parse_args()

    try:
        messages = load_messages(args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        raise SystemExit(1)

    for number, message in enumerate(messages, start=1):
        category = classify(message)
        reply = draft_reply(category, message)
        print(f"{number}. Обращение: {message}")
        print(f"   Категория: {category}")
        print(f"   Черновик ответа: {reply}")

        if args.review:
            ok, issues = review_result(category, reply)
            status = "OK" if ok else "FAIL"
            print(f"   Проверка качества: {status}")
            if issues:
                print(f"   Проблемы: {'; '.join(issues)}")
        print()


if __name__ == "__main__":
    main()
