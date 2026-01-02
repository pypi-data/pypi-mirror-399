# Original setup.py template: https://github.com/kennethreitz/setup.py

from setuptools import find_packages, setup, Command
from importlib import util as importlib_util
from subprocess import call
from shutil import rmtree
from os import path
import sys

NAME = 'staticjinjaplus'
DESCRIPTION = 'A sweet spot between staticjinja and a full-blown static site generator.'
URL = 'https://github.com/EpocDotFr/staticjinjaplus'
EMAIL = 'contact.nospam@epoc.nospam.fr'
AUTHOR = 'Maxime "Epoc" Gross'
REQUIRES_PYTHON = '>=3.10'
VERSION = None  # Pulled from staticjinjaplus/__version__.py

REQUIRED = [
    'staticjinja~=5.0',
    'webassets~=3.0',
    'htmlmin~=0.1',
    'rjsmin~=1.2',
    'environs~=14.0',
    'markdown~=3.6',
]

EXTRAS = {
    'dev': {
        'build~=1.2',
        'twine~=6.0',
        'setuptools>=69',
        'mkdocs~=1.6'
    }
}

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: OS Independent',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Topic :: Text Processing :: Markup :: XML',
    'Topic :: Text Processing :: Markup :: HTML',
    'Topic :: Text Processing :: Markup :: Markdown',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Intended Audience :: Developers',
]

PROJECT_URLS = {
    'Documentation': 'https://epocdotfr.github.io/staticjinjaplus/',
    'Source code': 'https://github.com/EpocDotFr/staticjinjaplus',
    'Issue tracker': 'https://github.com/EpocDotFr/staticjinjaplus/issues',
    'Changelog': 'https://github.com/EpocDotFr/staticjinjaplus/releases',
}

KEYWORDS = ['static', 'website', 'site', 'generator', 'staticjinja', 'jinja', 'jinja2']

here = path.abspath(path.dirname(__file__))

try:
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}

if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")

    spec = importlib_util.spec_from_file_location('__version__', path.join(here, project_slug, '__version__.py'))
    module = importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)

    about['__version__'] = module.__version__
else:
    about['__version__'] = VERSION


class UploadCommand(Command):
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')

            rmtree(path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel distribution…')

        call('"{0}" -m build --sdist --wheel'.format(sys.executable), shell=True)

        self.status('Uploading the package to PyPI via Twine…')

        call('twine upload dist/*', shell=True)

        self.status('Pushing git tags…')

        call('git tag v{0}'.format(about['__version__']), shell=True)
        call('git push --tags', shell=True)

        exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='DBAD',
    entry_points={
        'console_scripts': [
            'staticjinjaplus = staticjinjaplus.cli:cli',
        ]
    },
    classifiers=CLASSIFIERS,
    cmdclass={
        'upload': UploadCommand,
    },
    project_urls=PROJECT_URLS,
    keywords=KEYWORDS
)
