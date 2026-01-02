# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_annotate']

package_data = \
{'': ['*']}

install_requires = \
['pipen>=1.0,<2.0']

setup_kwargs = {
    'name': 'pipen-annotate',
    'version': '1.0.1',
    'description': 'Use docstring to annotate pipen processes',
    'long_description': '# pipen-annotate\n\nUse docstring to annotate [pipen](https://github.com/pwwang/pipen) processes\n\n## Installation\n\n```shell\npip install -U pipen-annotate\n```\n\n## Usage\n\n```python\nfrom pprint import pprint\nfrom pipen import Proc\nfrom pipen_annotate import annotate\n\n\nclass Process(Proc):\n    """Short description\n\n    Long description\n\n    Input:\n        infile: An input file\n        invar: An input variable\n\n    Output:\n        outfile: The output file\n\n    Envs:\n        ncores (type=int): Number of cores\n    """\n    input = "infile:file, invar"\n    output = "outfile:file:output.txt"\n    args = {\'ncores\': 1}\n\nannotated = annotate(Process)\n# returns:\n{\'Envs\': {\'ncores\': {\'attrs\': {\'type\': \'int\'},\n                     \'help\': \'Number of cores\',\n                     \'name\': \'ncores\',\n                     \'terms\': {}}},\n \'Input\': {\'infile\': {\'attrs\': {\'action\': \'extend\',\n                                \'itype\': \'file\',\n                                \'nargs\': \'+\'},\n                      \'help\': \'An input file\',\n                      \'name\': \'infile\',\n                      \'terms\': {}},\n           \'invar\': {\'attrs\': {\'action\': \'extend\',\n                               \'itype\': \'var\',\n                               \'nargs\': \'+\'},\n                     \'help\': \'An input variable\',\n                     \'name\': \'invar\',\n                     \'terms\': {}}},\n \'Output\': {\'outfile\': {\'attrs\': {\'default\': \'output.txt\', \'otype\': \'file\'},\n                        \'help\': \'The output file\',\n                        \'name\': \'outfile\',\n                        \'terms\': {}}},\n \'Summary\': {\'long\': \'Long description\', \'short\': \'Short description\'}}\n```\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
