#!/usr/bin/env python

import os
from glob import glob
import random
import re
import regex
import datetime


INDIR = '/home/dm/myprojects/markdown-samples'
OUTDIR = '/home/dm/myprojects/Pyramid-1.3--Py3.2--env/PySite/var/site-templates/default/blog'

AUTHORS = [
    'Leila Abouzeid',
    'Dritëro Agolli',
    'Johann Heinrich Jung',
    'Nichita Stănescu',
    '신경숙',
    'Евге́ния Соломо́новна Ги́нзбург'
]
L_AUTHORS = len(AUTHORS)
random.shuffle(AUTHORS)

DATE_MIN = datetime.date(1968, 1, 1).toordinal()
DATE_MAX = datetime.date.today().toordinal()

find_words = re.compile(r'\w+').findall
RE_SENTENCE = re.compile(r'[^.!?\n。]+')

REGEX_SENTENCE_MARK = regex.compile(r'\p{Sentence_Break=STerm}|\p{Sentence_Break=ATerm}')


def find_sentences(s):
    return [x.strip().replace("\n", '') for x in REGEX_SENTENCE_MARK.split(s) if len(x.strip()) > 0]


def meta2md(m):
    a = []
    for k, v in m.items():
        if isinstance(v, list):
            v = ",".join(v)
        a.append(k.capitalize() + ': ' + v)
    return "\n".join(a)


class Runner(object):
    def __init__(self):
        self._images = []
        self._codes = []
        self._texts = []

    def _collect(self):
        self._images = list(map(os.path.basename, glob(INDIR+'/img/*')))
        self._codes = list(map(os.path.basename, glob(INDIR+'/code/*')))
        self._collect_txt()
        self._collect_md()

    def _collect_md(self):
        ff = glob(INDIR+'/*.md')
        ff.sort()
        for f in ff:
            with open(f) as fh:
                ss = fh.readlines()
            s = ''.join(ss)
            words = find_words(s)
            meta = dict(
                author=random.choice(AUTHORS),
                pubdate=self._find_pubdate(),
                title=ss[0].strip(),
                relfn=os.path.basename(f)
            )
            meta['category'], meta['tags'] = self._find_cat_tags(words)
            meta['slug'] = re.sub(r'\W', '-', meta['title']).strip('-')
            self._texts.append([meta, s])

    def _collect_txt(self):
        ff = glob(INDIR+'/*.txt')
        ff.sort()
        for f in ff:
            if 'Morse' in f:
                continue
            with open(f) as fh:
                s = fh.read()
            words = find_words(s)
            sentences = find_sentences(s)
            meta = dict(
                author=random.choice(AUTHORS),
                pubdate=self._find_pubdate(),
                title=self._find_title(sentences),
                relfn=os.path.basename(f)[:-3] + 'md'
            )
            meta['category'], meta['tags'] = self._find_cat_tags(words)
            meta['slug'] = re.sub(r'\W', '-', meta['title']).strip('-')
            self._texts.append([meta, s])

    def _find_pubdate(self):
        return datetime.date.fromordinal(
            random.randint(DATE_MIN, DATE_MAX)).isoformat()

    def _find_cat_tags(self, words):
        ww = [w for w in words if len(w) > 4]
        if len(ww) < 8:
            tags = ww[:]
            random.shuffle(tags)
            ww = words
        else:
            tags = random.sample(ww, random.randint(3, 8))
        while True:
            category = random.choice(ww)
            if not category in tags:
                break
        return (category, tags)

    def _find_title(self, sentences):
        # Maybe there are no short sentences, search only 20 times
        for i in range(50):
            s = random.choice(sentences)
            if 10 >= len(s) <= 32:
                break
        if len(s) > 32:
            s = s[:32]
        return s.title()


    def run(self):
        self._collect()
        self._cattags2()
        self._inject_imgs()
        self._inject_code()
        self._write()

    def _inject_imgs(self):
        n = len(self._texts)
        ii = random.sample(range(n), round(n/2.0))
        for i in ii:
            pars = self._texts[i][1].split("\n\n")
            pp = random.sample(range(1, len(pars)), random.randint(0, 2))
            for p in pp:
                pic = random.choice(self._images)
                #pars.insert(p, '<img src="{{{{asset_url(\'img/blog/{1}\')}}}}" alt="{0}" title="Picture {2}">'.format(
                pars.insert(p, '![{0}]({{{{asset_url\(\'img/blog/{1}\'\)}}}} "Image tag by Markdown: {2}")'.format(
                    pic, pic, pic))
            if pp:
                self._texts[i][1] = "\n\n".join(pars)
                self._texts[i][0]['tags'].append('IMAGE')

    def _inject_code(self):
        n = len(self._texts)
        ii = random.sample(range(n), round(n/2.0))
        for i in ii:
            pars = self._texts[i][1].split("\n\n")
            p = random.randint(1, len(pars))
            fn = random.choice(self._codes)
            _, ext = os.path.splitext(fn)
            lang = ext[1:]
            if lang == 'lisp':
                lang = 'common-lisp'
            code = ['    :::' + lang + "\n"]
            with open(INDIR + '/code/' + fn) as fh:
                for s in fh:
                    s = s.expandtabs(4)
                    s = '    ' + s
                    code.append(s)
            pars.insert(p, ''.join(code))
            self._texts[i][1] = "\n\n".join(pars)
            self._texts[i][0]['tags'].append('CODE')
            self._texts[i][0]['tags'].append(lang)



    def _cattags2(self):
        ww = []
        for m, txt in self._texts:
            ww += find_words(txt)
        ww = random.sample([w for w in set(ww) if len(w) > 3], round(len(self._texts)*0.5))
        for m, txt in self._texts:
            tags = random.sample(ww, random.randint(3, 8))
            for i in range(50):
                categ = random.choice(ww)
                if not categ in tags:
                    break
            m['category'] = categ
            m['tags'] = tags

    def _write(self):
        for m, txt in self._texts:
            fn = OUTDIR + '/' + m['relfn']
            with open(fn, 'w', encoding="utf-8") as fh:
                fh.write(meta2md(m) + "\n\n")
                fh.write(txt)


if __name__ == '__main__':
    r = Runner()
    r.run()
    for x in r._texts:
        if 'CODE' in x[0]['tags']:
            print(x[0]['relfn'])

