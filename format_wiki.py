# -*- coding: utf-8 -*-
from gensim.corpora.wikicorpus import extract_pages,filter_wiki
import bz2file
import re
#import opencc
from tqdm import tqdm
import codecs

wiki = extract_pages(bz2file.open('zhwiki-latest-pages-articles.xml.bz2'))

def wiki_replace(d):
    s = d[1]
    s = re.sub(':*{\|[\s\S]*?\|}', '', s)
    s = re.sub('[\s\S]*?', '', s)
    s = re.sub('(.){{([^{}\n]*?\|[^{}\n]*?)}}', '\\1[[\\2]]', s)
    s = filter_wiki(s)
    s = re.sub('\* *\n|\'{2,}', '', s)
    s = re.sub('\n+', '\n', s)
    s = re.sub('\n[:;]|\n +', '\n', s)
    s = re.sub('\n==', '\n\n==', s)
    s = u'\u3010' + d[0] + u'\u3011\n' + s
    return s.strip()

i = 0
f = codecs.open('wiki.txt', 'w', encoding='utf-8')
w = tqdm(wiki, desc=u'get 0 article')
for d in w:
    if not re.findall('^[a-zA-Z]+:', d[0]) and d[0] and not re.findall(u'^#', d[1]):
        s = wiki_replace(d)
        f.write(s+'\n\n\n')
        i += 1
        if i % 100 == 0:
            w.set_description(u'get %d articles'%i)

f.close()