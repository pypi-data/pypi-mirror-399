# pwchkr

pwchkr est un module Python pour vérifier la force d'un mot de passe avec un score sur 10 et détecter les mots de passe trop communs, y compris français. pw -> password. chkr -> checker

Installation : pip install pwchkr

Utilisation :

* score\_motdepasse(mdp) : Évalue la force d’un mot de passe. Retourne "Code commun" si le mot de passe est trop courant, sinon un score sur 10.
* generate\_password(longueur=12) : Génère un mot de passe aléatoire sûr. longueur = taille du mot de passe (défaut 12).



Exemple :
from pwchkr import score\_motdepasse, generate\_password


print(score\_motdepasse("123456"))      # → "Code commun"


print(score\_motdepasse("Ab3$9fGh!"))   # → 8 ou 9


mdp = generate\_password(12)


print(mdp)


print(score\_motdepasse(mdp))           # → ≥ 8



Codes communs détectés : 123456, 123456789, qwerty, password, 1234567, 12345678, 12345, 111111, 123123, abc123, 1234, iloveyou, 1q2w3e4r, 000000, qwertyuiop, 123, monkey, dragon, baseball, letmein, login, football, admin, welcome, solo, 1qaz2wsx, master, sunshine, princess, 654321, 9876543210, azerty, 0000, 00000000, motdepasse, azerty123, bonjour, secret, chocolat



Exemple complet :


from pwchkr import score\_motdepasse, generate\_password


print(score\_motdepasse("motdepasse"))  # → "Code commun"


mdp = generate\_password(14)


print(mdp)


print(score\_motdepasse(mdp))           # → ≥ 8







pour l'installer : pip install pwchkr

