from setuptools import setup, find_packages

setup(
    name='multi-source-reader',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyGithub',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-api-python-client',
        'jira',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'multi-source-reader=src.main:main',
        ],
    },
)