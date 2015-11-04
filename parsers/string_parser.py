# -*- coding: utf-8 -*-
from collections import Counter
from pprint import pprint
import itertools

__author__ = 'Katharine'

import codecs
import re
from nltk.corpus import stopwords
import nltk
from nltk import FreqDist
import unicodedata as ud
import enchant
import string

stopwords = stopwords.words('english')
lemmatizer = nltk.WordNetLemmatizer()
stemmer = nltk.stem.porter.PorterStemmer()
latin_letters = {}

# Used when tokenizing words
sentence_re = r'((?x)([A-Z]\.)+ | \.\.\.| [.,;"\'?():`/@# | _-]    )'


# Domain-specific terms
noise_words_set = ['twitter', 'tweeter', 'tweet', 'list', 'www', 'http', 'com',
                   'org', 'people', 'myfollower', 'follow', 'follower', 'tweep', 'people',
                   'etc', 'ppl', 'friend', 'folk', 'else', 'influence', 'influential', 'tumblr',
                   'peep', 'facebook', 'good', 'great', 'like', 'fave', 'various', 'twibe', 'top',
                   'amigos', 'interest', 'account', 'stuff', 'work', 'real', 'visit', 'join', 'related',
                   'new', 'thing', 'know', 'info', 'awesome', 'met', 'cool', 'word',
                   'twibe', 'inspire', 'inspiration', 'inspirational', 'twitters', 'friend', 'follow']

# include plurals
noise_words_set.extend(list(map(lambda x: x + 's', noise_words_set)))

 # text containing any of these words will be discarded
useless_list = ['favstar', 'formulist', 'candy', 'SocialBro']

# 'stems' for common topics
replacements = ['tech', 'music', 'dev', 'blog', 'photo', 'design', 'food', 'fashion', 'journ']

# d is an english dictionary
d = enchant.Dict("en")

# add the stem words from above to the dictionary so they don't get thrown out
for rep in replacements:
    d.add(rep)


class UselessTextError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class StringParser:
    def __init__(self):
        self.camel_case_pattern = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')

    def parse_list(self, title=None, description=None):

        words_and_bgs = {'text':[], 'bigrams':[]}

        try:  # get rid of any text containing any word in useless_list
            if any([item in title+description for item in useless_list]):
                raise UselessTextError('Useless text so discarded')
        except UselessTextError:
            # go to next string
            return words_and_bgs

        parsed_title = self.parse(title)
        parsed_description = self.parse(description)

        text = list(set(parsed_title['text']+parsed_description['text']))
        bigrams = list(set(parsed_title['bigrams']+parsed_description['bigrams']))

        for word in text:
            if not d.check(word):
               text.remove(word)

            for rep in replacements:
                if word.startswith(rep):
                    word = rep


        words_and_bgs = {'text':text, 'bigrams':bigrams}


        return words_and_bgs

    def parse(self, strings):

        words_and_bgs = {'text': [], 'bigrams': []}

        strings = self.string_to_list(strings)
        text = []
        for w in strings:
            text.extend(self.camel_case(w))

        text = list(filter(self.acceptable_word,
                   list(map(self.normalise,
                            list(map(self.only_roman_chars, text))))))

        text = list(filter(lambda x: all(s.isalpha() for s in x), text))

        if not len(text):
            return words_and_bgs

        f_bigrams = self.find_bigrams(text)
        bigrams = []

        for bg in f_bigrams:
            text.remove(bg[0])
            text.remove(bg[1])
            bg = '_'.join(b.lower() for b in bg)
            bigrams.append(bg)


        # trying to get rid of those chars that cause it to crash
        text = ''.join(filter(lambda x: x in string.printable, text))

        words_and_bgs = {'text': text, 'bigrams': bigrams}

        return words_and_bgs

    def lists_overlap(self, a, b):
        """
        Check overlap between two lists
        """

        sb = set(b)
        return any(el in sb for el in a)

    def is_latin(self, uchr):
        """
        Check if all letters in string are Latin (no chinese, japanese chars)
        """

        try:
            return latin_letters[uchr]
        except KeyError:
            return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

    def only_roman_chars(self, unistr):
        # used to filter out non-latin chars (Chinese etc.)
        for x in unistr:
            if (x not in string.printable or x in string.punctuation):
                unistr = unistr.replace(x, '')
        # return all(self.is_latin(uchr) for uchr in unistr)
        return unistr

    def normalise(self, word):
        """
        :param word: string
        :return: word in lower-case, mapped to replacement stems
        """

        word = word.replace('.', '')
        word = word.lower()
        for rep in replacements:
            if word.startswith(rep):
                word = rep

        return word

    def acceptable_word(self, word):
        """
        :param word:  single word that's passed in
        :return:    empty if it's a stopword, noiseword, 1 char or 40 chars or more
                    if it's a list, only return words found in the english dictionary
        """
        accepted = (2 < len(word) < 40) \
                   and (word.lower() not in stopwords) \
                   and (word.lower() not in noise_words_set)

        return accepted

    def string_to_list(self, word_string):
        """
        :param word_string: untokenized string
        :return: list of tokens
        """

        list_of_words = [x for x in nltk.regexp_tokenize(word_string, sentence_re, gaps=True) if
                         x not in ["'", '"', "(", ")"]]
        return list_of_words

    def camel_case(self, word):
        """
        :param word: string to be checked for CamelCase format
        :return: split list of camel case words, empty if not found
        """
        camel = self.camel_case_pattern.findall(word)

        if camel:
            return camel
        else:
            return []

    def find_bigrams(self, wlist):
        """
        :param wlist: list of terms
        :return: list of adjective-noun or noun-noun pairs, in format: word1_word2
        """

        bgs = []
        bg = "BG: {<NN|NNS|NNP><NN|NNS|NNP> | <JJ><NN|NNS|NNP>}"  # define a tag pattern of a Bigram (adjective + noun|plural noun|proper noun)

        tags = nltk.pos_tag(wlist)

        # create a Bigram parser
        BGParser = nltk.RegexpParser(bg)
        bg_tags = BGParser.parse(tags)  # parse the word_list
        for subtree in bg_tags.subtrees(filter=lambda x: x.label() == 'BG'):  # only look at the bigrams
            # get bigrams, remove POS tags and link words with '_'

            bgs.append([l[0] for l in subtree.leaves()])
        return bgs

    def find_entities(self, wlist):
        """
        :param wlist: list of strings
        :return: list of found entities, in format: word1_word2
        """

        tags = nltk.pos_tag(wlist)
        entity_labels = ['GPE', 'LOCATION', 'FACILITY', 'PERSON', 'ORGANISATION']
        ne_tags = nltk.ne_chunk(tags)
        entities = []

        for subtree in ne_tags.subtrees(filter=lambda x: x.label() in entity_labels):
            if len(subtree) > 1:
                entities.append(
                    '_'.join([l[0] for l in subtree.leaves()
                              if l[0].lower() not in noise_words_set]))
        return entities
