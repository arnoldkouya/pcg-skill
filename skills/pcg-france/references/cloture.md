# Clôture d'exercice selon le PCG : référence détaillée

Les codes cités ont été vérifiés dans `plan-comptable-2026.csv`. Un code absent du plan de l'année (par exemple 79, 675, 775, 4486) ne doit pas être utilisé sans l'avoir confirmé : le plan a été remanié en 2025.

## 1. Réforme du PCG applicable depuis le 1er janvier 2025

Le règlement ANC n° 2022-06 modifie le règlement ANC n° 2014-03. Il s'applique aux exercices ouverts à compter du 1er janvier 2025, sans effet rétroactif. Points qui changent les imputations :

- **Résultat exceptionnel** : il n'est plus défini par une liste de comptes. Un événement n'est exceptionnel que s'il est à la fois majeur et inhabituel, avec une justification documentée. Les comptes 67 et 77 existent toujours (672 et 678, 772 et 778, dotations 687, reprises 787) mais leur usage est restreint.
- **Transferts de charges** : le compte 79 est supprimé. Les remboursements de charges de personnel vont en 649, les indemnités d'assurance en 7587 (sauf destruction ou vol d'une immobilisation, qui vont en 757).
- **Cessions d'immobilisations** : la valeur comptable des immobilisations cédées va en 657 et le produit de cession en 757, à la place de 675 et 775.
- **Subventions d'investissement** : la quote-part virée au résultat est inscrite en 747 (contrepartie 139).
- **Créances irrécouvrables** : 654 pour les créances commerciales, 668 et 768 pour les créances financières.

Pour un exercice ouvert avant le 1er janvier 2025, utiliser le plan 2024 (`--annee 2024`) : les comptes 79 (transferts de charges, 791), 675 (valeurs comptables des éléments d'actif cédés), 775 (produits des cessions d'éléments d'actif), 777 (quote-part des subventions d'investissement virée au résultat) et 6812 existent encore et les imputations ci-dessous sont à adapter. La commande `diff --de 2024 --vers 2025` liste les comptes ajoutés (71) et supprimés (235).

La différence entre les plans 2025 et 2026 est faible (4 comptes ajoutés, 4 supprimés, 10 modifiés, surtout autour des comptes 16 : avances conditionnées et emprunts participatifs). La commande `diff` du script la détaille.

## 2. Contrôles préalables sur la balance ou le FEC

1. Total des soldes débiteurs égal au total des soldes créditeurs. Pour un FEC, chaque écriture doit aussi être équilibrée.
2. Tous les codes existent dans le plan de l'année. Un code de plus de 5 chiffres se rattache à son préfixe (compte de l'entité).
3. Soldes à contre-sens à examiner, avec reclassement au bilan si l'anomalie est réelle :
   - client créditeur : à présenter en 419 au passif ;
   - fournisseur débiteur : à présenter en 409 à l'actif ;
   - caisse (53) créditrice : erreur de saisie ou opération non enregistrée ;
   - charge créditrice ou produit débiteur : régularisation ou erreur d'imputation (hors comptes de rabais, remises et ristournes 609, 619, 629, 709 qui ont un sens inverse).
4. TVA : arrêter les comptes 44566 et 44562 (déductible), 44571 (collectée) et 4452 (intracommunautaire). Un solde créditeur net va en 44551 (TVA à décaisser), un solde débiteur net en 44567 (crédit de TVA à reporter). Les opérations en attente de régularisation restent en 4458.
5. Comptes d'attente (47) et virements internes (58) : doivent être soldés.

## 3. Soldes intermédiaires de gestion (SIG)

Trame à aligner sur le modèle de compte de résultat applicable à l'entité (système de base, abrégé ou développé).

| SIG | Principe de calcul |
|---|---|
| Marge commerciale | Ventes de marchandises (707, nettes de 709) moins coût d'achat des marchandises vendues (607 net de 609, corrigé de la variation de stock 6037) |
| Production de l'exercice | Ventes de produits et de services (70 hors 707), production stockée (713), production immobilisée (72) |
| Valeur ajoutée | Marge commerciale plus production de l'exercice, moins consommations en provenance de tiers (60 hors 607 et 6037, 61, 62) |
| Excédent brut d'exploitation (EBE) | Valeur ajoutée plus subventions d'exploitation (741), moins impôts, taxes et versements assimilés (63), moins charges de personnel (64) |
| Résultat d'exploitation | EBE plus autres produits de gestion courante (75) et reprises d'exploitation (7811, 7815, 7816, 7817), moins autres charges de gestion courante (65) et dotations d'exploitation (6811, 6815, 6816, 6817) |
| Résultat financier | Produits financiers (76) et reprises (786), moins charges financières (66) et dotations financières (686) |
| Résultat courant avant impôts | Résultat d'exploitation plus résultat financier |
| Résultat exceptionnel | Produits (77, 787) moins charges (67, 687), dans le périmètre restreint de la réforme |
| Résultat net | Résultat courant plus résultat exceptionnel, moins participation des salariés (691) et impôt sur les bénéfices (695, 696) |

Les comptes 657 et 757 (cessions) sont des comptes de gestion courante (65 et 75). Leur place dans le modèle de compte de résultat suit le règlement en vigueur : à confirmer avant de présenter l'état.

Contrôle obligatoire : le résultat net de la cascade doit égaler la somme (crédit moins débit) des classes 6 et 7. La commande `balance` du script donne cette valeur. En cas d'écart, chercher le compte mal classé avant de rendre le résultat.

## 4. Écritures d'inventaire

Chaque écriture est présentée en tableau Date, Compte, Libellé, Débit, Crédit, avec l'égalité des totaux vérifiée par calcul.

### Amortissements
Débit 6811 ; crédit 28 suivi du numéro du compte d'immobilisation (par exemple 2813 pour des constructions du compte 213, 2815 pour du matériel du compte 215, 2805 pour des logiciels et brevets). Données à demander : valeur d'origine, mode (linéaire, dégressif), durée, date de mise en service, prorata temporis, composants.

### Dépréciations
- Immobilisations : débit 6816 ; crédit 29 suivi du numéro du compte concerné.
- Stocks : débit 6817 ; crédit 39 (391 matières premières, 397 marchandises, etc.).
- Créances clients : débit 6817 ; crédit 491.
- Éléments financiers : débit 6866 ; crédit 59 ou 29 selon la nature.

### Provisions pour risques et charges
- Exploitation : débit 6815 ; crédit 151 (risques : 1511 litiges, 1512 garanties données aux clients, 1514 amendes et pénalités, 1516 pertes sur contrats, 1518 autres) ou 152 (charges : 1521 pensions, 1522 restructurations, 1523 impôts, 1525 gros entretien ou grandes révisions, 1526 remise en état, 1527 autres).
- Financières : débit 6865 ; crédit 1515 pour pertes de change.
- Exceptionnelles : débit 6875 ; crédit au compte 15 concerné, seulement si l'événement est majeur et inhabituel.

### Reprises
Débit du compte de provision, d'amortissement ou de dépréciation ; crédit 7811 (amortissements), 7815 (provisions d'exploitation), 7816 (immobilisations), 7817 (actifs circulants), 7866 ou 7876 selon le cas.

### Variation des stocks
- Annulation du stock initial : débit 603 (6031 matières premières et fournitures, 6032 autres approvisionnements, 6037 marchandises) ; crédit du compte de stock (31, 32, 37).
- Constatation du stock final : débit du compte de stock ; crédit 603x.
- Production stockée : même mécanisme avec 713 (7133 en-cours, 7135 produits) et les comptes 33, 34, 35.

### Charges à payer et produits à recevoir
- Fournisseurs, factures non parvenues : débit du compte de charge ; crédit 408 (4081).
- Clients, factures à établir : débit 418 (4181) ; crédit du compte de produit.
- Personnel : crédit 4282 (congés à payer) ou 4286 (autres charges à payer). Organismes sociaux : 4382 (charges sociales sur congés) ou 4386. État : 4481 (charges à payer) et 4482 (produits à recevoir). Divers : 468.
- Participation des salariés : débit 691 ; crédit 424 (ou 4284 si dette provisionnée).

### Régularisations
- Charges constatées d'avance : débit 486 ; crédit du compte de charge.
- Produits constatés d'avance : débit du compte de produit ; crédit 487.
- Différences de conversion : 476 (actif) et 477 (passif). Provision pour perte de change latente : débit 6865 ; crédit 1515.

### Créances douteuses ou irrécouvrables
1. Reclassement : débit 416 ; crédit 411.
2. Dépréciation : débit 6817 ; crédit 491.
3. Perte définitive : débit 654 (6541 créances de l'exercice, 6544 exercices antérieurs) ; crédit 416 ; reprise de la dépréciation en 7817. La TVA sur créance irrécouvrable se régularise séparément.

### Cessions d'immobilisations
- Sortie : débit 657 (valeur nette comptable) et 28x (amortissements cumulés) ; crédit 2x (valeur brute).
- Prix de cession : débit 462 ou 512 ; crédit 757 (et TVA collectée).
- Dotation de l'exercice de sortie : amortissement jusqu'à la date de cession (prorata).

### Subventions d'investissement
Quote-part annuelle virée au résultat : débit 139 ; crédit 747.

### Impôt sur les bénéfices
Débit 695 (6951 impôts dus en France) ; crédit 444, net des acomptes déjà versés (portés au débit de 444). Taux, plafonds de taux réduit, contributions et régimes dépendent de l'exercice et de l'entité : ne pas figer de taux, renvoyer vers impots.gouv.fr ou un professionnel.

## 5. Détermination du résultat et états financiers

- Résultat : solder les classes 6 et 7 ; bénéfice au crédit de 120, perte au débit de 129.
- Compte de résultat : charges (classe 6) et produits (classe 7) par nature, selon la cascade des SIG.
- Bilan, actif : immobilisations de la classe 2 nettes de 28 et 29 ; stocks de la classe 3 nets de 39 ; créances de la classe 4 nettes de 49 ; disponibilités de la classe 5 (nettes de 59).
- Bilan, passif : capitaux propres de la classe 1 (résultat inclus), provisions (15), emprunts et dettes (16), dettes de la classe 4, concours bancaires courants (519).
- Comptes mixtes (la plupart des comptes de tiers, 51) : actif si le solde est débiteur, passif s'il est créditeur, compte par compte, sans compensation entre comptes différents.
- Contrôle final : total actif égal au total passif.
- Annexe et liasse fiscale : lister les informations à collecter. Les formulaires dépendent du régime (réel normal, réel simplifié, impôt sur les sociétés ou impôt sur le revenu) et changent de millésime : renvoyer vers impots.gouv.fr pour la liste en vigueur, sans inventer de montants.

## 6. Affectation du résultat

Après approbation des comptes par l'organe compétent :

1. Bénéfice : débit 120 ; crédit 1061 (réserve légale), 1063 (réserves statutaires ou contractuelles), 1064 (réserves réglementées), 1068 (autres réserves), 457 (dividendes à payer) et 110 (report à nouveau créditeur) pour le solde.
2. Perte : débit 119 (report à nouveau débiteur) ; crédit 129.
3. Entreprise individuelle : les mouvements passent par le compte de l'exploitant (108) et non par 457.

Le taux de réserve légale, les conditions de distribution et la fiscalité des dividendes dépendent de la forme sociale, des statuts et de la loi : les demander et les signaler comme hypothèses.

## 7. Fichier des écritures comptables (FEC)

Le FEC comporte 18 colonnes obligatoires : JournalCode, JournalLib, EcritureNum, EcritureDate, CompteNum, CompteLib, CompAuxNum, CompAuxLib, PieceRef, PieceDate, EcritureLib, Debit, Credit, EcritureLet, DateLet, ValidDate, Montantdevise, Idevise. Les séparateurs usuels sont la tabulation, la barre verticale et le point-virgule ; les dates sont au format AAAAMMJJ et les montants souvent avec une virgule décimale.

La commande `fec` du script agrège les écritures par compte (balance reconstituée), contrôle l'équilibre de chaque écriture, signale les codes inconnus du plan et calcule le résultat provisoire. Elle ne remplace pas le test de conformité formelle de l'administration fiscale (outil Test Compta Demat de la DGFiP) à passer avant un contrôle.
