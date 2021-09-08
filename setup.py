from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in gdpr_compliant/__init__.py
from gdpr_compliant import __version__ as version

setup(
	name='gdpr_compliant',
	version=version,
	description='Compliance app for GDPR',
	author='Bantoo',
	author_email='chipo@thebantoo.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
