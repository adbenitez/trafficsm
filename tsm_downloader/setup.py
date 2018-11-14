import re

from setuptools import find_packages, setup  # type: ignore

with open('tsm_downloader.py', 'rt', encoding='utf8') as fh:
    source = fh.read()
    match = re.search(r'__version__ = \'(.*?)\'', source, re.M)
    VERSION = match.group(1)  # type: ignore
    match = re.search(r'__author__ = \'(.*?)\'', source, re.M)
    AUTHOR = match.group(1)  # type: ignore

URL = 'https://github.com/adbenitez/tsm'
setup(
    name='tsm_downloader',
    version=VERSION,
    license='GPL3+',
    author=AUTHOR,
    author_email='asieldbenitez@gmail.com',
    description='See '+URL,
    url=URL,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ),
    keywords='downloader xml sqlite traffic',
    project_urls={
        'Documentation': URL,
        'Source': URL,
        'Tracker': URL+'/issues'
    },
    py_modules=['tsm_downloader'],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'tsm_downloader=tsm_downloader:main',
        ],
    }
)
