from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='vaultdweller',
    version='0.2.2',
    author='ckoetael',
    author_email='ckoetael@gmail.com',
    description='This is the simplest client for quick work with vaultwarden.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ckoetael/vaultdweller',
    packages=find_packages(),
    install_requires=[
        'pyotp>=2.9.0',
        'httpx>=0.28.1',
        'pycryptodome>=3.22.0',
        'hkdf>=0.0.3'
    ],
    setup_requires=[
        'pyotp>=2.9.0',
        'httpx>=0.28.1',
        'pycryptodome>=3.22.0',
        'pydantic',
        'hkdf>=0.0.3'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords=[
        'vaultwarden',
        'bitwardern',
        'password',
        'totp',
        'one-time-password'
    ],
    project_urls={
        'GitHub': 'https://github.com/Ckoetael/vaultdweller'
    },
    python_requires='>=3.11'
)
