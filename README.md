# coda_lib
Interprétation des fichiers bancaires au format coda

## Fonction trt_file
Interpéter le fichier coda 
Cette méthode prend en paramètre le contenu du fichier coda et renvoie un dictionnaire avec les informations.
Contenu du dictionnaire:
- fichier
	- date_création (du fichier coda)
	- inst_fin_code (code de l'institution financière - nombre entier)
	- inst_fin_nom (nom de l'institution financière)
	- destinataire_nom (nom destinataire fichier coda)
	- destinataire_bic (bic destinataire fichier coda)
	- version (version fichier coda)
	- numéro
	- nom_titulaire
	- libellé_compte
- devise
- ancien_solde
	- date
	- valeur
- mouvements
	- {numéro mouvement dans le fichier coda}
		- montant
		- date_valeur
		- communication
		- communication_type
		- date_comptabilisation
		- contrepartie_compte
		- contrepartie_nom
- nouveau_solde
	- date
	- valeur