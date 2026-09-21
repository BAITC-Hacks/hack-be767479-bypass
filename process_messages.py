"""Classify student requests from messages.txt and print response drafts."""

from pathlib import Path
import sys


REFERENCE_WORDS = ("справк", "где", "как получить", "парковк")
COMPLAINT_WORDS = ("очеред", "холодн", "пропал", "не работает", "проблем")


def classify(message: str) -> str:
    """Return one of: справка, жалоба, другое."""
    text = message.lower()
    if any(word in text for word in COMPLAINT_WORDS):
        return "жалоба"
    if any(word in text for word in REFERENCE_WORDS):
        return "справка"
    return "другое"


def draft_reply(category: str, message: str) -> str:
    """Prepare a concise Russian reply, tailored to the request when possible."""
    text = message.lower()

    if "справк" in text:
        return (
            "Справку о месте учёбы можно заказать в учебном офисе или через "
            "личный кабинет. Возьмите с собой удостоверение личности."
        )
    if "столов" in text:
        return (
            "Спасибо за сообщение. Передадим жалобу администрации столовой "
            "для проверки очередей и качества блюд."
        )
    if "консультац" in text:
        return (
            "Записаться на консультацию на завтра можно через преподавателя "
            "или учебный офис. Уточните, пожалуйста, предмет и удобное время."
        )
    if "wi-fi" in text or "wifi" in text:
        return (
            "Спасибо за сообщение. Передадим информацию технической службе "
            "для проверки Wi-Fi в корпусе B."
        )
    if "парковк" in text:
        return (
            "Гостевая парковка расположена у главного входа. Пожалуйста, "
            "уточните на посту охраны доступные места."
        )
    if category == "жалоба":
        return "Спасибо за сообщение. Передадим его ответственным сотрудникам для проверки."
    if category == "справка":
        return "Спасибо за вопрос. Уточним информацию и поможем с дальнейшими шагами."
    return "Спасибо за обращение. Уточните, пожалуйста, детали, чтобы мы могли помочь."


def main() -> None:
    # Windows terminals may default to a legacy code page without Cyrillic.
    sys.stdout.reconfigure(encoding="utf-8")
    messages_path = Path(__file__).with_name("messages.txt")
    messages = messages_path.read_text(encoding="utf-8").splitlines()

    for number, message in enumerate(messages, start=1):
        category = classify(message)
        print(f"{number}. Обращение: {message}")
        print(f"   Категория: {category}")
        print(f"   Черновик ответа: {draft_reply(category, message)}\n")


if __name__ == "__main__":
    main()
