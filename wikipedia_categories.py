from math import log
import operator
from pprint import pprint
import psycopg2
from parsers.string_parser import StringParser
from wikipedia_stuff.models import WikiCategory


test = (
    'Tens of thousands of Greeks rallied on Monday to back their leftwing government\'s rejection of a tough international bailout after a clash with foreign lenders pushed Greece close to financial chaos and forced a shutdown of its banking system.\n'
    '\n'
    'With a popular referendum on the bailout planned for Sunday, Prime Minister Alexis Tsipras put his own position on the line, saying he would respect the result of the vote but would not lead a government to administer "austerity in perpetuity".\n'
    '\n'
    '"If the Greek people want to have a humiliated prime minister, there are a lot of them out there. It won\'t be me," he said in an interview on Greek state television as one of the biggest rallies seen in Athens in years was taking place.\n'
    '\n'
    'The show of defiance came at the end of a day that started with stunned Greeks waking up to shuttered banks, long supermarket lines and overwhelming uncertainty over their future in the euro zone.\n'
    '\n'
    'European leaders and policymakers, wrong-footed by Tsipras\'s shock announcement of the referendum in the early hours of Saturday morning, warned that it would be a plebiscite on Greece\'s future as a member of the single currency.\n'
    '\n'
    'With Greece hours away from defaulting on a 1.6 billion euro loan from the International Monetary Fund, European commission President Jean-Claude Juncker made a last-minute offer to Athens in a bid to reach a bailout agreement, European Union and Greek government sources said.\n'
    '\n'
    'Under the offer, Prime Minister Alexis Tsipras would have to send written acceptance by Tuesday, in time for an emergency meeting of the Eurogroup of euro zone finance ministers, and agree to campaign in favour of the bailout in the July 5 referendum.\n'
    '\n'
    'There was little sign that Tsipras would drop his repeated rejections of the bailout offer, however, with a Greek official saying the prime minister would be voting "no".\n'
    '\n'
    'UNCHARTED TERRITORY\n'
    '\n'
    'Ratings agency Standard and Poor\'s cut Greece\'s sovereign debt rating one notch further into junk levels to CCC- on Monday, saying there was a 50 percent probability it would leave the euro zone.\n'
    '\n'
    'Greeks, used to seeing lengthy talks with creditors end with an 11th-hour deal, were shocked by the turn of events. Queues snaked outside ATMs and inside supermarkets, while fears of disruptions to fuel and medicine supplies grew.\n'
    '\n'
    'Drugmakers said they would continue to ship medicines to Greece in coming weeks despite unpaid bills, but warned that supplies could soon be in jeopardy without emergency action.\n'
    '\n'
    'The breakdown of talks has pushed the European Union and euro zone into uncharted terrain. The Athens stock exchange was closed, but financial markets elsewhere fell on fears that Greece could be heading out of the euro.\n'
    '\n'
    'The blue-chip Euro STOXX 50 .STOXX50E index fell more than 4 percent, with bank shares down sharply [.EU] .SX7E. By midday, all three major U.S. stock indexes were down more than 1 percent. [.N]\n'
    '\n'
    '"I can\'t believe it," said Athens resident Evgenia Gekou, 50, on her way to work. "I keep thinking we\'ll wake up tomorrow and everything will be OK. I\'m trying hard not to worry."\n'
    '\n'
    'After months of talks, Greece\'s exasperated European partners have put the blame for the crisis squarely on Tsipras for rejecting a package they consider generous. The Greek side argues that pension cuts and tax hikes demanded of it would only deepen the economic crises in a country where a quarter of the workforce is already unemployed.\n'
    '\n'
    'A snap Reuters poll of more than 70 economists and traders taken on Monday put the probability of Greece leaving the euro zone at 45 percent, up from 30 percent a week ago.')

__author__ = 'James'

get_stems_query = """select p.page_id, p.page_title, s1.stem_id, s1.stem_word
from wiki_pages_rec as p
join stem_rec_pages as sp1
on sp1.wikipage_id=p.page_id
join stem_rec as s1
on sp1.stem_id=s1.stem_id
where page_id in (
select sp.wikipage_id
from stem_rec as s
right join stem_rec_pages as sp
on sp.stem_id=s.stem_id
where s.stem_id=%s);"""

get_categories_query = """select c.category_id, c.category_title
from wiki_pages_rec as p
right join wiki_pages_rec_categories as pc
on pc.wikipage_id=p.page_id
right join wiki_category_rec as c
on pc.wikicategory_id=c.category_id
where p.page_id=%s;"""

category_count_query = """select s.stem_id, count(distinct c.category_id)
from  stem_rec as s
join stem_rec_pages as sp
on s.stem_id=sp.stem_id
join wiki_pages_rec as p
on sp.wikipage_id=p.page_id
join wiki_pages_rec_categories as pc
on pc.wikipage_id= p.page_id
join wiki_category_rec as c
on c.category_id=pc.wikicategory_id
where s.stem_word=%s
group by s.stem_id;"""

N_category = WikiCategory.objects.all().count()


class WikiStem:
    def __init__(self):
        self.stem_id = None
        self.word = None
        self.pages = {}
        self.category_count = 0.0
        self.weight = 0.0


class WikiPage:
    def __init__(self, page_id, page_title):
        self.page_id = page_id
        self.title = page_title
        self.categories = {}
        self.stems = {}
        self.title_length = len(self.stems)


connection = psycopg2.connect(database='nlstudent',
                              user='nlstudent',
                              host='localhost',
                              port='5432', )

article_words = [('peopl', 81), ('medium', 27), ('interest', 24), ('tech', 22), ('blogger', 21), ('writer', 19), ('follow', 18), ('social', 18), ('fave', 15), ('ive', 14), ('top', 12), ('journalist', 12), ('uk', 12), ('celebr', 11), ('stuff', 11), ('use', 11), ('list', 11), ('Tech', 10), ('funni', 10), ('fun', 9)]
article_words = [('entertain', 14), ('funni', 11), ('geek', 11), ('celebr', 10), ('interest', 10), ('writer', 9), ('celeb', 7), ('thing', 6), ('art', 5), ('Funny', 5), ('ha', 5), ('tv', 5), ('gener', 5), ('medium', 5), ('stuff', 5), ('awesom', 5), ('fun', 5), ('screenwrit', 4), ('music', 4)]
# 813286: [('peopl', 90), ('news', 84), ('polit', 36), ('follow', 25), ('medium', 19), ('interest', 19), ('tech', 18), ('influenti', 16), ('world', 15), ('social', 15), ('favorit', 13), ('formulist', 12), ('design', 12), ('influenc', 12), ('top', 12), ('tweep', 12), ('made', 11), ('technolog', 11), ('use', 11), ('stuff', 10)]

parser = StringParser()
# test = "Tens of thousands of Greeks rallied on Monday to back their leftwing government\'s rejection of a tough international bailout after a clash with foreign lenders pushed Greece close to financial chaos and forced a shutdown of its banking system."

# text = parser.parse(test, False)
#
# article_words = text['text']

stems = {}
pages = {}

categories = {}

article_words = [('ariana', 1), ('grande', 1)]

for word, frequency in article_words:
    print(word)
    with connection.cursor() as cursor:
        cursor.execute(category_count_query, (word,))
        try:
            stem_id, category_count = cursor.fetchone()
        except TypeError:
            continue

        w = frequency * log(N_category / category_count, 10)
        stem = {'weight': w, 'word': word}

        stems[stem_id] = stem

        cursor.execute(get_stems_query, (stem_id,))

        for page_id, page_title, stem_id, stem_word in cursor:
            try:
                page = pages[page_id]
                page['stems'][stem_id] = stem_word
                page['weight'] += stem['weight']
            except KeyError:
                page = {'title': page_title, 'stems': {stem_id: stem_word}, 'weight': 0.0}

            pages[page_id] = page

i = 0
print(pages)
for page_id, page in pages.items():

    i+=1

    intersection = len(list(set(stems.keys()).intersection(page['stems'].keys())))
    # print(intersection)

    if intersection > len(list(page['stems'].keys())) - 2:

        with connection.cursor() as cursor:
            cursor.execute(get_categories_query, [page_id])
            for category_id, category_title in cursor:
                try:
                    category = categories[category_id]
                    category['weight'] += page['weight']
                except KeyError:
                    categories[category_id] = {'title': category_title, 'weight': 0.0}


pprint(sorted([c for i, c in categories.items() if c['weight'] > 0.0], key=operator.itemgetter('weight'), reverse=True)[:30])

