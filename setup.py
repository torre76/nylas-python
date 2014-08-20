from distutils.core import setup

setup(
    name='inbox',
    version='0.1.0',
    author='Inbox Team',
    author_email='support@inboxapp.com',
    packages=['inbox'],
    scripts=[],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Python bindings for the Inbox API',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 2.3.0"
    ],
)
