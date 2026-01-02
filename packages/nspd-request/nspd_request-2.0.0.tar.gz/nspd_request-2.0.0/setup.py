"""
Setup script for nspd-request package
Совместимость со старыми системами сборки
"""

from setuptools import setup, find_packages

# Читаем README для длинного описания
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Читаем requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nspd-request",
    version="2.0.0",
    author="Logar1t",
    author_email="logar1t.official@gmail.com",
    description="Python-библиотека для работы с НСПД (Национальная система пространственных данных)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Logar1t/NSPD-request",
    project_urls={
        "Bug Tracker": "https://github.com/Logar1t/NSPD-request/issues",
        "README": "https://github.com/Logar1t/NSPD-request/blob/main/README.md",
        "Documentation": "https://github.com/Logar1t/NSPD-request/blob/main/DOCUMENTATION.md",
        "Source Code": "https://github.com/Logar1t/NSPD-request",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="nspd кадастр недвижимость api росреестр",
    include_package_data=True,
    zip_safe=False,
)

