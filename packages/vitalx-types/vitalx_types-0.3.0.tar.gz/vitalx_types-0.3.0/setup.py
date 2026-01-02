# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vitalx', 'vitalx.types']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'vitalx-types',
    'version': '0.3.0',
    'description': 'Vital Horizon AI common types package',
    'long_description': 'Vital Horizon AI common types package\n\n* [Product documentation](https://docs.tryvital.io/api-reference/horizon-ai/)\n\n## License\n\nAGPL 3.0. Refer to [the LICENSE](/LICENSE.txt) for more information.\n',
    'author': 'Vital',
    'author_email': 'developers@tryvital.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.tryvital.com/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
