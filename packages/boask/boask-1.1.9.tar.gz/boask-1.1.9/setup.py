from setuptools import setup, find_packages
from pathlib import Path

version_file = Path("boask") / "version.py"
version_globals = {}
with open(version_file, "r") as f:
    exec(f.read(), version_globals)

__version__ = version_globals["__version__"]

setup(
    name="boask",
    version=__version__,
    description="Pure Python website engine. Zero dependencies. Real JSX templates.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="OXOP",
    author_email="minbartek41@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    license="MIT",
    keywords=["web", "minimal", "python", "no-dependencies"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Werkzeug>=2.3.0",
        "PyJWT>=2.8.0"
    ]
)
