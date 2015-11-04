import time

__author__ = 'James'

from wikipedia_stuff.tests import WikiParser

w = WikiParser()
toc = time.time()
w.load_queue(13099910)
tic = time.time()
print("Done in:", tic-toc, "s")