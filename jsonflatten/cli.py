"""Command-Line Interface."""

import sys
from collections import Mapping
from collections import Sequence

import click
import click._termui_impl
from click import argument
from click import option
from click import version_option

from jsoncore.cli import jsonfile
from jsoncut.cli import output
from jsoncore.sequence import Items
from jsoncut.tokenizer import parse_keystr
from jsoncut.treecrawler import find_keys

from jsonflatten.core import flatten_by_keys


def get_results(data, kwds):
    """Parse args and flatten the document."""
    if not kwds['flatten']:
        return flatten_by_keys(data, keys=None)
    else:
        args = ','.join(kwds['flatten'])
        data_ = Items([data] if kwds['slice_'] else data)
        keys = find_keys(data_.value, fullscan=True)
        keylists = parse_keystr(args, data.items, quotechar=kwds['quotechar'],
                                keys=keys)
        results = flatten_by_keys(data_.value, keys=['.'.join(key)
                                  for key in keylists])
    return results


@click.command(name='jsonflatten')
@option('-f', '--flatten', 'flatten', multiple=True,
        help=('Flatten only those specified keys generated from `jsoncut -l` '
              'option as a comma-separated list or idividually, i.e. '
              ' `-f7,9` or `-f7 -f9`'))
@option('-n', '--nocolor', is_flag=True, help='Disable syntax highlighting')
@option('-q', '--quotechar', 'quotechar', default='"',
        help='Quote character used in serialized data, defaults to \'"\'')
@option('-s', '--slice', 'slice_', is_flag=True, help='Disable sequencer')
@version_option(version='0.2', prog_name='JSON Flatten')
@jsonfile
@click.pass_context
def main(ctx, **kwds):
    """Specify which keys or whole document to flatten."""
    ctx.color = False if kwds['nocolor'] else True
    data = kwds['jsonfile']

    if isinstance(data, Mapping):
        results = get_results(data, kwds)
        output(ctx, results, indent=4, is_json=True)

    elif isinstance(data, Sequence):
        results = [get_results(item, kwds) for item in data]
        for res in results:
            output(ctx, res, indent=4, is_json=True)
