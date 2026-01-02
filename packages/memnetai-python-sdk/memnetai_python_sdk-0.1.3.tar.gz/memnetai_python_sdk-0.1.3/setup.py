from setuptools import setup, find_packages

setup(
    name='memnetai-python-sdk',
    version='0.1.3',
    packages=find_packages(),
    description='MemNet AI Python SDK - 提供记忆网络AI的Python接口',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='',
    author='MemNet AI Team',
    author_email='admin@donglizhiyuan.com',
    license='Apache License 2.0',
    install_requires=[
        'requests>=2.32.0',
        'loguru>=0.7.0',
        'openai>=2.14.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    python_requires='>=3.9',
)