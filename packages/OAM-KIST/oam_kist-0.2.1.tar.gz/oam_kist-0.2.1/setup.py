from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="OAM_KIST",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
    ],
    author="Youngjun Kim",
    author_email="kyjun0915@kist.re.kr",
    description="Quantum information and technology using OAM states and SLM for KIST research",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires=">=3.7",
)