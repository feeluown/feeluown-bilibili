# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fuo_bilibili',
 'fuo_bilibili.api',
 'fuo_bilibili.api.schema',
 'fuo_bilibili.geetest']

package_data = \
{'': ['*'], 'fuo_bilibili': ['assets/*']}

install_requires = \
['beautifulsoup4', 'cachetools', 'feeluown>=3.8.14', 'pycryptodome']

entry_points = \
{'fuo.plugins_v1': ['bilibili = fuo_bilibili']}

setup_kwargs = {
    'name': 'feeluown-bilibili',
    'version': '0.3',
    'description': 'Bilibili provider for FeelUOwn player.',
    'long_description': '# Yet another bilibili plugin for FeelUOwn player\n\n![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/brucezhang1993/feeluown-bilibili/build.yml?style=for-the-badge)\n![AUR version](https://img.shields.io/aur/version/feeluown-bilibili?style=for-the-badge)\n![PyPI](https://img.shields.io/pypi/v/feeluown_bilibili?style=for-the-badge)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/feeluown_bilibili?style=for-the-badge)\n![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/brucezhang1993/feeluown-bilibili?style=for-the-badge)\n\n## Prerequisite\n\nYou must have [FeelUOwn](https://github.com/feeluown/FeelUOwn) first\n\n- Python >= 3.10  \n- FeelUOwn >= 3.8.7\n\n## Installation\n\n### PyPI\n\nhttps://pypi.org/project/feeluown-bilibili/\n\n```shell\npip install feeluown-bilibili\n```\n\n### Arch Linux\n\nhttps://aur.archlinux.org/packages/feeluown-bilibili\n\n```shell\nyay -S feeluown-bilibili\n```\n\n## Development\n\n```shell\npoetry install\npoetry run pre-commit install\n```\n\n## License\n\n[GPL-3.0](https://github.com/BruceZhang1993/feeluown-bilibili/blob/master/LICENSE.txt)\n\n## Special notes\n\n- Proudly use [danmaku2ass](https://github.com/m13253/danmaku2ass) to transform danmaku format\n- Proudly use [poetry](https://python-poetry.org/) as dependency manager tool\n',
    'author': 'Bruce Zhang',
    'author_email': 'zttt183525594@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/BruceZhang1993/feeluown-bilibili',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)

