from distutils.core import setup
from setuptools import find_packages, setup

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')

reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='interpretability-engine',
    version='0.1.0',
    author='Parmentier Laurent',
    author_email='laurent.parmentier@corp.ovh.com',
    packages=find_packages(),
    scripts=['bin/interpretability-engine'],
    url='https://gitlab.society-lbl.com/thesis/interpretability-engine',
    description='An API to interepret Machine Learning models',
    install_requires=reqs,
    include_package_data=True
)
