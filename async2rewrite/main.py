import re

import astunparse

from .transformers import *


def get_result(code, **kwargs):

    remove_parens = kwargs.pop('remove_parens', False)
    stats = kwargs.pop('stats', False)
    include_ast = kwargs.pop('include_ast', False)

    def snowflake_repl(match):
        return str(int(match.group(1)))

    code = re.sub("""['\"](\d{17,18,19})['\"]""", snowflake_repl, code)  # str snowflakes to int snowflakes

    expr_ast = ast.parse(code)

    if stats:
        return find_stats(expr_ast)

    new_ast = DiscordTransformer().generic_visit(expr_ast)

    unparsed = astunparse.unparse(new_ast)

    unparsed = unparsed.replace('ctx.message.guild', 'ctx.guild').replace('ctx.message.author', 'ctx.author')
    unparsed = unparsed.replace('ctx.message.channel', 'ctx.channel')

    final_ast = ast.parse(unparsed)

    if remove_parens:
        def parens_repl(match):
            return match.group(1)

        unparsed = re.sub("""(?<=\s)\((.+)\)(?=[\s:])""", parens_repl, unparsed) # this can cause some issues

    if include_ast:
        return unparsed, final_ast
    else:
        return unparsed


def from_file(file_path, **kwargs):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
        return get_result(code, **kwargs)


def from_text(text, **kwargs):
    return get_result(text, **kwargs)
