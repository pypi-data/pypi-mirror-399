
import string
import random
import os

# Charger les codes communs depuis le fichier
chemin_codes = os.path.join(os.path.dirname(__file__), "codes_communs.txt")
with open(chemin_codes, "r", encoding="utf-8") as f:
    CODES_COMMUNS = [ligne.strip() for ligne in f if ligne.strip()]

def est_code_commun(mdp):
    """Vérifie si le mot de passe contient un code/mot commun."""
    for code in CODES_COMMUNS:
        if code.lower() in mdp.lower():
            return True
    return False

def score_motdepasse(mdp):
    """
    Calcule un score sur 10 pour un mot de passe.
    Retourne "Code commun" si le mot de passe contient un élément trop courant.
    """
    if est_code_commun(mdp):
        return "Code commun"

    score = 0

    # Critères (longueur, lettres, chiffres, spéciaux, etc.)
    if len(mdp) >= 8: score += 1
    if any(c.islower() for c in mdp): score += 1
    if any(c.isupper() for c in mdp): score += 1
    if any(c.isdigit() for c in mdp): score += 1
    if any(c in "!@#$%^&*(),.?\":{}|<>" for c in mdp): score += 1

    # Pas de suite logique
    suite = False
    for i in range(len(mdp) - 2):
        seq = mdp[i : i + 3]
        if seq.isdigit() and seq in "0123456789": suite = True
        if seq.isalpha() and seq.lower() in "abcdefghijklmnopqrstuvwxyz": suite = True
    if not suite: score += 1

    # Pas de répétitions
    repet = False
    for i in range(len(mdp) - 2):
        if mdp[i] == mdp[i + 1] == mdp[i + 2]: repet = True
    if not repet: score += 1

    if len(mdp) >= 12: score += 1
    if len(mdp) >= 16: score += 1

    lettres = sum(c.isalpha() for c in mdp)
    chiffres = sum(c.isdigit() for c in mdp)
    speciaux = sum(c in "!@#$%^&*(),.?\":{}|<>" for c in mdp)
    if lettres >= 3 and chiffres >= 3 and speciaux >= 2: score += 1

    return score

def generate_password(longueur=12):
    """
    Génère un mot de passe aléatoire avec un score ≥ 8/10
    et qui n’est pas dans les codes communs.
    """
    lettres = string.ascii_letters
    chiffres = string.digits
    speciaux = "!@#$%^&*(),.?\":{}|<>"
    caracteres = lettres + chiffres + speciaux

    while True:
        mdp = "".join(random.choice(caracteres) for _ in range(longueur))
        s = score_motdepasse(mdp)
        if s != "Code commun" and isinstance(s, int) and s >= 8:
            return mdp
