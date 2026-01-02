from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gfxcanvas",
    version="1.0.0",
    author="Basit Ahmad Ganie",
    author_email="basitahmed1412@gmail.com",
    description="Advanced Python Graphics and Game Engine built on Tkinter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/basitganie/gfxcanvas",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Pillow>=9.0.0",
    ],
    keywords="graphics game-engine tkinter canvas animation physics 2d 3d sprites",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/gfxcanvas/issues",
        "Source": "https://github.com/yourusername/gfxcanvas",
        "Documentation": "https://github.com/yourusername/gfxcanvas#readme",
    },
)
