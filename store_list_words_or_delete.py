from collections import Counter
import csv
import string
from nltk import FreqDist
import nltk
from psycopg2._psycopg import DatabaseError
import sys
from parsers.string_parser import StringParser, latin_letters
import psycopg2

__author__ = 'Katharine'

conn_string = "dbname='nlstudent' user = 'nlstudent' password ='2015pink'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

f = StringParser()
s = {}

get_listinfo_for_member = """SELECT l.list_name,l.list_description FROM list_rec as l JOIN
	list_member_rec as lm ON l.list_id = lm.list_id
	where lm.member_id = %s"""

get_listcount_for_member = """SELECT count(lm.list_id) FROM list_member_rec as lm JOIN
	list_rec as l ON l.list_id = lm.list_id
	where lm.member_id = %s;"""

get_listinfo_for_list = """SELECT l.list_name,l.list_description FROM list_rec as l
	where list_id = %s"""

store_wordfreq_for_list = """SELECT l.list_name,l.list_description FROM list_rec as l
	where list_id = %s"""

get_all_lists = """SELECT l.list_name,l.list_description FROM list_rec as l """

# check if the word is already in the database
def word_not_in_db(word):
	cursor.execute("SELECT word_id FROM list_word_rec WHERE word = %s", (word,))
	return cursor.fetchone() is None

# knowing the word is in db, get its word_id
def get_word_id(word):
	cursor.execute("SELECT word_id FROM list_word_rec WHERE word = %s", (word,))
	return cursor.fetchone()

def delete_word_frequency_rec(article_id):
	delete_word_frequency_rec = "DELETE FROM word_frequency_rec WHERE article_id = %s;"
	cursor.execute(delete_word_frequency_rec,[article_id])
	conn.commit()

def delete_list_and_list_member_recs(list_id):
    delete_list_member_rec = "DELETE FROM list_member_rec WHERE list_id = %s;"
	cursor.execute(delete_list_member_rec,[list_id])
	delete_list_rec = "DELETE FROM list_rec WHERE list_id = %s;"
	cursor.execute(delete_list_rec,[list_id])
	conn.commit()

def isEmpty(self, dictionary):
   for element in dictionary:
     if element:
       return True
     return False

# # read member id from a file
# reader = csv.reader(open('memberid.csv', 'r'))
#
# for current_line in reader:
#     curr_string = ''.join(current_line)
#     member_id = int(curr_string)
#
#     cursor.execute(get_listcount_for_member,[member_id])
#     mlistcount = cursor.fetchall()[0]
#     cursor.execute(get_listinfo_for_member,[member_id])
#
#     tstrout = ''
#     rows = cursor.fetchall()
#     for row in rows:
#     # for current_line in reader:
#         c_line=str(row)
#         # c_line=str(current_line.strip())
#         c_line = ''.join(filter(lambda x: x in string.printable, c_line))
#         # print(c_line)
#         if len(c_line):
#             s = f.parse(c_line,True)
#             strout = ''
#             if s is not None:
#                 for item in s.items():
#                     # print(1,str(item[1]))
#                     word = []
#                     for word in item[1]:
#                         strout = strout+' '+word
#             if len(strout):
#                 tstrout = tstrout+' '+strout
#     # print(tstrout)
#     words = nltk.tokenize.word_tokenize(tstrout)
#     the_list_dist = FreqDist(words)
#
#     print('for',member_id,'on',mlistcount[0],'lists:',the_list_dist.most_common(20))

def get_list_dists_for(member_id):
    print(member_id, file=sys.stderr)

    # cursor.execute(get_listcount_for_member, [member_id])

    # mlistcount = cursor.fetchone()[0]
    cursor.execute(get_listinfo_for_member, [member_id])

    tstrout = ''
    rows = cursor.fetchall()
    for row in rows:
        c_line = str(row)
        c_line = ''.join(filter(lambda x: x in string.printable, c_line))

        if len(c_line):
            parsed_text = f.parse(c_line, True)
            strout = ''
            if parsed_text is not None:
                for item in s.items():
                    # print(1,str(item[1]))
                    word = []
                    for word in item[1]:
                        strout = strout + ' ' + word
            if len(strout):
                tstrout = tstrout + ' ' + strout
    # print(tstrout)
    words = nltk.tokenize.word_tokenize(tstrout)
    the_list_dist = FreqDist(words)

    return str(member_id) + " on " + str(len(rows)) + " lists: " + str(the_list_dist.most_common(20))


def get_list_dists(list_id):

    cursor.execute(get_listinfo_for_list, [list_id])

    c = Counter()

    for row in cursor:
        list_text = ' '.join(row)
        # print(list_text)
        parsed_text = f.parse(list_text, is_list=True)
        if parsed_text is not None:
            c.update(parsed_text['text'])
            c.update(dict.fromkeys(parsed_text['bigrams'], 1))
            c.update(dict.fromkeys(parsed_text['entities'], 1))


    the_list_dist = {k: v for k, v in c.items()}
    return the_list_dist

# read list ids from a file
byte_reader = open('no_wf_rec.csv', 'rb')
#
for current_line in byte_reader:
    # convert to string
    current_string = current_line.decode("utf-8")
    # print(current_string)
    # print(len(current_line),current_line)
    if not len(current_string):
        print('empty string... go to next record')
        continue
    current_string = current_string.split(',')
    list_id = current_string[0]
    # print(list_id)
    if not len(list_id):
        print('list_id,',list_id,' zero length... go to next record')
        continue
    if not list_id.isdigit():
        print('list_id not numeric... go to next record')
        continue
    curr_string = ' '.join(current_string[1:])
    # print('working on list :', list_id, file=sys.stderr)
    print('working on list :',list_id)
    # list_dict = get_list_dists(list_id)

    c = Counter()

    parsed_text = f.parse(curr_string, is_list=True)
    if parsed_text is not None:
        c.update(parsed_text['text'])
        c.update(dict.fromkeys(parsed_text['bigrams'], 1))
        c.update(dict.fromkeys(parsed_text['entities'], 1))
    else:
        print('parsed text is empty')
    # cycle through dictionary
    if not c.items():
        print('parsed text is empty')
    for word,frequency in c.items():
        print('storing words')
        cursor.execute("SELECT word_id FROM list_word_rec WHERE word = %s", (word,))


        if word_not_in_db(word):
            #it's not in database so store this as a new word
            store_word_rec = """INSERT INTO list_word_rec(word_id,word)
                                    VALUES (DEFAULT,%s)
                                    RETURNING word_id """
            cursor.execute(store_word_rec,[word])
            #store the current value of word_id
            word_id = cursor.fetchone()[0]
            conn.commit()

        else:
            word_id = get_word_id(word)

        store_list_wf_rec = """INSERT INTO list_wf_rec(list_id,word_id,frequency)
                                VALUES (%s,%s,%s) """
        cursor.execute(store_list_wf_rec,(list_id,word_id,frequency))

        conn.commit()