# Fichero instalador

from setuptools import setup, find_packages

setup(
    name="minimodulo",           # Nombre del paquete
    version="0.2",              # Versión inicial
    packages=find_packages(),   # Encuentra automáticamente las carpetas con __init__.py
    author="Iker Ortiz de Luzuriaga",
    author_email="iker.ortiz@dipc.org",
    description="Un módulo de ejemplo que solicita datos",
    url="https://github.com/iortizdeluzu/minimodulo",
    install_requires=[
    "numpy>=1.23",
    "pandas",
    "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
