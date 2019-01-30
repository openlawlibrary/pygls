############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
import os

from setuptools import find_packages, setup

PACKAGE_NAME = 'pygls'
VERSION = '0.7.2'
AUTHOR = 'Open Law Library'
AUTHOR_EMAIL = 'info@openlawlib.org'
DESCRIPTION = 'a pythonic generic language server (pronounced like "pie glass").'
KEYWORDS = 'python pythonic generic language server protocol'
LICENSE = 'Apache 2.0'
URL = 'https://github.com/openlawlibrary/pygls/tree/master/'

packages = find_packages()

print('packages:', packages)

package_root_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(package_root_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

docs_require = [
    "sphinx==1.8.2",
    "sphinx_rtd_theme==0.4.2"
]

tests_require = [
    "bandit==1.5.1",  # Run locally: bandit -r ./pygls
    "flake8==3.7.1",  # Run locally: flake8
    "mock==2.0.0",
    "pytest==4.0.2",
    "pytest-asyncio==0.9.0"
]

# pip install pygls
# pip install pygls pygls[docs]
# pip install pygls pygls[test]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    license=LICENSE,
    packages=packages,
    include_package_data=True,
    data_files=[
        ('lib/site-packages/pygls', [
            './CHANGELOG.md',
            './LICENSE.txt',
            './README.md',
            'ThirdPartyNotices.txt'
        ])
    ],
    zip_safe=False,
    install_requires=[],
    extras_require={
        'docs': docs_require,
        'test': tests_require,
    },
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
