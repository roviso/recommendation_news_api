import nepali_roman as nr
import inflect
import re
from unidecode import unidecode

_inflect = inflect.engine()
_number_re = re.compile(r'[0-9]+')
_decimal_number_re = re.compile(r'([0-9]+\.[0-9]+)')

def convert_to_ascii(text):
    return unidecode(text)


def convertToDigit(n, suffix):
 
    # if `n` is zero
    if n == 0:
        return EMPTY
 
    # split `n` if it is more than 19
    return X[n]+' ' + suffix


# Function to convert a given number (max 9-digits) into words
def convert(n):
    # add digits at ten million and hundred million place
    result = convertToDigit((n // 1000000000) % 100, 'अरब, ')
 
    # add digits at ten million and hundred million place
    result += convertToDigit((n // 10000000) % 100, 'करोड, ')
 
    # add digits at hundred thousand and one million place
    result += convertToDigit(((n // 100000) % 100), 'लाख, ')
 
    # add digits at thousand and tens thousand place
    result += convertToDigit(((n // 1000) % 100), 'हजार, ')
 
    # add digit at hundred place
    result += convertToDigit(((n // 100) % 10), 'सय ')
 
    if n > 100 and n % 100:
        result += ''
 
    # add digits at ones and tens place
    result += convertToDigit((n % 100), '')
 
    return result.strip().rstrip(',').replace(', and', ' and')


EMPTY = ''

X = [EMPTY, "एक", "दुई", "तीन", "चार", "पाँच", "छ", "सात", "आठ", "नौ", "दस", "एघार", "बाह्र", "तेह्र", "चौध", "पन्ध्र", "सोह्र", "सत्र", "अठाह्र", "उन्नाइस", "बीस", "एकाइस", "बाइस", "तेइस", "चौबीस", "पचीस", "छब्बीस", "सत्ताइस", "अठ्ठाइस", "उनन्तीस", "तीस", "एकतीस", "बतीस", "तेतीस", "चौतीस", "पैतीस", "छतीस", "सरतीस", "अरतीस", "उननचालीस", "चालीस", "एकचालीस", "बयालिस", "तीरचालीस", "चौवालिस", "पैंतालिस", "छयालिस", "सरचालीस", "अरचालीस", "उननचास", "पचास", "एकाउन्न", "बाउन्न", "त्रिपन्न", "चौवन्न", "पच्पन्न", "छपन्न", "सन्ताउन्न", "अन्ठाउँन्न", "उनान्न्साठी ", "साठी", "एकसाठी", "बासाठी", "तीरसाठी", "चौंसाठी", "पैसाठी", "छैसठी", "सत्सठ्ठी", "अर्सठ्ठी", "उनन्सत्तरी", "सतरी", "एकहत्तर", "बहत्तर", "त्रिहत्तर", "चौहत्तर", "पचहत्तर", "छहत्तर", "सत्हत्तर", "अठ्हत्तर", "उनास्सी", "अस्सी", "एकासी", "बयासी", "त्रीयासी", "चौरासी", "पचासी", "छयासी", "सतासी", "अठासी", "उनान्नब्बे", "नब्बे", "एकान्नब्बे", "बयान्नब्बे", "त्रियान्नब्बे", "चौरान्नब्बे", "पंचान्नब्बे", "छयान्नब्बे", "सन्तान्‍नब्बे", "अन्ठान्नब्बे", "उनान्सय"]

word = 'बिहीवार नेप्से परिसूचक २७.७२ अंकले बढेर २०६८.४२ बिन्दुमा पुगेको छ। त्यस्तै, सेन्सेटिभ इण्डेक्स ५.५१ अंकले बढेको छ भने फ्लोट इण्डेक्स १.८१ अंक र सेन्सेटिभ फ्लोट इण्डेक्स १.६९ अंकले बढेको छ।'

def _expand_number(m):
    num = int(m.group(0))
    # print(num,"nummmm")
    converted_num = convert(num)
    return convert_to_ascii(converted_num)


def _expand_decimal_point(m):
    return m.group(1).replace('.', ' दशमलब ')


def convert_nepali_sentence(sentence):
    text = convert_to_ascii(sentence)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = nr.romanize_text(text)

    text = re.sub(_number_re, _expand_number, text)
    return text

# print(convert(99))
# print(convert(1000))
# print(convert(14632))
# print(convert(997751076))
# print(convert(2147483647))
