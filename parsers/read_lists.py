# -*- coding: utf-8 -*-
import codecs
import csv
import string
from nltk import FreqDist
import nltk
from parsers.string_parser import StringParser, latin_letters
import psycopg2

__author__ = 'Katharine'

# conn_string = "dbname='nlstudent' user = 'nlstudent' password ='2015pink'"
#
# conn = psycopg2.connect(conn_string)
# cursor = conn.cursor()

# read list names and descriptions from a file
# reader = codecs.open('no_wf_rec.csv', encoding='utf-8')
# reader_csv = csv.reader('no_wf_rec.csv','rb')
csv_file = 'no_wf_rec.csv'
f = StringParser()
s = {}
tstrout = ''

# get_listinfo_for_member = """SELECT l.list_name,l.list_description FROM list_rec JOIN
# 	# list_member_rec ON list_rec.list_id = list_member_rec.list_id
# 	# where member_id = %s """
# cursor.execute(get_listinfo_for_member,21447363)

with open(csv_file) as csvfile:
       dialect = csv.Sniffer().sniff(csvfile.read(1024))
       csvfile.seek(0)
       reader = csv.reader(csvfile, dialect)

# rows = cursor.fetchall()
# for row in rows:
for c_line in reader:
    # reader_csv.next()
    if not len(c_line):
        # reader_csv.next()
        continue
    # list_id = c_line[:c_line.find(',')]
    list_id = c_line[0]
    if not list_id.isdigit():
        # reader_csv.next()
        continue
    c_line=str(c_line.strip())
    # c_string is everything after the list_id
    c_string = ' '.join(c_line[1:])
    # print('working on list :', list_id, file=sys.stderr)
    print('working on list :',list_id)

    c_string=str(c_string.strip())
    c_string = ''.join(filter(lambda x: x in string.printable, c_string))
    if len(c_string):
        print('printable chars:',c_string)
        s = f.parse(c_string,True)
        strout = ''
        if s is not None:
            for item in s.items():
                # print(1,str(item[1]))
                word = []
                for word in item[1]:
                    strout = strout+' '+word
        if len(strout):
            tstrout = tstrout+' '+strout
print(tstrout)
words = nltk.tokenize.word_tokenize(tstrout)
the_list_dist = FreqDist(words)

print(the_list_dist.most_common(20))
