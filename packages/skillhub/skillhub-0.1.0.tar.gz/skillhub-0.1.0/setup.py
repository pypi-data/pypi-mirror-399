from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='skillhub',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'requests>=2.28.0',
        'pyyaml>=6.0',
        'rich>=13.0.0',
    ],
    entry_points={
        'console_scripts': [
            'skillhub=skillhub.cli:cli',
        ],
    },
    author='Bhavik Dhandhala',
    author_email='dhandhalyabhavik@gmail.com',
    description='Package manager for AI agent workflows',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/v1k22/skillhub-cli',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.9',
    keywords='ai agent automation workflow package-manager',
    project_urls={
        'Bug Reports': 'https://github.com/v1k22/skillhub-cli/issues',
        'Source': 'https://github.com/v1k22/skillhub-cli',
        'Registry': 'https://github.com/v1k22/skillhub-registry',
    },
)
