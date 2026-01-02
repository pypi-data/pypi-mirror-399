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


from os import path

import babelfish
import chardet
import langdetect


class DetectError(Exception):
    pass


class LanguageDetectError(DetectError):
    pass


class EncodingDetectError(DetectError):
    pass


def get_language(buff):
    # Try with utf-8
    try:
        return langdetect.detect(buff.decode("utf-8"))
    except langdetect.lang_detect_exception.LangDetectException as e:
        raise LanguageDetectError(str(e)) from e
    except UnicodeError:
        pass

    # Try guessing
    guess = chardet.detect(buff)
    if not guess or guess["encoding"] is None:
        msg = "Unable to detect encoding"
        raise EncodingDetectError(msg)

    try:
        return langdetect.detect(buff.decode(guess["encoding"]))
    except UnicodeError as e:
        msg = f"Encoding '{guess['encoding']}' is incorrect: {e}"
        raise EncodingDetectError(msg)


def get_file_language(filepath, chunk=1024):
    with open(filepath, "rb") as stream:
        ret = get_language(stream.read(chunk))

    return ret


def get_filename_for_language(filepath, language):
    name, ext = path.splitext(filepath)
    name_without_langext, langext = path.splitext(name)

    try:
        babelfish.Language.fromalpha2(langext[1:])
        name = name_without_langext
    except (IndexError, babelfish.LanguageReverseError):
        pass

    return f"{name}.{language}{ext}"


def get_language_aware_filename(filepath):
    return get_filename_for_language(filepath, get_file_language(filepath))
