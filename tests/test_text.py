import unittest
from ttschat.pipeline import validate_text
from ttschat.errors import AppError
from ttschat.text.chunker import split_text
from ttschat.text.normalizer import normalize_es


class Limits(unittest.TestCase):
    def test_empty(self):
        for t in (None, "", "   \n\t"):
            with self.assertRaises(AppError) as c: validate_text(t, 20000)
            self.assertEqual(c.exception.code, "EMPTY_TEXT")

    def test_limit_exact_ok(self):
        validate_text("a" * 20000, 20000)

    def test_limit_exceeded_message(self):
        with self.assertRaises(AppError) as c: validate_text("a" * 20123, 20000)
        self.assertEqual(c.exception.code, "TEXT_TOO_LONG")
        self.assertIn("123", c.exception.message)
        self.assertIn("20.000", c.exception.message)


class Chunking(unittest.TestCase):
    TEXT = ("Hola, soy el Sr. Pérez. ¿Cómo estás hoy? Muy bien, gracias. " * 5 + "\n\n" +
            "Segundo párrafo con una oración bastante larga, que incluye comas, y sigue y sigue sin parar, " * 6 + "Fin.")

    def test_no_word_cut_and_size(self):
        for limit in (40, 120, 400):
            chunks = split_text(self.TEXT, limit)
            self.assertTrue(all(len(c.text) <= limit for c in chunks))
            self.assertEqual(" ".join(self.TEXT.split()), " ".join(" ".join(c.text for c in chunks).split()))

    def test_paragraph_flags(self):
        ch = split_text("Uno.\n\nDos.", 100)
        self.assertEqual([c.paragraph_end for c in ch], [True, True])

    def test_sentences_kept_whole_when_they_fit(self):
        ch = split_text("Primera oración. Segunda oración. Tercera oración.", 40)
        for c in ch: self.assertTrue(c.text.endswith("."))

    def test_long_unpunctuated_split_on_words(self):
        ch = split_text("palabra " * 200, 50)
        self.assertTrue(all(c.text.split() and set(c.text.split()) == {"palabra"} for c in ch))

    def test_20000_chars(self):
        text = ("Esta es una oración de prueba para medir el rendimiento. " * 400)[:20000]
        ch = split_text(text, 400)
        self.assertTrue(all(len(c.text) <= 400 for c in ch))
        self.assertGreater(len(ch), 40)

    def test_empty(self):
        self.assertEqual(split_text(" \n \n", 100), [])


class Normalizer(unittest.TestCase):
    def test_abbreviations_and_separators(self):
        out = normalize_es("El Sr. López, Dra. Ruiz y 12.450 pesos")
        self.assertIn("señor López", out); self.assertIn("doctora Ruiz", out); self.assertIn("12450", out)

    def test_date(self):
        self.assertIn("octubre", normalize_es("Es el 08/10/2026."))


if __name__ == "__main__":
    unittest.main()
