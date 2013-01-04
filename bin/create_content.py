#!/usr/bin/env python

import re
from glob import glob
import os
import random
import datetime

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

TAGS = [
    'человек',
    'год',
    'время',
    'рука',
    'дело',
    'раз',
    'глаз',
    'жизнь',
    'день',
    'голова',
    'друг',
    'дом',
    'слово',
    'место',
    'лицо',
    'сторона',
    'нога',
    'дверь',
    'работа',
    'земля',
    'конец',
    'час',
    'голос',
    'город',
    'вода',
    'стол',
    'ребёнок',
    'сила',
    'отец',
    'женщина',
    'машина',
    'случай',
    'ночь',
    'мир',
    'вид',
    'ряд',
    'начало',
    'вопрос',
    'война',
    'деньги',
    'минута',
    'жена',
    'правда',
    'страна',
    'свет',
    'мать',
    'товарищ',
    'дорога',
    'окно',
    'комната',
	'크기',
	'큰',
	'깊은',
	'긴',
	'폭이 좁은',
	'짧은',
	'작은',
	'키가 큰',
	'두꺼운',
	'얇은',
	'넓은',
	'맛',
	'쓴',
	'신선한',
	'짠',
	'신(시큼한)',
	'매운',
	'달콤한',
	'특성',
	'나쁜',
	'깨끗한',
	'어두운',
	'어려운',
	'더러운',
	'건조한',
	'쉬운',
	'비어있는/빈',
	'(가격이) 비싼',
	'빨리',
	'외국의',
	'가득한/완전한',
	'좋은',
	'딱딱한/어려운',
	'무거운',
	'값싼/바싸지 않은',
	'가벼운/밝은',
	'지역의/현지의',
	'새로운',
	'시끄러운',
    'Gebrauch',
    'Eis',
    'Hackfleisch',
    'Müsli',
    'Ungeheuer',
    'Abitur',
    'Alter',
    'Amt',
    'Angebot',
    'Aquarium',
    'Asyl',
    'Auge',
    'Ausland',
    'Aussehen',
    'Autohaus',
    'Bargeld',
    'Beet',
    'Bein',
    'Bekenntnis',
    'Bekleidungsgeschäft',
    'Besteck',
    'Bier',
    'Bild',
    'Blatt',
    'Blut',
    'Blütenblatt',
    'Bonbon',
    'Brett',
    'Brät',
    'Brötchen',
    'Bund',
    'Bußgeld',
    'Bügeleisen',
    'Chaos',
    'Croissant',
    'Datum',
    'Denken',
    'Dirndl',
    'Doppelbett',
    'Doppelzimmer',
    'Dorf',
    'Ursäkta',
    'Systembolaget',
    'Skål',
    'Korv',
    'Kanelbulle',
    'Fika',
    'Tunnelbana',
    'Tack så mycket',
    'En kopp kaffe',
    'Hej då'
]
L_TAGS = len(TAGS)
random.shuffle(TAGS)

CATEGORIES = random.sample(TAGS, 15)
L_CATEGORIES = len(CATEGORIES)

DATE_MIN = datetime.date(1968, 1, 1).toordinal()
DATE_MAX = datetime.date.today().toordinal()


def create_meta():
    m = dict(
        date=datetime.date.fromordinal(random.randint(DATE_MIN, DATE_MAX)).isoformat(),
        category=CATEGORIES[random.randint(0, L_CATEGORIES-1)],
        tags=",".join(random.sample(TAGS, random.randint(5, 15))),
        author=AUTHORS[random.randint(0, L_AUTHORS-1)],
    )
    return m


def meta2rst(m):
    a = []
    for k, v in m.items():
        a.append(':' + k + ': ' + v)
    return "\n".join(a)


def meta2md(m):
    a = []
    for k, v in m.items():
        a.append(k[0].capitalize() + k[1:] + ': ' + v)
    return "\n".join(a)

ROOTDIR = '/home/dm/myprojects'
OUTDIR = os.path.join(os.path.dirname(__file__), 'var', 'site-templates', 'default', 'blog')

def pylonsbook():
    INDIR = os.path.join(ROOTDIR, "pylonsbook.com/en/1.1/_sources")
    for a in glob(os.path.join(INDIR, '*.txt')):
        b = os.path.join(OUTDIR, os.path.basename(a)[:-3] + 'rst')
        with open(a, 'r', encoding='utf-8') as ha:
            with open(b, 'w', encoding='utf-8') as hb:
                m = create_meta()
                m['slug'] = b[:-4]
                hb.write(meta2rst(m) + "\n\n")
                for sa in ha:
                    sb = re.sub(r'(\.\.\s+\w+\s*::)', r'   "\1"', sa)
                    sb = re.sub(r':\w+:`[^`]+`', '', sb)
                    hb.write(sb)


def docutilstest():
    INDIR = os.path.join(ROOTDIR, "docutils.sourceforge.net/test/functional/input")
    for a in glob(os.path.join(INDIR, '*.txt')):
        b = os.path.join(OUTDIR, os.path.basename(a)[:-3] + 'rst')
        with open(a, 'r', encoding='utf-8') as ha:
            with open(b, 'w', encoding='utf-8') as hb:
                m = create_meta()
                m['slug'] = b[:-4]
                hb.write(meta2rst(m) + "\n\n")
                for sa in ha:
                    sb = re.sub(r'(\.\.\s+\w+\s*::)', r'   "\1"', sa)
                    sb = re.sub(r':\w+:`[^`]+`', '', sb)
                    hb.write(sb)


def gesetze():
    INDIR = os.path.join(ROOTDIR, "gesetze")
    L = len(INDIR)
    ff = []
    for root, dirs, files in os.walk(INDIR):
        for f in files:
            if f.startswith('.') or not f.endswith('.md'):
                continue
            ff.append(os.path.join(root, f)[L:].lstrip(os.path.sep))
    #ff = ['f/fleimstrv/index.md']
    MAX = 15 #len(ff)
    for a in random.sample(ff, MAX):
        b = os.path.join(OUTDIR, "_".join(a.split(os.path.sep)))
        a = os.path.join(INDIR, a)
        with open(a, 'r', encoding='utf-8') as ha:
            ss = ha.readlines()
            head = []
            for i, s in enumerate(ss):
                if s.startswith('---'):
                    if head:
                        break
                    else:
                        continue
                else:
                    if s.startswith('  '):
                        head[-1] = head[-1].rstrip() + ' ' + s.lstrip()
                    else:
                        head.append(s)
        with open(b, 'w', encoding='utf-8') as hb:
            m = create_meta()
            #m['slug'] = b[:-3]
            hb.write(meta2md(m) + "\n")
            for s in head:
                hb.write(s)
            for s in ss[i + 1:]:
                hb.write(s)


if __name__ == '__main__':
    #pylonsbook()
    #docutilstest()
    gesetze()
