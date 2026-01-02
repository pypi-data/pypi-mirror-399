from setuptools import setup, find_packages

setup(
    name="keystone-license",
    version="0.1.2",
    description="KeyStone - License validation library for KeyForge",
    author="MaskedTTN",
    author_email="mustaeensiddiqui27@gmail.com",
    url="https://github.com/MaskedTTN/keystone",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
