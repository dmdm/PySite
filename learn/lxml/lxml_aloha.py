#!/usr/bin/env python

from lxml import html


class Replacer(object):

    MARKER = '~+~' * 5 + '#' + '~+~' * 5

    def __init__(self):
        self.fragments = None
        self.newfragments = None

    def load_page(self, fn):
        with open(fn, 'r', encoding='utf-8') as fh:
            txt = fh.read()
        self.parse_page(txt)

    def parse_page(self, txt):
        self.fragments = None
        self.newfragments = None
        # Parse into fragments (plural), not into a single fragments.
        # In the latter case lxml would try to create valid HTML:
        # - if txt has no root element, txt is enclosed in 'div'
        # - if txt starts with strings (not tags), these are enclosed
        #   in 'p'
        # To avoid this, we let lxml parse txt into fragments which
        # preserves leading text.
        self.fragments = html.fragments_fromstring(txt)

    def _replace_with_marker(self, keys):
        self.newfragments = []
        # Look through all fragments if an element has an ID.
        # If so, look if we have new content for that ID, and if so
        # mark it.
        for fr in self.fragments:
            if not isinstance(fr, html.HtmlElement):
                self.newfragments.append(fr)
                continue
            # iter() loops through current item and all of its
            # descendants.
            # If element has no ID or an ID for which we have no new content,
            # keep element as-is.
            for e in fr.iter():
                try:
                    k = e.attrib['id']
                except KeyError:
                    pass
                else:
                    if k in keys:
                        # Clear element but keep its attributes
                        attr = {}
                        for ak, av in e.attrib.items():
                            attr[ak] = av
                        e.clear()
                        e.attrib.update(attr)
                        # Set marker
                        e.text = self.MARKER.replace('#', k)
            self.newfragments.append(fr)

    def _newfragments_tostring(self, content):
        a = []
        for s in self.newfragments:
            if isinstance(s, str):
                a.append(s)
            else:
                a.append(html.tostring(s, method='html',
                    pretty_print=True, encoding=str))
        s = "".join(a)
        for k, v in content.items():
            m = self.MARKER.replace('#', k)
            s = s.replace(m, "\n" + v.strip() + "\n")
        return s

    def replace(self, content):
        self._replace_with_marker(content.keys())
        return self._newfragments_tostring(content)


# This simulates getting the content from POST:
# We obtain a dict, keys are the div IDs, values are the new content.
def load_content(here):
    content = {}
    for fn in glob.glob(os.path.join(here, '*.html')):
        key, _ = os.path.splitext(os.path.basename(fn))
        with open(fn, 'r', encoding='utf-8') as fh:
            content[key] = fh.read()
    content['foo'] = 'BAAAAAAAAAAAR'
    return content


if __name__ == '__main__':
    import glob
    import os
    here = os.path.dirname(__file__)
    content = load_content(here)
    fn = os.path.join(here, 'index.jinja2')
    r = Replacer()
    r.load_page(fn)
    print(r.replace(content))
