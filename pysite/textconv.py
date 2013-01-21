import markdown
from typogrify.filters import typogrify


class Converter(object):
    def __init__(self, rc):
        self.rc = rc
        self.fn = None
        self.input_ = None
        self.output = None
        self.meta = None
        self.error = None

    def convert(self, fn_or_text):
        if isinstance(fn_or_text, str):
            # TODO Obtain metadata from filename
            self.fn = fn_or_text
            with open(self.fn, 'r', encoding='utf-8') as fh:
                self.input_ = fh.read()
        else:
            self.fn = None
            self.input_ = fn_or_text
        self._convert()
        self._postprocess()

    def _convert(self):
        raise Exception("Implement this in child class")

    def _postprocess(self):
        if self.rc.get('typogrify', False):
            if self.output:
                self.output = typogrify(self.output)
            if 'title' in self.meta:
                self.meta['title'] = typogrify(self.meta['title'])
        if 'tags' in self.meta:
            self.meta['tags'] = [t.strip() for t in self.meta['tags'].split(',')]



class Markdown(Converter):

    def __init__(self, rc):
        super().__init__(rc)
        rcmd = {
            'extensions': [
                'abbr',
                'attr_list',
                'codehilite',
                'def_list',
                'fenced_code',
                'footnotes',
                'meta',
                'sane_lists',
                'smart_strong',
                'tables',
                'toc'
            ],
            'extension_configs': { },
            'output_format': 'html5',
            'safe_mode': False,
            'html_replacement_text': '!!!!FOOOOOOO!!!!'
        }
        if 'markdown' in rc and rc['markdown']:
            rcmd.update(rc['markdown'])
        #from pprint import pprint; pprint(rcmd); raise Exception('foo')
        self._md = markdown.Markdown(**rcmd)

    def _convert(self):
        try:
            self.error = None
            self.output = self._md.convert(self.input_)
            # Markdown meta lowercases keys
            self.meta = {}
            for k, v in self._md.Meta.items():
                self.meta[k.lower()] = "|".join(v)
        except Exception as exc:
            self.error = exc
