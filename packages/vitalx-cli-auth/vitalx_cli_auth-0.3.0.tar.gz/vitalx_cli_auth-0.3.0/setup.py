# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vitalx', 'vitalx.cli_auth']

package_data = \
{'': ['*']}

install_requires = \
['filelock>=3.15,<4.0', 'requests>=2.32,<3.0']

setup_kwargs = {
    'name': 'vitalx-cli-auth',
    'version': '0.3.0',
    'description': 'Vital Horizon AI CLI authentication support package',
    'long_description': 'Vital Horizon AI CLI authentication support package\n\n* [Product documentation](https://docs.tryvital.io/api-reference/horizon-ai/)\n\n## License\n\nAGPL 3.0. Refer to [the LICENSE](/LICENSE.txt) for more information.\n',
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
