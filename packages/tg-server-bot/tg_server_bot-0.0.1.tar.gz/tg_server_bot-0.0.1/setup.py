from setuptools import setup, find_packages

# 读取依赖
with open('requirements.txt') as f:
    required = f.read().splitlines()

# 读取 README
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tg-server-bot',
    version='0.0.1',
    description='A Telegram bot for Linux server management and shell execution.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='nobitaqaq',
    packages=find_packages(),
    install_requires=required,
    entry_points={
        'console_scripts': [
            'tg-bot=tg_server_bot.main:main',
            'tg-bot-cfg=tg_server_bot.main:edit_config',
            'tg-bot-auth=tg_server_bot.main:edit_auth',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.8',
    include_package_data=True,
)
