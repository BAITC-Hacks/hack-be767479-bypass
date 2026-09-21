import unittest
from pathlib import Path

from process_messages import classify, draft_reply, load_messages, normalize_text


class ProcessMessagesTests(unittest.TestCase):
    def test_normalize_text_cleans_input_variants(self):
        self.assertEqual(normalize_text("  Пропал Wi‑Fi в корпусе B.  \n\n"), "пропал wi-fi в корпусе b.")
        self.assertEqual(normalize_text("  wifi   "), "wi-fi")

    def test_classify_expected_categories(self):
        expected = [
            ("Как получить справку о месте учёбы?", "справка"),
            ("В столовой очередь, еда холодная.", "жалоба"),
            ("Хочу записаться на консультацию завтра.", "другое"),
            ("Пропал Wi‑Fi в корпусе B.", "жалоба"),
            ("Где парковка для гостей?", "справка"),
        ]
        for message, category in expected:
            with self.subTest(message=message):
                self.assertEqual(classify(message), category)

    def test_draft_reply_for_each_category_is_specific_and_non_empty(self):
        samples = [
            ("Как получить справку о месте учёбы?", "справка"),
            ("В столовой очередь, еда холодная.", "жалоба"),
            ("Хочу записаться на консультацию завтра.", "другое"),
            ("Пропал Wi‑Fi в корпусе B.", "жалоба"),
            ("Где парковка для гостей?", "справка"),
        ]
        for message, category in samples:
            with self.subTest(message=message):
                reply = draft_reply(category, message)
                self.assertTrue(reply)
                self.assertRegex(reply, r"[А-Яа-яЁё]")

    def test_load_messages_reads_exactly_five_non_empty_lines(self):
        messages = load_messages(Path(__file__).with_name("messages.txt"))
        self.assertEqual(len(messages), 5)
        self.assertEqual(
            [classify(item) for item in messages],
            ["справка", "жалоба", "другое", "жалоба", "справка"],
        )

    def test_missing_file_raises_clear_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "messages.txt"):
            load_messages(Path(__file__).with_name("missing_messages.txt"))


if __name__ == "__main__":
    unittest.main()
