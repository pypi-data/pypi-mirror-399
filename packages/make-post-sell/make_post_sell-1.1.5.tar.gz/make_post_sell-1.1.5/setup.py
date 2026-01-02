import os
from setuptools import setup, find_packages


def parse_requirements(filename):
    """
    Read and parse a requirements file, ignoring comments and blank lines.
    """
    req_path = os.path.join(os.path.dirname(__file__), filename)
    with open(req_path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


# Determine the runtime requirements.
install_requires = parse_requirements("requirements.py3.txt")

# Optional extras for development, production, and testing.
extras_require = {
    "dev": parse_requirements("requirements-dev.txt"),
    "prod": parse_requirements("requirements-prod.txt"),
    "test": parse_requirements("requirements-test.txt"),
}

# Read the long description from README.rst.
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst"), "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="make_post_sell",
    version="1.1.5",
    description="Make Post Sell",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Russell Ballestrini",
    author_email="russell@ballestrini.net",
    url="https://www.makepostsell.com",
    keywords="make post sell web pyramid pylons ecommerce digital downloads physical goods content marketing youtube alternative",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "make_post_sell": ["scripts/alembic/*.py", "scripts/alembic/versions/*.py"]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "paste.app_factory": ["main = make_post_sell:main"],
        "console_scripts": [
            "initialize_make_post_sell_db = make_post_sell.scripts.initialize_db:main",
            "crypto_watcher = make_post_sell.lib.crypto_watcher:main",
        ],
    },
)

# python setup.py sdist bdist_wheel
# twine upload dist/*
