import re
import urllib

import simplejson as json

langs = {
    "swedish":"sv",
    "mongolian":"mn",
    "icelandic":"is",
    "uighur":"ug",
    "afrikaans":"af",
    "inuktitut":"iu",
    "dhivehi":"dv",
    "serbian":"sr",
    "german":"de",
    "bulgarian":"bg",
    "latvian":"lv",
    "tagalog":"tl",
    "oriya":"or",
    "thai":"th",
    "esperanto":"eo",
    "arabic":"ar",
    "kannada":"kn",
    "slovak":"sk",
    "malay":"ms",
    "gujarati":"gu",
    "cherokee":"chr",
    "polish":"pl",
    "chinese_simplified":"zh-CN",
    "punjabi":"pa",
    "korean":"ko",
    "finnish":"fi",
    "basque":"eu",
    "swahili":"sw",
    "marathi":"mr",
    "hungarian":"hu",
    "uzbek":"uz",
    "danish":"da",
    "sanskrit":"sa",
    "laothian":"lo",
    "georgian":"ka",
    "bihari":"bh",
    "tamil":"ta",
    "norwegian":"no",
    "telugu":"te",
    "japanese":"ja",
    "english":"en",
    "amharic":"am",
    "sinhalese":"si",
    "catalan":"ca",
    "macedonian":"mk",
    "guarani":"gn",
    "persian":"fa",
    "chinese":"zh",
    "turkish":"tr",
    "azerbaijani":"az",
    "khmer":"km",
    "filipino":"tl",
    "spanish":"es",
    "hindi":"hi",
    "chinese_traditional":"zh-TW",
    "maltese":"mt",
    "urdu":"ur",
    "czech":"cs",
    "russian":"ru",
    "galician":"gl",
    "bengali":"bn",
    "kyrgyz":"ky",
    "tajik":"tg",
    "nepali":"ne",
    "indonesian":"id",
    "vietnamese":"vi",
    "italian":"it",
    "dutch":"nl",
    "albanian":"sq",
    "sindhi":"sd",
    "lithuanian":"lt",
    "greek":"el",
    "burmese":"my",
    "pashto":"ps",
    "tibetan":"bo",
    "kazakh":"kk",
    "estonian":"et",
    "armenian":"hy",
    "slovenian":"sl",
    "malayalam":"ml",
    "hebrew":"iw",
    "ukrainian":"uk",
    "portuguese":"pt-PT",
    "croatian":"hr",
    "romanian":"ro",
    "kurdish":"ku",
    "french":"fr",
    "belarusian":"be"
}

class UrlOpener(urllib.FancyURLopener):
	version = "py-gtranslate/1.0"

class GTransError(Exception): pass

class InvalidLanguage(GTransError): pass

class TranslationFailed(GTransError): pass

base_uri = "http://ajax.googleapis.com/ajax/services/language/translate"
default_params = {'v': '1.0'}

def translate(src, to, phrase):
	src = langs.get(src, src)
	to = langs.get(to, to)
	if not src in langs.values() or not to in langs.values():
		raise InvalidLanguage("%s=>%s is not a valid translation" % (src, to))
	
	args = default_params.copy()
	args.update({
		'langpair': '%s%%7C%s' % (src, to),
		'q': urllib.quote_plus(phrase),
	})
	argstring = '%s' % ('&'.join(['%s=%s' % (k,v) for (k,v) in args.iteritems()]))
	resp = json.load(UrlOpener().open('%s?%s' % (base_uri, argstring)))
	try:
		return resp['responseData']['translatedText']
	except Exception, e:
		raise TranslationFailed("Could not translate %s: %s" (phrase, e.msg))

if __name__ == "__main__":
    print translate("english", "de", "This is a Test")
