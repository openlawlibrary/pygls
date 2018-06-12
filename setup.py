import os
from setuptools import setup, find_packages

PACKAGE_NAME = 'pygls'
VERSION = '0.1.0'
AUTHOR = 'Open Law Library'
AUTHOR_EMAIL = 'info@openlawlib.org'
DESCRIPTION = 'Python Generic Language Server (pronounced like "spy glass").'
KEYWORDS = 'python generic language server protocol'
LICENSE = 'All rights reserved'
URL = 'https://github.com/openlawlibrary/pygls/tree/master/'

packages = find_packages()

print('packages:', packages)

package_root_dir = os.path.abspath(os.path.dirname(__file__))

tests_require = [
    "pytest==3.5.0",
]

# pip install pygls
# pip install pygls pygls[test]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    license=LICENSE,
    packages=packages,
    include_package_data=True,
    data_files=[
        ('Lib/site-packages/pygls', ['./CHANGELOG.md', './README.md', ])
    ],
    zip_safe=False,
    install_requires=[
        "semver==2.8.0",
    ],
    extras_require={
        'test': tests_require,
    },
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
