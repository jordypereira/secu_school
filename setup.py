from setuptools import setup

setup(
    name='secu_school',
    packages=['secu_school'],
    include_package_data=True,
    install_requires=[
        'flask',
        'setuptools-git',
    ],
)
