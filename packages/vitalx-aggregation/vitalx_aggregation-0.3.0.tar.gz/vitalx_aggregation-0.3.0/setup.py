# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vitalx', 'vitalx.aggregation']

package_data = \
{'': ['*']}

install_requires = \
['polars>=1.5,<2.0',
 'pydantic>=2.0,<3.0',
 'requests>=2.32,<3.0',
 'vitalx-types<1.0']

extras_require = \
{'cli-auth': ['vitalx-cli-auth<1.0']}

setup_kwargs = {
    'name': 'vitalx-aggregation',
    'version': '0.3.0',
    'description': 'Vital Horizon AI Aggregation API',
    'long_description': 'Vital Horizon AI Aggregation API\n\n* [Product documentation](https://docs.tryvital.io/api-reference/horizon-ai/)\n\n## License\n\nAGPL 3.0. Refer to [the LICENSE](/LICENSE.txt) for more information.\n',
    'author': 'Vital',
    'author_email': 'developers@tryvital.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.tryvital.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
