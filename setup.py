from distutils.core import setup

setup(
	name='pytest-vnet',
	version='0.1.1',
	description='Pytest plugin for SDN testing',
	author='Guillermo Rodriguez',
	author_email='guillermor@fing.edu.uy',
	packages=['pytest_vnet'],
	entry_points={"pytest11": ["pytest-vnet = pytest_vnet.plugin"]},
	classifiers=["Framework :: Pytest"]
)