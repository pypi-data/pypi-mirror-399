# Guyteub

Outils pour afficher les stats GitHub d'un utilisateur dans le terminal.

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

- Statistiques complètes du profil (repos, followers, gists, etc.)
- Liste des repositories triés par popularité
- Interface colorée avec Rich
- Layout moderne en 3 colonnes

## Dépendances

- `requests` - Pour les appels API GitHub
- `rich` - Pour l'affichage coloré dans le terminal

## Développement

```bash
git clone https://github.com/votre-username/guyteub.git
cd guyteub
pip install -e .
```

## License

MIT
