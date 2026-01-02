#
# Copyright (C) 2015-2022 Luis López <luis@cuarentaydos.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.


import unittest
from os import path

import txtflar  # type: ignore[import]

sample_dir = path.dirname(path.realpath(__file__)) + "/samples"


def sample(filepath):
    return sample_dir + "/" + filepath


class TestTxtflat(unittest.TestCase):
    tests = [
        (
            "en",
            "eng-xx-doctor-who-2005-s02e04.srt",
            "eng-xx-doctor-who-2005-s02e04.en.srt",
        ),
        (
            "es",
            "spa-es-doctor-who-s01e01.srt",
            "spa-es-doctor-who-s01e01.es.srt",
        ),
    ]

    def test_get_language(self):
        for lang, filename, x in self.tests:
            got = txtflar.get_file_language(sample(filename))

            self.assertEqual(lang, got, filename)

    def test_no_features_text_exception(self):
        with self.assertRaises(txtflar.LanguageDetectError):
            txtflar.get_file_language(sample("xxx-xx-no-features-lang.txt"))

    def test_get_language_aware_filename(self):
        for x, filename, language_aware_filename in self.tests:
            expected = sample(language_aware_filename)
            got = txtflar.get_language_aware_filename(sample(filename))

            self.assertEqual(expected, got, filename)

    def test_get_filename_for_language(self):
        # Correct filename
        self.assertEqual(
            txtflar.get_filename_for_language("foo.en.txt", "en"), "foo.en.txt"
        )

        # Add language ext
        self.assertEqual(
            txtflar.get_filename_for_language("foo.doc", "es"), "foo.es.doc"
        )

        # Ignore non-lang subextension
        self.assertEqual(
            txtflar.get_filename_for_language("foo.other.doc", "br"),
            "foo.other.br.doc",
        )

        # Fix incorrect extension
        self.assertEqual(
            txtflar.get_filename_for_language("molo.en.md", "es"), "molo.es.md"
        )

    def test_non_utf_file(self):
        lang = txtflar.get_file_language(sample("spa-es-non-utf8-file.srt"))
        self.assertEqual(lang, "es")


if __name__ == "__main__":
    unittest.main()
