import csv
import string
from nltk import FreqDist
import nltk
from parsers.string_parser import StringParser, latin_letters
import psycopg2
__author__ = 'Katharine'

conn_string = "dbname='nlstudent' user = 'nlstudent' password ='2015pink'"

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

f = StringParser()
s = {}

get_listinfo_for_list = """SELECT l.list_name,l.list_description FROM list_rec as l
	where list_id = %s"""

def get_list_dists_for(list_id):
    cursor.execute(get_listinfo_for_list,[list_id])

    rows = cursor.fetchall()
    tstrout = ''
    for row in rows:
        c_line=str(row)
        c_line = ''.join(filter(lambda x: x in string.printable, c_line))
        # print(c_line)
        if len(c_line):
            s = f.parse(c_line,True)
            strout = ''
            if s is not None:
                for item in s.items():
                    # print(1,str(item[1]))
                    word = []
                    for word in item[1]:
                        strout = strout+' '+word
            if len(strout):
                tstrout = tstrout+' '+strout
    # print(tstrout)
    words = nltk.tokenize.word_tokenize(tstrout)
    the_list_dist = FreqDist(words)
    return " top 20 list text : " + str(the_list_dist.most_common(20))
    # return the_list_dist

# read list id from a file
reader = csv.reader(open('listid.csv', 'r'))

for current_line in reader:
    curr_string = ''.join(current_line)
    list_id = int(curr_string)
    print(get_list_dists_for(list_id))

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
