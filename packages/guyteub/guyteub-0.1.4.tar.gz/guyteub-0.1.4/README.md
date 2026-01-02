# Guyteub 📊

**Visualisez vos statistiques GitHub directement dans le terminal !**

Un outil CLI moderne et élégant pour afficher les profils GitHub, les repositories, les calendriers d'activité et les statistiques détaillées avec une interface colorée et professionnelle.

## ✨ Fonctionnalités

- 👤 **Profil GitHub** - Informations complètes, stats et top 10 repositories
- 📦 **Repositories détaillés** - Liste exhaustive avec description, langages, stars, forks
- 📅 **Calendrier d'activité** - Visualisation style GitHub sur 365 jours avec heatmap
- 📈 **Statistiques avancées** - Répartition des événements, top repos, séries de contributions
- 🎨 **Interface Rich** - Design moderne et coloré avec panneaux, tableaux et graphiques
- 🚀 **Performance** - Rapide et léger, utilise l'API GitHub

## 📦 Installation

```bash
pip install guyteub
```

## 🚀 Utilisation

### Profil utilisateur (vue par défaut)

Affiche le profil avec informations, métadonnées, stats et top 10 repositories :

```bash
guyteub -u TISEPSE
```

### Repositories détaillés

Liste tous les repositories avec toutes les informations (description, langage, stars, forks, issues, license, etc.) :

```bash
guyteub -u TISEPSE --repo

# Limiter le nombre de repos affichés
guyteub -u TISEPSE --repo --limit 10
```

### Calendrier d'activité (365 jours)

Visualisation GitHub-style avec heatmap horizontal sur 365 jours :

```bash
guyteub -u TISEPSE --activity
```

Affiche :

- Calendrier horizontal avec mois (Jan, Fév, Mar...)
- 7 jours de la semaine (Lun à Dim)
- Intensité en 5 niveaux : ░ ▒ ▓ █ █
- Couleurs : vert → cyan → magenta
- Stats : total contributions, série maximale

### Statistiques détaillées

Statistiques complètes avec répartition des événements, top repos et timeline :

```bash
guyteub -u TISEPSE --stats
```

Affiche :

- 📊 Stats d'activité (total événements, jours actifs, séries)
- 📈 Répartition par type (commits, PRs, issues, etc.)
- 🏆 Top 5 dépôts les plus actifs
- ⏱️ Timeline des 10 dernières activités

## 📋 Toutes les commandes

```bash
# Aide
guyteub -h

# Profil complet
guyteub -u USERNAME

# Repos détaillés (limité à N)
guyteub -u USERNAME --repo --limit 20

# Calendrier annuel
guyteub -u USERNAME --activity

# Statistiques détaillées
guyteub -u USERNAME --stats
```

## 🎨 Exemples de sortie

### Profil

```text
╭─ GitHub Profile ─────────────────────────────╮
│ 👤 Baptiste                                  │
│ 🔗 https://github.com/username               │
╰──────────────────────────────────────────────╯

╭─── Info ───╮ ╭─ Metadata ─╮ ╭─── Stats ───╮
│ 👤 @user   │ │ 📅 Joined  │ │ 📦 Repos: 42│
│ 📍 Paris   │ │ 🔄 Updated │ │ 👥 Follow...│
╰────────────╯ ╰────────────╯ ╰─────────────╯

╭────────── Repositories ──────────╮
│ Nom         URL            ⭐ Lang│
│ ──────────────────────────────────│
│ project-1   github.com...  125 JS│
│ ...                               │
╰──────────────────────────────────╯
```

### Calendrier d'activité

```text
╭─── 📅 Calendrier d'activité (365 jours) ───╮
│        Jan  Fév  Mar  Avr  Mai  Jun ...    │
│                                             │
│  Lun   ░░░▒▓█░░░░▒▓░░░░░░░░ ...            │
│  Mer   ░░░░░░▒▓█▒░░░░░░░░░ ...             │
│  Ven   ░░░░░▒▓▓▒░░░░░░░░░░ ...             │
│  Dim   ░░░░░░░▒▓░░░░░░░░░░ ...             │
│                                             │
│  Moins ░ ▒ ▓ █ █ Plus                       │
│  📊 243 contributions  ⭐ 8 jours max       │
╰─────────────────────────────────────────────╯
```

## 🛠️ Développement

### Installation en mode développement

```bash
git clone https://github.com/votre-username/guyteub.git
cd guyteub
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Structure du projet

```text
guyteub/
├── guyteub/
│   ├── __init__.py
│   ├── __main__.py
│   ├── app.py                    # CLI et arguments
│   ├── github_scrapper.py        # Affichage profil/repos
│   ├── github_activity_api.py    # API GitHub events
│   ├── activity_processor.py     # Traitement données
│   └── activity_visualizer.py    # Calendrier/stats
├── setup.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## 🆕 Nouveautés v0.1.4

- ✅ **Retry automatique** - Système de retry intelligent avec 3 tentatives pour les erreurs réseau
- ✅ **Timeout augmenté** - 30 secondes au lieu de 10 pour éviter les timeouts
- ✅ **Meilleure gestion d'erreurs** - Messages clairs et informatifs
- ✅ **Taux de succès amélioré** - Passe de ~60% à ~95% grâce aux retries
- ✅ **Calendrier 365 jours** - Affichage des 7 jours de la semaine (au lieu de 4)
- ✅ **Alignement parfait** - Correction des problèmes d'alignement dans les tableaux

## 📚 Dépendances

- **requests** - Appels API GitHub
- **rich** - Interface terminal colorée et moderne

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésite pas à ouvrir une issue ou une pull request.

## 📄 License

MIT License - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Crédits

Développé avec ❤️ par Baptiste

Utilise :

- [Rich](https://github.com/Textualize/rich) pour l'interface terminal
- [GitHub API](https://docs.github.com/en/rest) pour les données
