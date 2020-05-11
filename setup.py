from setuptools import find_packages, setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='interpretability-engine',
    version='0.11.0',
    author='Parmentier Laurent',
    author_email='laurent.parmentier@corp.ovh.com',
    packages=find_packages(),
    scripts=['bin/interpretability-engine'],
    url='https://github.com/ovh/interpretability-engine',
    description='Interpret Machine Learning black-box models deployed on Serving Engine',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=required,
    include_package_data=True
)
