# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vitalx', 'vitalx.vitalx']

package_data = \
{'': ['*']}

install_requires = \
['vitalx-aggregation>=0.1,<0.2',
 'vitalx-cli-auth>=0.1,<0.2',
 'vitalx-cli>=0.1,<0.2',
 'vitalx-types<1.0']

setup_kwargs = {
    'name': 'vitalx',
    'version': '0.3.0',
    'description': 'Vital Horizon AI SDK',
    'long_description': 'Vital Horizon AI SDK\n\n* [Product documentation](https://docs.tryvital.io/api-reference/horizon-ai/)\n',
    'author': 'Vital',
    'author_email': 'developers@tryvital.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.tryvital.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
