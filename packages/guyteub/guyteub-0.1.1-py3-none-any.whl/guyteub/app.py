import argparse
from .github_scrapper import *

def main():
    parser = argparse.ArgumentParser(description="Outils pour afficher les stats d'une personnes dans un terminale.")
    parser.add_argument('--echo', action='store_true', help="Affiche un pti message rigouligolo.")
    parser.add_argument('-u', '--username', type=str, help="Pseudo GitHub de la personne à scrapper.")

    args = parser.parse_args()

    if args.echo:
        print("MAIS MISERICOOOOOOOOORDE LE CIEL ME TOMBE SUR LA TETE")

    if args.username:
        scrapper(username=args.username)

if __name__ == "__main__":
    main()