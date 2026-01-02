from setuptools import setup, find_packages

from kody_clientsdk_python import __version__ as version
setup(
    name="kody_clientsdk_python",
    version=version,
    description='Kody API client',
    long_description=open('README.md').read(),
    author='Kody Tech Team',
    author_email='tech@kody.com',
    url='https://github.com/KodyPay/kody-clientsdk-python',
    license='MIT',
    requires_python='>=3.12',
    packages=find_packages(),
    install_requires=[  # List your dependencies here
        'grpcio==1.66.1',
        'protobuf==5.27.2'
    ],
)
