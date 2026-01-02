from staticjinjaplus import config, smart_build_url
from typing import Dict, Optional, Any
from htmlmin import minify as htmlmin
from staticjinja import Site, logger
from markupsafe import Markup
from markdown import Markdown
from os import makedirs, path
from jinja2 import Template
from rjsmin import jsmin


class MarkdownWithMetadata(Markdown):
    Meta: Dict[str, Any]


_markdown_instance: Optional[MarkdownWithMetadata] = None


def minify_xml(out: str, site: Site, template_name: str, **kwargs) -> None:
    """Render, minify and save XML template output to a file"""
    with open(out, 'w', encoding=site.encoding) as f:
        f.write(
            htmlmin(
                site.get_template(template_name).render(**kwargs),
                remove_optional_attribute_quotes=False,
                remove_empty_space=True,
                remove_comments=True
            )
        )


def minify_xml_template(site: Site, template: Template, **kwargs) -> None:
    """Minify XML output (HTML/RSS/Atom) from a rendered Jinja template"""
    out = path.join(site.outpath, template.name)

    makedirs(path.dirname(out), exist_ok=True)

    minify_xml(out, site, template.name, **kwargs)


def minify_json_template(site: Site, template: Template, **kwargs) -> None:
    """Minify JSON output from a rendered Jinja template"""
    out = path.join(site.outpath, template.name)

    makedirs(path.dirname(out), exist_ok=True)

    with open(out, 'w', encoding=site.encoding) as f:
        f.write(
            jsmin(
                site.get_template(template.name).render(**kwargs)
            )
        )


def convert_markdown_file(template: Template) -> Dict:
    """Parse and convert a Markdown file to HTML and return the result, as well as metadata if any, to be used in the
    current context"""
    global _markdown_instance

    # Use a single Markdown parser instance for performance reasons
    if not _markdown_instance:
        extension_configs = {
            'markdown.extensions.extra': {},
            'markdown.extensions.meta': {},
        }

        if config['MARKDOWN_EXTENSIONS']:
            extension_configs.update(config['MARKDOWN_EXTENSIONS'])

        extensions = [
            e for e in extension_configs.keys()
        ]

        _markdown_instance = MarkdownWithMetadata(
            extensions=extensions,
            extension_configs=extension_configs,
            output_format='html5'
        )
    else:  # Reset the Markdown parser state before reusing it
        _markdown_instance.reset()

    with open(path.join(config['TEMPLATES_DIR'], template.name), 'r', encoding='utf-8') as f:
        filename = path.normpath(template.name).replace('\\', '/')
        url, _ = smart_build_url(filename)

        return {
            'markdown': {
                'converted': Markup(_markdown_instance.convert(f.read())),
                'source': filename,
                'url': url,
                'meta': {
                    k: '\n'.join(v) for k, v in _markdown_instance.Meta.items()
                }
            }
        }


def render_markdown_template(site: Site, template: Template, **kwargs) -> None:
    """Render a template partial from a converted Markdown file. Resulting HTML is minified as well if configured so"""
    render_template = kwargs.get('markdown', {}).get('meta', {}).get('partial', config['MARKDOWN_DEFAULT_PARTIAL'])

    if not render_template:
        logger.critical('Could not determine which template partial to use to render this Markdown template.')

        return

    render_template = render_template.lstrip('/')
    root, _ = path.splitext(template.name)
    out = path.join(site.outpath, f'{root}.html')

    makedirs(path.dirname(out), exist_ok=True)

    if config['MINIFY_XML']:
        minify_xml(out, site, render_template, **kwargs)
    else:
        site.get_template(render_template).stream(**kwargs).dump(out, encoding=site.encoding)
