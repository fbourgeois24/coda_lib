""" Interpréter un fichier bancaire au format coda """
from datetime import datetime as dt
from decimal import Decimal 

class coda_file():

	def __init__(self, filepath):
		self.filepath = filepath

	def read_file(self):
		""" Renvoyer le contenu du fichier """
		with open(self.filepath, 'r') as text_file:
			return text_file.read().replace("\r", "").split("\n")

	def trt_file(self, filecontent = None):
		""" 
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


		"""
		if filecontent is None: filecontent = self.read_file()

		data = {}

		for line in filecontent:
			if line == "":
				continue
			if line[0] == "0":
				# Ligne header
				data.setdefault("fichier", {})
				data["fichier"]["date_création"] = dt.strptime(line[5:11], "%d%m%y").date()
				data["fichier"]["inst_fin_code"] = int(line[11:14])
				# Nom institution financière
				if 1 <= data["fichier"]["inst_fin_code"] <= 49:
					data["fichier"]["inst_fin_nom"] = "?"
				elif 50 <= data["fichier"]["inst_fin_code"] <= 99:
					data["fichier"]["inst_fin_nom"] = "Belfius"
				elif 200 <= data["fichier"]["inst_fin_code"] <= 299:
					data["fichier"]["inst_fin_nom"] = "BNP Paribas Fortis"
				elif 300 <= data["fichier"]["inst_fin_code"] <= 399:
					data["fichier"]["inst_fin_nom"] = "ING"
				
				data["fichier"]["destinataire_nom"] = line[34:60].rstrip()
				data["fichier"]["destinataire_bic"] = line[60:71].rstrip()
				data["fichier"]["version"] = int(line[127])

			elif line[0] == "1":
				# Ancien solde
				data.setdefault("fichier", {})
				data["fichier"]["numéro"] = int(line[2:5])
				data["fichier"]["numéro_compte"] = line[5:21]
				data["devise"] = line[39:42]
				sens_transaction = 1 if line[42] == "0" else -1
				data["ancien_solde"] = {
					"date": dt.strptime(line[58:64], "%d%m%y").date(), 
					"valeur" : Decimal(line[43:58]) / 1000 * sens_transaction}
				data["fichier"]["nom_titulaire"] = line[64:90].rstrip()
				data["fichier"]["libellé_compte"] = line[90:125].rstrip()
				
			elif line[0] == "2":
				# Mouvement
				data.setdefault("mouvements", {})
				numéro_mvt = int(line[2:6]) # Numéro interne au coda
				data["mouvements"].setdefault(numéro_mvt, {"communication": ""})

				if line[1] == "1" and int(line[6:10]) == 0:
					# Première ligne du mouvement et première ligne de détail
					sens_mouvement = 1 if line[31] == "0" else -1
					data["mouvements"][numéro_mvt]["montant"] = Decimal(line[32:47]) / 1000 * sens_mouvement
					data["mouvements"][numéro_mvt]["date_valeur"] = dt.strptime(line[47:53], "%d%m%y").date()
					if line[61] == "0":
						# Communication libre
						data["mouvements"][numéro_mvt]["communication"] = line[62:115]
					else:
						# Communication structurée
						data["mouvements"][numéro_mvt]["communication_type"] = line[62:65]
						data["mouvements"][numéro_mvt]["communication"] = line[65:115].rstrip()
					
					data["mouvements"][numéro_mvt]["date_comptabilisation"] = dt.strptime(line[115:121], "%d%m%y").date()

				elif line[1] == "2":
					# Deuxième ligne du mouvement
					data["mouvements"][numéro_mvt]["communication"] += line[10:63]
					

				elif line[1] == "3":
					# Troisième ligne du mouvement
					data["mouvements"][numéro_mvt]["contrepartie_compte"] = line[10:43].rstrip()
					data["mouvements"][numéro_mvt]["contrepartie_nom"] = line[47:82].rstrip()
					data["mouvements"][numéro_mvt]["communication"] += line[82:125]

			elif line[0] == "3":
				# Informations
				data.setdefault("mouvements", {})
				numéro_mvt = int(line[2:6]) # Numéro interne au coda
				data["mouvements"].setdefault(numéro_mvt, {"communication": ""})

				if line[1] == "1":
					# Première ligne information
					data["mouvements"][numéro_mvt]["communication"] += line[40:113]
				if line[1] == "2":
					# Deuxième ligne information
					data["mouvements"][numéro_mvt]["communication"] += line[10:115]
				if line[1] == "3":
					# Troisième ligne information
					data["mouvements"][numéro_mvt]["communication"] += line[10:100]


			elif line[0] == "8":
				# Nouveau solde
				sens_transaction = 1 if line[41] == "0" else -1
				data["nouveau_solde"] = {
					"date": dt.strptime(line[57:63], "%d%m%y").date(), 
					"valeur" : Decimal(line[42:57]) / 1000 * sens_transaction}

				# On supprime les espaces en surnombre dans la communication
				for numero_mvt_ in data["mouvements"]:
					data["mouvements"][numero_mvt_]["communication"] = ' '.join(data["mouvements"][numero_mvt_]["communication"].split())

		return data

	def __enter__(self):
		""" Utilisation avec with """
		return self.trt_file()

	def __exit__(self, *args, **kwargs):
		""" Utilisation avec with """
		pass