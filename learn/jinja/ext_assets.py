# -*- coding: utf-8 -*-

import jinja2 as jj
import jinja2.ext

#from pprint import pprint

class AssetsEnvironment(object):
    pass

class AssetsExtension(jinja2.ext.Extension):

    tags = set(['assets'])

    def __init__(self, environment):
        super(AssetsExtension, self).__init__(environment)

        environment.extend(
            assets_environment=None,
        )

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # we only listen to ``'assets'`` so this will be a name token with
        # `assets` as value.  We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno
        # parser.stream.current is now the first argument of the tag or None if
        # no arguments are given.
        free_args = []
        flags = []
        kw = {}
        allowed_kw = ['bar', 'egon']
        allowed_flags = ['foo', 'zip']
        first = True
        while parser.stream.current.type != 'block_end':
            if not first:
                parser.stream.expect('comma')
            first = False
            # Token is either a name...
            if parser.stream.current.test('name'):
                # Lookahead to see if this is an assignment (an option)
                # Its RHS is the value of the name
                if parser.stream.look().test('assign'):
                    k = next(parser.stream).value
                    parser.stream.skip()
                    v = parser.parse_expression()
                    if k in allowed_kw:
                        kw[k] = v
                    else:
                        parser.fail("Unexpected keyword: '{0}'".format(k))
                # No assignment, so treat this token as a flag
                else:
                    flag = next(parser.stream).value
                    if flag in allowed_flags:
                        flags.append(jj.nodes.Const(flag))
                    else:
                        parser.fail("Unexpected flag: '{0}'".format(flag))
            # ...or a free argument
            else:
                free_args.append(parser.parse_expression())

        ###print("*** Keywords"); pprint(kw)
        ###print("*** free_args"); pprint(free_args)
        ###print("*** flags"); pprint(flags)
        # Parse the contents of this tag
        body = parser.parse_statements(['name:endassets'], drop_needle=True)
        ###print("### BODY")
        ###print(body)
        
        block_vars = [jj.nodes.Name('ASSET_URL', 'store'),
                      jj.nodes.Name('EXTRA', 'store')]
        block_defaults = [jj.nodes.Const('DEFAULT')]
        call_args = [
            jj.nodes.Dict([jj.nodes.Pair(jj.nodes.Const(k), v) for k, v in kw.items()]),
            jj.nodes.List(flags),
            jj.nodes.List(free_args)
        ]
        call = self.call_method('_render_assets', args=call_args)
        call_block = jj.nodes.CallBlock(call, block_vars, block_defaults, body)
        call_block.set_lineno(lineno)
        return call_block



    def _render_assets(self, kw, flags, free_args, caller=None):
        env = self.environment.assets_environment
        if env is None:
            raise RuntimeError('No assets environment configured in '+
                               'Jinja2 environment')

        #result = caller(str(kw), "|".join(free_args)+"+"+"|".join(flags))
        result = caller(str(kw))
        return result
    
