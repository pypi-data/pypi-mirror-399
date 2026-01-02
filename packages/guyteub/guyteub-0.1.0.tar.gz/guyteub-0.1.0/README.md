# Guyteub

Outils pour afficher les stats GitHub d'un utilisateur dans le terminal avec la photo de profil.

## Installation

```bash
pip install guyteub
```

## Utilisation

```bash
# Afficher les stats d'un utilisateur GitHub
guyteub -u username

# Message de test
guyteub --echo
```

## Fonctionnalités

- Affichage de la photo de profil GitHub dans le terminal
- Statistiques complètes du profil (repos, followers, gists, etc.)
- Interface colorée avec Rich
- Support de l'affichage d'images dans le terminal

## Dépendances

- `requests` - Pour les appels API GitHub
- `rich` - Pour l'affichage coloré dans le terminal
- `term-image` - Pour l'affichage des images

## Développement

```bash
git clone https://github.com/votre-username/guyteub.git
cd guyteub
pip install -e .
```

## License

MIT
