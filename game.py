# Cartes
correspondance_cartes = [str(k) for k in range(2,11)] + ["valet", "dame", "roi", "as"]
nb_cartes_par_couleur = len(correspondance_cartes)
nb_figures = 16
class Carte:

	# Constructeur
	def __init__(self, num):
		# Warnings
		if num > nb_cartes_par_couleur:
			print("Carte: Number " + str(num) + " not authorized.")
		self.num = num
		self.figure = (11 <= num <= 13) or (num == 1)
		if (11 <= num <= 13):
			self.price = num - 10
		elif num == 1:
			self.price = 4
		else:
			self.price = 0

	# Retourne le numéro de la carte
	def getNum(self):
		return self.num

	# Retourne le prix à payer
	def getPrice(self):
		return self.price

	# Indique si la carte est une figure
	def isFigure(self):
		return self.figure

	# Donne le nom réel de la carte
	def realName(self):
		if (self.num == 1):
			return correspondance_cartes[-1]
		else:
			return correspondance_cartes[self.num-2]

	# Vérifie si deux cartes sont égales
	def equals(self, carte):
		return self.num == carte.getNum()

	# Convertit en string
	def __str__(self):
		return self.realName()

# Tapis
class Tapis:

	# Constructeur
	def __init__(self):
		self.tapis = []
		self.longueur = 0
		self.nbFigure = 0

	# Ajout d'une carte au tapis
	def add(self, carte):
		self.tapis.append(carte)
		self.longueur += 1
		if carte.isFigure():
			self.nbFigure += 1

	# Retourne le nombre de figures
	def getNbFigures(self):
		return self.nbFigure

	# Le tapis est-il vide ?
	def estVide(self):
		return (self.longueur == 0)

	# Tapis actuel
	def current(self):
		if self.longueur <= 1:
			return (self.tapis[:], self.longueur)
		else:
			return (self.tapis[-2:], 2)

	# Retour du tapis
	def dump(self):
		return (self.tapis, self.longueur)

	# Reset le tapis
	def reset(self):
		self.tapis = []
		self.longueur = 0

	# Convertit en string
	def __str__(self):
		return str([str(x) for x in self.tapis])

# Paquets de cartes
import queue
max_size = 53
class Paquet:

	# Constructeur
	def __init__(self, cartes):
		self.paquet = queue.Queue(max_size)
		self.longueur = 0
		# On remplit le paquet
		for carte in cartes:
			self.paquet.put(Carte(carte))
			self.longueur += 1

	# On pose une carte
	# TODO: Euhhhhh ...
	def pose(self):
		if not self.estVide():
			self.longueur -= 1
			return self.paquet.get()
		return None

	# Le paquet est-il vide ?
	def estVide(self):
		return (self.longueur <= 0)

	# Retourne la longueur du paquet
	def length(self):
		return self.longueur

	# Récupération d'un tapis
	def get(self, tapis):
		cartes, longueur = tapis.dump()
		for carte in cartes:
			self.paquet.put(carte)
		self.longueur += longueur
		tapis.reset()

	# Convertit en string
	def __str__(self):
		return str([str(x) for x in list(self.paquet.queue)])

# Numpy
import numpy as np

# Joueur de bataille Corse
sigma = 10
class Joueur:

	# Constructeur
	def __init__(self, prenom, nom, lossFunction, decisionParam, sizeMemory):
		self.prenom = prenom
		self.nom = nom
		self.lossFunction = lossFunction
		self.decisionParam = decisionParam
		self.memory = []
		self.sizeMemory = sizeMemory
		self.couleurDePeau = "blanc"

	# Decision de poser ou de taper
	def taperOuPoser(self, tapis):
		# Plus il y a de figures, plus la probabilité de taper est forte
		f = lambda x : (self.decisionParam - 1.) / nb_figures + 1
		pos = np.random.uniform(0.,f(tapis.getNbFigures()))
		return (pos <= self.decisionParam)

	# Le joueur agit
	def agir(self, k):
		return np.random.normal(self.lossFunction(k),sigma)

	# Convertit en string
	def __str__(self):
		return self.prenom + " " + self.nom


# Partie de bataille Corse
class Partie:

	# Constructeur
	def __init__(self, paquet, joueurs, debug):

		# Debug
		self.debug = debug

		# Joueurs
		self.nbJoueurs = len(joueurs)
		self.profilJoueurs = joueurs
		self.joueursOFF= []

		# Distribution
		self.nbCartes = len(paquet)
		nb_cartes_init = self.nbCartes // self.nbJoueurs
		reste_cartes_init = self.nbCartes % self.nbJoueurs
		self.paquets = [paquet[i*nb_cartes_init:(i+1)*nb_cartes_init] for i in range(0,self.nbJoueurs,1)]
		for carte in range(reste_cartes_init):
			self.paquets[carte].append(paquet[nb_cartes_init * self.nbJoueurs + carte])

		# Conversion en carte et en paquets
		self.paquets = [Paquet(x) for x in self.paquets]

		# Tapis
		self.tapis = Tapis()

		# Game
		self.main = 0
		self.temps = 0

	# Vérifie si la partie est terminée
	def victory(self):
		joueursON = list(set(range(self.nbJoueurs)) - set(self.joueursOFF))
		if (len(joueursON) == 1):
			return True, joueursON[0]
		else:
			return False, None

	# Calcul des réactivités
	def reactivites(self):
		return [np.random.random() for i in range(self.nbJoueurs)]

	# Tapage
	def tapage(self, succ, defiEnCours):
		decision_succ = self.profilJoueurs[succ].taperOuPoser(self.tapis)
		reactivites = [self.profilJoueurs[i].agir(self.temps) for i in range(self.nbJoueurs)]
		acteur = np.argmin(reactivites)
		if self.debug:
			print("  Les réactivités sont " + str(reactivites))
			print("  " + str(self.profilJoueurs[acteur]) + " est l'acteur.")
		if acteur == succ:
			if decision_succ:
				self.paquets[succ].get(self.tapis)
				if self.debug:
					print("  " + str(self.profilJoueurs[succ]) + " a tapé, son paquet est le suivant : ")
					print("    " + str(self.paquets[succ]))
				defiEnCours = False
		else:
			self.paquets[acteur].get(self.tapis)
			if self.debug:
				print("  " + str(self.profilJoueurs[acteur]) + " a tapé, son paquet est le suivant : ")
				print("    " + str(self.paquets[acteur]))
			defiEnCours = False
		self.main = acteur
		try:
			self.joueursOFF.remove(acteur)
		except:
			pass

	# Met à jour les joueurs OFF
	def updateJoueursOFF(self):
		if self.paquets[self.main].estVide() and (self.main not in self.joueursOFF):
			if self.debug:
				print("  " + str(self.profilJoueurs[self.main]) + " n'a plus de cartes.")
			self.joueursOFF.append(self.main)

	# Tour
	def start(self):
		# Present users
		if self.debug:
			print("Partie is starting ...")
			print("Players are (" + str(self.nbJoueurs) + ") :")
			for joueur in self.profilJoueurs:
				print("  " + str(joueur))
		# La partie est-elle terminée ?
		victory, winner = self.victory()
		price = 0
		defiEnCours = False
		while (not victory):
			# Check for victory
			victory, winner = self.victory()
			# Affichage de la situation actuelle
			if self.debug:
				print("#########################")
				print("Temps : " + str(self.temps))
				print("Main : " + str(self.profilJoueurs[self.main]))
				print("Tapis : " + str(self.tapis))
				print("Joueurs OFF : " + str([str(self.profilJoueurs[i]) for i in self.joueursOFF]))
				print("Prix : " + str(price))
				print("Les paquets des joueurs sont :")
				for joueur in range(self.nbJoueurs):
					print("-> " + str(self.profilJoueurs[joueur]) + " : ")
					print(" " + str(self.paquets[joueur]))
				print("-------------------------")
			# Check la situation actuelle
			last_cards, longueur = self.tapis.current()
			if self.debug:
				print("  Les dernieres cartes du tapis sont : " + str([str(x) for x in last_cards]))
			# Poser la carte
			succ = (self.main+1) % self.nbJoueurs
			self.updateJoueursOFF()
			if not (self.main in self.joueursOFF):
				carte = self.paquets[self.main].pose()
				self.tapis.add(carte)
				if self.debug:
					print("  " + str(self.profilJoueurs[self.main]) + " a posé " + str(carte))
				# Besoin de réagir ?
				besoin = (longueur != 0) and ((last_cards[-1].equals(carte)) or ((longueur == 2) and (last_cards[-2].equals(carte))))
				if self.debug:
					if besoin:
						print("  On peut réagir !")
					else:
						print("  On ne peut pas réagir !")
				if besoin:
					self.tapage(succ, defiEnCours)
				else:
					if not defiEnCours:
						self.main = succ
			elif (self.main in self.joueursOFF):
				self.main = succ

			# Gestion des figures
			if not self.tapis.estVide():
				if carte.isFigure():
					price = carte.getPrice()
					defiEnCours = True
					if self.debug:
						print("  " + str(self.profilJoueurs[(succ-1) % self.nbJoueurs]) + " lance un défi à " + str(self.profilJoueurs[succ]))
					while (succ in self.joueursOFF):
						succ = (succ+1) % self.nbJoueurs
					self.main = succ
				elif defiEnCours:
					price -= 1
				self.updateJoueursOFF()
				if ((price == 0) and defiEnCours) or (defiEnCours and (self.main in self.joueursOFF)):
					price = 0
					defiEnCours = False
					gagnant = (self.main-1) % self.nbJoueurs
					while (gagnant in self.joueursOFF):
						gagnant = (gagnant-1) % self.nbJoueurs
					self.paquets[gagnant].get(self.tapis)
					if self.debug:
						print("  " + str(self.profilJoueurs[gagnant]) + " a gagné le défi, son paquet est le suivant : ")
						print("    " + str(self.paquets[gagnant]))
					self.main = gagnant
			self.temps += 1
		print("The winner is " + str(self.profilJoueurs[winner]))