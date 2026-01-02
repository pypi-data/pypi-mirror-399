from staticjinjaplus.__version__ import __version__ as staticjinjaplus_version
from staticjinja import __version__ as staticjinja_version
from typing import Dict, Any, Iterator, Tuple
from importlib import util as importlib_util
from glob import iglob
from os import path
import markdown.extensions.meta as markdown_meta

__generator__ = f'staticjinjaplus {staticjinjaplus_version} (staticjinja {staticjinja_version})'

# Set default config values
_serve_port = 8080

config: Dict[str, Any] = {
    'SERVE_PORT': _serve_port,
    'BASE_URL': f'http://localhost:{_serve_port}/',
    'MINIFY_XML': False,
    'MINIFY_JSON': False,
    'TEMPLATES_DIR': 'templates',
    'OUTPUT_DIR': 'output',
    'STATIC_DIR': 'static',
    'ASSETS_DIR': 'assets',
    'CONTEXTS': [],
    'WEBASSETS_BUNDLES': [],
    'JINJA_GLOBALS': {},
    'JINJA_FILTERS': {},
    'JINJA_EXTENSIONS': [],
    'MARKDOWN_EXTENSIONS': {},
    'MARKDOWN_DEFAULT_PARTIAL': None,
    'USE_HTML_EXTENSION': True,
}


def load_config() -> None:
    """Load configuration from both `config.py` in the directory where staticjinjaplus is executed and environment
    variables, returning a dict representation of this configuration. Only uppercase variables are loaded"""
    global config

    # Load and override default config values from config.py, if the file exists
    try:
        spec = importlib_util.spec_from_file_location('config', 'config.py')
        actual_config = importlib_util.module_from_spec(spec)
        spec.loader.exec_module(actual_config)

        config.update({
            k: v for k, v in vars(actual_config).items() if k.isupper()
        })
    except FileNotFoundError:
        pass


def smart_build_url(filename: str) -> Tuple[str, str]:
    """Build a pretty URL (if configured so) pointing to an HTML file"""
    _, ext = path.splitext(filename)
    ext = ext.lstrip('.')

    url = '/' + filename.lstrip('/')

    if url.endswith(('/index.html', '/index.md')):
        url = url.removesuffix('/index.html').removesuffix('/index.md') + '/'
    elif ext in ('html', 'md'):
        if not config['USE_HTML_EXTENSION']:
            url, _ = path.splitext(url)
        elif ext == 'md':
            url, = url.removesuffix('.md') + '.html'

    return url, ext


def collect_templates() -> Iterator[Dict[str, Any]]:
    """Iterates over all valid files found in the templates directory and return several kind of information about
    them."""
    for filename in iglob(
        f'**/[!_]*.*',
        root_dir=config['TEMPLATES_DIR'],
        recursive=True
    ):
        filename = path.normpath(filename).replace('\\', '/')

        url, ext = smart_build_url(filename)

        data = {
            'source': filename,
            'type': ext,
            'url': url,
        }

        if ext == 'md':
            data['meta'] = {}

            first_line = True

            with open(path.join(config['TEMPLATES_DIR'], filename), 'r', encoding='utf-8') as f:
                # The following code has been borrowed and adapted from the meta extension of Python's markdown package:
                # https://github.com/Python-Markdown/markdown/blob/master/markdown/extensions/meta.py
                for line in f:
                    if first_line:
                        first_line = False

                        if markdown_meta.BEGIN_RE.match(line):
                            continue

                    m1 = markdown_meta.META_RE.match(line)

                    if line.strip() == '' or markdown_meta.END_RE.match(line):
                        break

                    if m1:
                        key = m1.group('key').lower().strip()
                        value = m1.group('value').strip()

                        try:
                            data['meta'][key] += f'\n{value}'
                        except KeyError:
                            data['meta'][key] = value
                    else:
                        m2 = markdown_meta.META_MORE_RE.match(line)

                        if m2 and key:
                            value = m2.group('value').strip()

                            data['meta'][key] += f'\n{value}'
                        else:
                            break

        yield data


load_config()
