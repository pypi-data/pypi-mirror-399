"""
Guyteub - GitHub Stats CLI Tool
Main application entry point with command-line argument parsing
"""
import argparse
from .github_scrapper import scrapper


def main():
    """Main entry point for the Guyteub CLI application"""
    parser = argparse.ArgumentParser(
        description="Outils pour afficher les stats GitHub dans un terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--echo',
        action='store_true',
        help="Affiche un message de test"
    )

    parser.add_argument(
        '-u', '--username',
        type=str,
        required=False,
        help="Pseudo GitHub de la personne à scrapper"
    )

    parser.add_argument(
        '-r', '--repo',
        action='store_true',
        help="Affiche les repositories détaillés avec toutes les informations"
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help="Nombre de repositories à afficher (défaut: 20)"
    )

    parser.add_argument(
        '-a', '--activity',
        action='store_true',
        help="Affiche le calendrier d'activité GitHub (365 jours, style GitHub)"
    )

    parser.add_argument(
        '-s', '--stats',
        action='store_true',
        help="Affiche les statistiques détaillées (top repos, répartition événements, timeline)"
    )

    args = parser.parse_args()

    if args.echo:
        print("MAIS MISERICOOOOOOOOORDE LE CIEL ME TOMBE SUR LA TETE")

    if args.username:
        if args.activity or args.stats:
            # Display activity/stats
            from .github_activity_api import GitHubActivityAPI
            from .activity_processor import ActivityProcessor
            from .activity_visualizer import ActivityVisualizer

            api = GitHubActivityAPI()
            events = api.fetch_user_events(args.username, max_pages=10, days_limit=365)

            if events:
                processor = ActivityProcessor(events)
                visualizer = ActivityVisualizer(processor, args.username)

                if args.activity:
                    # Show only the calendar
                    visualizer.render_full_activity_view()
                elif args.stats:
                    # Show detailed statistics
                    visualizer.render_stats_view()
            else:
                print(f"❌ Aucune activité trouvée pour {args.username}")
        else:
            # Display profile
            scrapper(
                username=args.username,
                show_detailed_repos=args.repo,
                limit=args.limit
            )
    elif not args.echo:
        parser.print_help()


if __name__ == "__main__":
    main()
