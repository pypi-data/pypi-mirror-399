# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pipen_lock']
install_requires = \
['filelock>=3,<4', 'pipen==1.1.*']

entry_points = \
{'pipen': ['lock = pipen_lock:pipen_lock_plugin']}

setup_kwargs = {
    'name': 'pipen-lock',
    'version': '1.1.0',
    'description': 'Process lock for pipen to prevent multiple runs at the same time',
    'long_description': '# pipen-lock\n\nProcess lock for pipen to prevent multiple runs at the same time\n\n## Installation\n\n```bash\npip install -U pipen-lock\n```\n\n## Enable/Disable\n\nThe plugin is enabled by default. To disable it, either uninstall it or:\n\n```python\nfrom pipen import Proc, Pipen\n\n# process definition\n\nclass MyPipeline(Pipen):\n    plugins = ["-lock"]\n\n```\n\n## Configuration\n\n- `lock_soft`: Whether to use soft lock. Default: `False`\n    non-soft lock is platform dependent while soft lock only watches the existence of the lock file.\n    See more details <https://py-filelock.readthedocs.io/en/latest/index.html#filelock-vs-softfilelock>\n    for the difference between `FileLock` and `SoftFileLock`\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
