"""
Guyteub - GitHub Stats CLI Tool

A terminal-based tool for displaying GitHub user profiles and repository statistics
with beautiful Rich-based visualizations.
"""

__version__ = "0.1.4"
__author__ = "Baptiste Demé (TISEPSE)"
__description__ = "Outils pour afficher les informations GitHub d'un utilisateurs dans un terminal"

from .github_scrapper import scrapper
from .app import main

__all__ = [
    'scrapper',
    'main',
    '__version__',
]
