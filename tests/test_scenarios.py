import sys

from src.search_engine import MoteurRecherche

# Jeu de DÉVELOPPEMENT : déjà vu, il a servi à diagnostiquer le moteur.
CAS_DEVELOPPEMENT = [
    ("Ma nouvelle alternante démarre le 3 décembre, il lui faut un compte et un ordinateur", {"PROC-ONB-001"}),
    ("Je n'arrive plus à me connecter, j'ai oublié mon code", {"PROC-ACC-003"}),
    ("Il me faut Excel sur mon PC pour analyser des chiffres", {"PROC-LOG-001"}),
    ("Mon écran est cassé", {"PROC-MAT-001"}),
    ("J'ai trouvé une clé USB inconnue dans l'open space", {"PROC-INC-002"}),
    ("Mon collègue part à la retraite, que faire de ses accès ?", {"PROC-ONB-002", "PROC-ACC-002"}),
    ("Je veux utiliser un assistant IA en ligne pour résumer des documents", {"PROC-LOG-002"}),
    ("Mme Durand devient Mme Martin, comment mettre à jour son profil ?", {"PROC-CPT-001"}),
    ("L'outil de reporting est inaccessible depuis ce matin, erreur 500", {"PROC-INC-001"}),
    ("Je voudrais donner plus de droits à un collaborateur promu chef d'équipe", {"PROC-CPT-002"}),
    ("J'ai cliqué sur un lien douteux dans un mail", {"PROC-INC-002"}),
]

# Jeu de VALIDATION 1 : mesuré une première fois (6/6). Sert désormais de
# contrôle de non-régression après chaque modification de la base.
CAS_VALIDATION_1 = [
    ("Je dois commander une souris et un clavier pour un nouvel arrivant", {"PROC-MAT-001", "PROC-ONB-001"}),
    ("Le compte de mon collègue est bloqué après trois erreurs de saisie", {"PROC-ACC-003"}),
    ("Peux-tu installer Teams sur mon ordinateur ?", {"PROC-LOG-001"}),
    ("Mon stagiaire change d'équipe, son rattachement doit être modifié", {"PROC-CPT-001"}),
    ("Je pense avoir été victime d'une arnaque par mail, mon mot de passe a peut-être fuité", {"PROC-INC-002"}),
    ("Un prestataire quitte la mission, je souhaite supprimer ses droits sur l'outil de suivi", {"PROC-ACC-002"}),
]

# Jeu de VALIDATION 2 : écrit AVANT l'enrichissement de la base, ciblant les
# points faibles constatés (matériel endommagé, périphérique inconnu, IA en
# ligne, alternance). Ne pas reprendre ces phrases dans la base documentaire.
CAS_VALIDATION_2 = [
    ("Mon casque audio est hors service, je souhaite le faire remplacer", {"PROC-MAT-001"}),
    ("Un inconnu m'a remis une clé USB, je soupçonne qu'elle est piégée", {"PROC-INC-002"}),
    ("Puis-je utiliser ChatGPT pour mon travail ?", {"PROC-LOG-002"}),
    ("Mon apprenti commence en septembre, il faut préparer son poste", {"PROC-ONB-001"}),
    ("Je veux ajouter un second responsable hiérarchique sur le compte d'une collègue", {"PROC-CPT-001"}),
    ("Mon ordinateur ne démarre plus du tout", {"PROC-INC-001", "PROC-MAT-001"}),
]

# Cas limites : pas de résultat attendu, on observe le comportement.
CAS_LIMITES = [
    "recette de la tarte aux pommes",
    "I forgot my password and cannot log in",
    "mot de pase oublié",
    "j'ai un problème",
    "bonjour",
    "a",
]


def afficher_top3(analyse):
    if not analyse["resultats"]:
        score = analyse["meilleur_score"]
        texte = f"{score:.3f}" if score is not None else "n/a"
        print(f"      aucun résultat affiché (meilleur score = {texte})")
        return
    for rang, r in enumerate(analyse["resultats"], start=1):
        print(f"      {rang}. {r['procedure']['id']}  score={r['score']:.3f}")


def evaluer(titre, cas, moteur):
    print(f"\n=== {titre} ===")
    ok_top1 = 0
    ok_top3 = 0
    nb_ambigus = 0
    for demande, acceptes in cas:
        analyse = moteur.rechercher(demande)
        ids = [r["procedure"]["id"] for r in analyse["resultats"]]
        top1 = bool(ids) and ids[0] in acceptes
        top3 = any(i in acceptes for i in ids)
        ok_top1 += top1
        ok_top3 += top3
        nb_ambigus += analyse["statut"] == "ambigu"
        print(f"\n[{'OK' if top1 else 'KO'}] {demande}")
        print(f"      attendu : {sorted(acceptes)}   statut : {analyse['statut']}   dans le top 3 : {'oui' if top3 else 'non'}")
        afficher_top3(analyse)

    total = len(cas)
    print(f"\nRésultat {titre} : top 1 = {ok_top1}/{total}   top 3 = {ok_top3}/{total}   signalées ambiguës = {nb_ambigus}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    moteur = MoteurRecherche()

    evaluer("DEVELOPPEMENT", CAS_DEVELOPPEMENT, moteur)
    evaluer("VALIDATION 1", CAS_VALIDATION_1, moteur)
    evaluer("VALIDATION 2", CAS_VALIDATION_2, moteur)

    print("\n=== CAS LIMITES (à observer) ===")
    for demande in CAS_LIMITES:
        analyse = moteur.rechercher(demande)
        print(f"\n> {demande!r}   statut : {analyse['statut']}")
        afficher_top3(analyse)

    print("\n> demande vide ''")
    try:
        moteur.rechercher("   ")
    except ValueError as erreur:
        print(f"      erreur gérée : {erreur}")


if __name__ == "__main__":
    main()