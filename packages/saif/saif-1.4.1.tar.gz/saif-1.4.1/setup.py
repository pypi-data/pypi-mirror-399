from setuptools import setup, find_packages

LONG_DESCRIPTION = """
Saif Library - A Python library about Saif's eternal love for Cutie

Official Website: https://saif.likesyou.org
Documentation: https://saif.likesyou.org/assets/saif.pdf

Installation:
pip install saif

Usage:
import saif
print(saif.loveWithWhom())  # Returns: Cutie
print(saif.inLove())        # Returns: True
print(saif.love_poem())     # Returns a beautiful love poem
print(saif.generate_love_letter())  # Generates heartfelt love letter

Features:
- Check eternal love status
- Generate beautiful love poems and quotes
- Create love letters and romantic surprises
- Check soulmate compatibility
- Get love horoscopes and romantic advice
- Calculate love equations and percentages
- Share love whispers and eternal vows
- Plan perfect dates and romantic gestures

Saif is eternally in Love with Cutie. Forever and Always. ❤️✨

Visit: https://saif.likesyou.org
"""

setup(
    name="saif",
    version="1.4.1",
    author="Saif",
    author_email="saifullahanwar00040@gmail.com",
    description="Saif loves Cutie - A Python library of eternal, infinite love",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/plain",
    packages=find_packages(),
    python_requires=">=3.6",
    url="https://saif.likesyou.org",
    project_urls={
        "Website": "https://saif.likesyou.org",
        "Documentation": "https://saif.likesyou.org/assets/saif.pdf",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Topic :: Communications :: Chat",
        "Topic :: Text Processing",
    ],
    keywords=["love", "saif", "cutie", "romance", "eternal", "soulmate", "poetry", "relationship"],
    install_requires=[],
)