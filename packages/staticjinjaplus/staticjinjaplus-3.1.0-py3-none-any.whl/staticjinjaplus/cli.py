from staticjinjaplus import config, collect_templates, staticjinja_helpers, jinja_helpers, __generator__
from staticjinjaplus.http import EnhancedThreadingHTTPServer, SimpleEnhancedHTTPRequestHandler
from webassets import Environment as AssetsEnvironment
from staticjinja import Site, logger
from jinja2 import select_autoescape
from argparse import ArgumentParser
from shutil import copytree, rmtree
from os import makedirs, path
from environs import Env


def build(watch: bool = False) -> None:
    """Build the site"""
    webassets_cache = path.join(config['ASSETS_DIR'], '.webassets-cache')

    makedirs(webassets_cache, exist_ok=True)
    makedirs(config['TEMPLATES_DIR'], exist_ok=True)
    makedirs(config['OUTPUT_DIR'], exist_ok=True)
    makedirs(config['STATIC_DIR'], exist_ok=True)
    makedirs(config['ASSETS_DIR'], exist_ok=True)

    logger.info('Copying static files from "{STATIC_DIR}" to "{OUTPUT_DIR}"...'.format(**config))

    copytree(
        config['STATIC_DIR'],
        config['OUTPUT_DIR'],
        dirs_exist_ok=True
    )

    logger.info('Building from "{TEMPLATES_DIR}" to "{OUTPUT_DIR}"...'.format(**config))

    rules = [
        r for r in [
            (r'.*\.(xml|html|rss|atom)', staticjinja_helpers.minify_xml_template) if config['MINIFY_XML'] else None,
            (r'.*\.json', staticjinja_helpers.minify_json_template) if config['MINIFY_JSON'] else None,
            (r'.*\.md', staticjinja_helpers.render_markdown_template),
        ] if r is not None
    ]

    jinja_globals = {
        'config': config,
        'absurl': jinja_helpers.absurl,
        'embed': jinja_helpers.embed,
        'collected': list(collect_templates()),
        '__generator__': __generator__,
    }

    jinja_globals.update(config['JINJA_GLOBALS'])

    jinja_filters = {
        'tojsonm': jinja_helpers.tojsonm,
        'dictmerge': jinja_helpers.dictmerge,
    }

    jinja_filters.update(config['JINJA_FILTERS'])

    contexts = [
        (r'.*\.md', staticjinja_helpers.convert_markdown_file)
    ]

    if config['CONTEXTS']:
        contexts.extend(config['CONTEXTS'])

    jinja_extensions = [
        'webassets.ext.jinja2.AssetsExtension',
    ]

    jinja_extensions.extend(config['JINJA_EXTENSIONS'])

    site = Site.make_site(
        searchpath=config['TEMPLATES_DIR'],
        outpath=config['OUTPUT_DIR'],
        mergecontexts=True,
        env_globals=jinja_globals,
        filters=jinja_filters,
        contexts=contexts,
        rules=rules or None,
        extensions=jinja_extensions,
        env_kwargs={
            'trim_blocks': True,
            'lstrip_blocks': True,
            'autoescape': select_autoescape(enabled_extensions=('html', 'xml', 'rss', 'atom')),
        }
    )

    site.env.assets_environment = AssetsEnvironment(
        directory=config['OUTPUT_DIR'],
        url='/',
        cache=webassets_cache
    )

    site.env.assets_environment.append_path(config['ASSETS_DIR'])

    for name, args, kwargs in config['WEBASSETS_BUNDLES']:
        site.env.assets_environment.register(name, *args, **kwargs)

    site.render(watch)


def clean() -> None:
    """Delete and recreate the output directory"""
    logger.info('Deleting and recreating "{OUTPUT_DIR}"...'.format(**config))

    if path.isdir(config['OUTPUT_DIR']):
        rmtree(config['OUTPUT_DIR'])

    makedirs(config['OUTPUT_DIR'], exist_ok=True)


def publish() -> None:
    """Build the site for production"""
    logger.info('Overriding some configuration values from environment variables...')

    env = Env()

    config.update({
        'BASE_URL': env.str('BASE_URL'),
        'MINIFY_XML': env.bool('MINIFY_XML', config['MINIFY_XML']),
        'MINIFY_JSON': env.bool('MINIFY_JSON', config['MINIFY_JSON']),
    })

    clean()
    build()


def serve() -> None:
    """Serve the rendered site directory through HTTP"""
    with EnhancedThreadingHTTPServer(
            ('', config['SERVE_PORT']),
            SimpleEnhancedHTTPRequestHandler,
            directory=config['OUTPUT_DIR']
    ) as server:
        msg = 'Serving "{OUTPUT_DIR}" on http://localhost:{SERVE_PORT}/'.format(**config)

        if server.has_dualstack_ipv6:
            msg += ' and http://[::1]:{SERVE_PORT}/'.format(**config)

        logger.info(msg)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def cli() -> None:
    arg_parser = ArgumentParser(
        description='The staticjinjaplus CLI which should be your main and only way to interact with staticjinjaplus.'
    )

    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version=__generator__
    )

    command_arg_parser = arg_parser.add_subparsers(dest='command', required=True)

    command_arg_parser.add_parser('build', help='Build the site')

    command_arg_parser.add_parser('watch', help='Build the site and watch for templates changes')

    command_arg_parser.add_parser('clean', help='Delete and recreate the output directory')

    command_arg_parser.add_parser('publish', help='Build the site for production')

    command_arg_parser.add_parser('serve', help='Serve the output directory through HTTP')

    args = arg_parser.parse_args()

    if args.command == 'build':
        build()
    elif args.command == 'watch':
        build(True)
    elif args.command == 'clean':
        clean()
    elif args.command == 'publish':
        publish()
    elif args.command == 'serve':
        serve()
