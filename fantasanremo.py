import random

CANTANTI = {
    "Alessandra Amoroso": 23,
    "Alfa": 20,
    "Angelina Mango": 23,
    "Annalisa": 23,
    "BigMama": 23,
    "bnkr44": 16,
    "CLARA": 16,
    "Dargen D'Amico": 22,
    "Diodato": 21,
    "Emma": 23,
    "Fiorella Mannoia": 20,
    "Fred De Palma": 18,
    "Gazzelle": 19,
    "Geolier": 22,
    "Ghali": 20,
    "Il Tre": 17,
    "Il Volo": 20,
    "Irama": 19,
    "La Sad": 19,
    "Loredana Bertè": 18,
    "Mahmood": 21,
    "Maninni": 17,
    "Mr. Rain": 21,
    "Negramaro": 22,
    "Renga e Nek": 20,
    "Ricchi e Poveri": 18,
    "Rose Villain": 19,
    "sangiovanni": 21,
    "SANTI FRANCESI": 16,
    "The Kolors": 22,
}


def select():
    cantanti = [*CANTANTI.keys()]
    random.shuffle(cantanti)
    return cantanti[:5]


squadra = select()
while sum([CANTANTI[name] for name in squadra]) > 100:
    squadra = select()


print(*squadra, sep="\n")
