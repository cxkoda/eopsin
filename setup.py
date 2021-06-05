import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eopsin",
    version="0.0.0",
    author="David Huber",
    author_email="dave@yomi.eu",
    description="Yet another automated crypto trading framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cxkoda/eopsin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'SQLAlchemy>=1.4.15',
        'numpy>=1.19.5',
        'python-binance>=1.0.10'
    ],
    python_requires='>=3.6',
)
