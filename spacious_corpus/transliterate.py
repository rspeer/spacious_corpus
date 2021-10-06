# This table comes from https://github.com/opendatakosovo/cyrillic-transliteration/blob/master/cyrtranslit/mapping.py,
# from the 'cyrtranslit' module. We originally had to reimplement it because
# 'cyrtranslit' didn't work in Python 3; now it does, but we've made the table
# more robust than the one in cyrtranslit.
SR_LATN_TABLE = {
    ord('А'): 'A',   ord('а'): 'a',
    ord('Б'): 'B',   ord('б'): 'b',
    ord('В'): 'V',   ord('в'): 'v',
    ord('Г'): 'G',   ord('г'): 'g',
    ord('Д'): 'D',   ord('д'): 'd',
    ord('Ђ'): 'Đ',   ord('ђ'): 'đ',
    ord('Е'): 'E',   ord('е'): 'e',
    ord('Ж'): 'Ž',   ord('ж'): 'ž',
    ord('З'): 'Z',   ord('з'): 'z',
    ord('И'): 'I',   ord('и'): 'i',
    ord('Ј'): 'J',   ord('ј'): 'j',
    ord('К'): 'K',   ord('к'): 'k',
    ord('Л'): 'L',   ord('л'): 'l',
    ord('Љ'): 'Lj',  ord('љ'): 'lj',
    ord('М'): 'M',   ord('м'): 'm',
    ord('Н'): 'N',   ord('н'): 'n',
    ord('Њ'): 'Nj',  ord('њ'): 'nj',
    ord('О'): 'O',   ord('о'): 'o',
    ord('П'): 'P',   ord('п'): 'p',
    ord('Р'): 'R',   ord('р'): 'r',
    ord('С'): 'S',   ord('с'): 's',
    ord('Т'): 'T',   ord('т'): 't',
    ord('Ћ'): 'Ć',   ord('ћ'): 'ć',
    ord('У'): 'U',   ord('у'): 'u',
    ord('Ф'): 'F',   ord('ф'): 'f',
    ord('Х'): 'H',   ord('х'): 'h',
    ord('Ц'): 'C',   ord('ц'): 'c',
    ord('Ч'): 'Č',   ord('ч'): 'č',
    ord('Џ'): 'Dž',  ord('џ'): 'dž',
    ord('Ш'): 'Š',   ord('ш'): 'š',

    # Handle Cyrillic letters from other languages. We hope these cases don't
    # come up often when we're trying to transliterate Serbian, but if these
    # letters show up in loan-words or code-switching text, we can at least
    # transliterate them approximately instead of leaving them as Cyrillic
    # letters surrounded by Latin.

    # Russian letters transliterated in Serbian style
    ord('Ё'): 'Jo',  ord('ё'): 'jo',
    ord('Й'): 'J',   ord('й'): 'j',
    ord('Щ'): 'Šč',  ord('щ'): 'šč',
    ord('Ъ'): '',    ord('ъ'): '',
    ord('Ы'): 'Y',   ord('ы'): 'y',
    ord('Ь'): "'",   ord('ь'): "'",
    ord('Э'): 'E',   ord('э'): 'e',
    ord('Ю'): 'Ju',  ord('ю'): 'ju',
    ord('Я'): 'Ja',  ord('я'): 'ja',

    # Belarusian letter
    ord('Ў'): 'Ŭ',   ord('ў'): 'ŭ',

    # Ukrainian letters
    ord('Є'): 'Je',  ord('є'): 'je',
    ord('І'): 'I',   ord('і'): 'i',
    ord('Ї'): 'Ï',   ord('ї'): 'ï',
    ord('Ґ'): 'G',   ord('ґ'): 'g',

    # Macedonian letters
    ord('Ѕ'): 'Dz',  ord('ѕ'): 'dz',
    ord('Ѓ'): 'Ǵ',   ord('ѓ'): 'ǵ',
    ord('Ќ'): 'Ḱ',   ord('ќ'): 'ḱ',

    # Tajik letter
    ord('Ҷ'): 'Dž',  ord('ҷ'): 'dž',

    # Azerbaijani letters
    ord('Ҹ'): 'C',  ord('ҹ'): 'c',
    ord('Ә'): 'Ə',  ord('ә'): 'ə',
    ord('Ғ'): 'Ğ',  ord('ғ'): 'ğ',
    ord('Һ'): 'H',  ord('һ'): 'h',
    ord('Ө'): 'Ö',  ord('ө'): 'ö',
    ord('Ҝ'): 'G',  ord('ҝ'): 'g',
    ord('Ү'): 'Ü',  ord('ү'): 'ü',

    # Kazakh letters
    ord('Қ'): 'Q',   ord('қ'): 'q',
    ord('Ә'): "A'",  ord('ә'): "a'",
    ord('Ң'): "N'",  ord('ң'): "n'",
    ord('Ұ'): 'U',   ord('ұ'): "u",

    # Obsolete letters - transcribe them like Polish when appropriate
    ord('Ѣ'): 'Ě',   ord('ѣ'): 'ě',
    ord('Ѧ'): 'Ę',   ord('ѧ'): 'ę',
    ord('Ѩ'): 'Ję',  ord('ѩ'): 'ję',
    ord('Ѫ'): 'Ą',   ord('ѫ'): 'ą',
    ord('Ѭ'): 'Ją',  ord('ѭ'): 'ją',
    ord('Ѥ'): 'Je',  ord('ѥ'): 'je',
}

AZ_LATN_TABLE = SR_LATN_TABLE.copy()
AZ_LATN_TABLE.update({
    # Azerbaijani letters with different transliterations
    ord('Ч'): 'Ç',  ord('ч'): 'ç',
    ord('Х'): 'X',  ord('х'): 'x',
    ord('Ы'): 'I',  ord('ы'): 'ı',
    ord('И'): 'İ',  ord('и'): 'i',
    ord('Ж'): 'J',  ord('ж'): 'j',
    ord('Ј'): 'Y',  ord('ј'): 'y',
    ord('Г'): 'Q',  ord('г'): 'q',
    ord('Ш'): 'Ş',  ord('ш'): 'ş',
})


# from https://www.translitteration.com/transliteration/en/kazakh/national/
KK_LATN_TABLE = SR_LATN_TABLE.copy()
KK_LATN_TABLE.update({
    # Kazakh letters with different transliterations
    ord('Ғ'): "G'",  ord('ғ'): "g'",
    ord('И'): "I'",  ord('и'): "i'",
    ord('Й'): "I'",  ord('й'): "i'",
    ord('Ж'): 'J',   ord('ж'): 'j',
    ord('Ө'): "O'",  ord('ө'): "o'",
    ord('У'): "Y'",  ord('у'): "y'",
    ord('Ү'): "U'",  ord('ү'): "u'",
    ord('Һ'): 'H',   ord('һ'): 'h',
    ord('Ч'): "C'",  ord('ч'): "c'",
})


def transliterate(table, text):
    """
    Transliterate text according to one of the tables above.

    `table` chooses the table. It looks like a language code but comes from a
    very restricted set:

    - 'sr-Latn' means to convert Serbian, which may be in Cyrillic, into the
      Latin alphabet.
    - 'az-Latn' means the same for Azerbaijani Cyrillic to Latn.
    """
    if table == 'sr-Latn':
        return text.translate(SR_LATN_TABLE)
    elif table == 'az-Latn':
        return text.translate(AZ_LATN_TABLE)
    elif table == 'kk-Latn':
        return text.translate(KK_LATN_TABLE)
    else:
        raise ValueError("Unknown transliteration table: {!r}".format(table))
