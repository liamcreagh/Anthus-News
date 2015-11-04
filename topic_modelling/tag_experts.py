from collections import Counter, defaultdict
from math import log
import operator
from pprint import pprint
from urllib import request
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, Tag
from gensim.corpora import Dictionary, MmCorpus, IndexedCorpus
from gensim.models import TfidfModel
import pickle
import requests
from parsers.string_parser import StringParser


topics = ['art', 'business', 'celeb', 'design', 'education', 'entertain', 'fashion', 'film', 'food', 'health', 'music', 'politic', 'scien', 'sport', 'tech', 'travel']

__author__ = 'James'

from psycopg2 import connect

expert2doc = {}


class ExpertCorpus(object):
    def __init__(self):

        member_query = """
        select * from expert_420
        """

        count_query = """
        select count(*) from expert_420
        """

        self.query = """
        select l.list_id,l.list_name,l.list_description from list_rec_420 as l
        join list_member_rec_420 as lm1
        on lm1.list_id=l.list_id
        where lm1.member_id = %s;
        """

        conn_string = "dbname='list_6220' user = 'nlstudent' password =''"

        self.connection = connect(conn_string)
        self.ind = 0
        self.parser = StringParser()
        self.cursor = self.connection.cursor()
        self.cursor.execute(member_query)
        self.members = self.cursor.fetchall()

        self.cursor.execute(count_query)
        self.N_members = self.cursor.fetchone()[0]
        print(self.N_members)
        # self.members =[50393960, 39247971, 39224224]

    def __iter__(self):
        list_dict = Dictionary.load('terms.dict')
        # list_dict.filter_extremes(no_below=1000,no_above=0.99)
        counter = 0
        doc_id = 0
        for member_id, count in self.members:
            if counter % 1000 == 0:
                print('Done', counter)

            print(member_id, count)
            self.cursor.execute(self.query, (member_id,))
            expert_text = Counter()

            for result in self.cursor:
                parsed_text = self.parser.parse_list(title=result[1], description=result[2])

                expert_text.update(parsed_text['text'])
                # expert_text.update(parsed_text['bigrams'])

            terms = ((e, v) for e, v in expert_text.items() if v > 10 and any([e.startswith(t) for t in topics]))
            counter += 1

            print(list(terms))

            word_bag = []
            for k, v in terms:
                try:
                    word_bag.append((list_dict.token2id[k], v))
                except KeyError:
                    pass
            expert2doc[member_id] = doc_id
            doc_id += 1

            yield word_bag


class _ExpertCorpus(object):
    def __init__(self):

        member_query = """
        select * from expert_10_50
        """

        count_query = """
        select count(*) from expert_10_50
        """

        self.query = """
        select l.list_id,l.list_name,l.list_description from list_rec as l
        join list_member_rec as lm1
        on lm1.list_id=l.list_id
        where lm1.member_id = %s;
        """

        conn_string = "dbname='nlstudent' user = 'nlstudent' password ='2015pink'"

        self.connection = connect(conn_string)
        self.ind = 0
        self.parser = StringParser()
        self.cursor = self.connection.cursor()
        self.cursor.execute(member_query)
        self.members = self.cursor.fetchall()

        self.cursor.execute(count_query)
        self.N_members = self.cursor.fetchone()[0]
        print(self.N_members)
        # self.members =[12, 50393960, 39247971, 39224224]

    def __iter__(self):
        list_dict = Dictionary.load('terms.dict')
        # list_dict.filter_extremes(no_below=1000,no_above=0.99)
        counter = 0
        doc_id = 0
        for member_id, count in self.members:
            if counter % 100 == 0:
                print('Done', counter)

            self.cursor.execute(self.query, (member_id,))
            expert_text = Counter()

            for result in self.cursor:
                parsed_text = self.parser.parse_list(title=result[1], description=result[2])

                expert_text.update(parsed_text['text'])

            terms = sorted([(e, v) for e, v in expert_text.items() if v > 1], key=operator.itemgetter(1), reverse=True)
            counter += 1

            if len(terms):
                if terms[0][1] > 10:
                    word_bag = []
                    for k, v in terms:
                        try:
                            word_bag.append((list_dict.token2id[k], v))
                        except KeyError:
                            pass
                    expert2doc[member_id] = doc_id
                    doc_id += 1
                    yield word_bag


def load_experts():
    """
    load expert data and save to file
    """
    expert_corpus = ExpertCorpus()
    MmCorpus.serialize(corpus=expert_corpus, fname='expert_corpus_new_test.mm')

    """
    save expert-to-document map to pickle
    """
    pickle.dump(expert2doc, open('expert2doc_new_test.p', 'wb'))
