# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vitalx', 'vitalx.cli']

package_data = \
{'': ['*']}

install_requires = \
['typer>=0.12.5,<0.13.0', 'vitalx-cli-auth<1.0']

entry_points = \
{'console_scripts': ['vitalx-cli = vitalx.cli:main']}

setup_kwargs = {
    'name': 'vitalx-cli',
    'version': '0.3.0',
    'description': 'Vital Horizon AI command line tools',
    'long_description': 'Vital Horizon AI command line tools\n\n* [Product documentation](https://docs.tryvital.io/api-reference/horizon-ai/)\n\n## License\n\nAGPL 3.0. Refer to [the LICENSE](/LICENSE.txt) for more information.\n',
    'author': 'Vital',
    'author_email': 'developers@tryvital.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.tryvital.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
