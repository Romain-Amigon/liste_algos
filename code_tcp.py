import socket
import struct
import heapq
from collections import deque

class Reseau:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connecter(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def recevoir(self, taille):
        donnees = b''
        while len(donnees) < taille:
            paquet = self.sock.recv(taille - len(donnees))
            if not paquet:
                return None
            donnees += paquet
        return donnees

    def envoyer(self, donnees):
        self.sock.sendall(donnees)

    def fermer(self):
        self.sock.close()

class Utils:
    @staticmethod
    def complement_a_deux(valeur, bits):
        if valeur & (1 << (bits - 1)):
            valeur -= 1 << bits
        return valeur

    @staticmethod
    def extraire_bits(valeur, masque, decalage):
        return (valeur & masque) >> decalage

class Pathfinding:
    @staticmethod
    def heuristique(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def a_etoile(grille, depart, arrivee):
        frontiere = []
        heapq.heappush(frontiere, (0, depart))
        came_from = {depart: None}
        cost_so_far = {depart: 0}
        voisins = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while frontiere:
            _, courant = heapq.heappop(frontiere)
            if courant == arrivee:
                break
            
            for dx, dy in voisins:
                suivant = (courant[0] + dx, courant[1] + dy)
                if 0 <= suivant[0] < len(grille) and 0 <= suivant[1] < len(grille[0]) and grille[suivant[0]][suivant[1]] == 0:
                    nouveau_cout = cost_so_far[courant] + 1
                    if suivant not in cost_so_far or nouveau_cout < cost_so_far[suivant]:
                        cost_so_far[suivant] = nouveau_cout
                        priorite = nouveau_cout + Pathfinding.heuristique(arrivee, suivant)
                        heapq.heappush(frontiere, (priorite, suivant))
                        came_from[suivant] = courant
        
        chemin = []
        courant = arrivee
        while courant != depart:
            chemin.append(courant)
            courant = came_from.get(courant)
            if courant is None:
                return []
        chemin.reverse()
        return chemin

class Agent:
    def __init__(self):
        self.etat = "INIT"
        self.grille = []
        self.position = (0, 0)
        self.objectif = (0, 0)

    def mettre_a_jour_etat(self, donnees_brutes):
        pass

    def agir(self):
        if self.etat == "INIT":
            self.etat = "RECHERCHE"
            return struct.pack('>B', 0x01)
            
        elif self.etat == "RECHERCHE":
            chemin = Pathfinding.a_etoile(self.grille, self.position, self.objectif)
            if chemin:
                self.etat = "DEPLACEMENT"
            return struct.pack('>B', 0x02)
            
        elif self.etat == "DEPLACEMENT":
            return struct.pack('>B', 0x03)

        return struct.pack('>B', 0x00)

def main():
    HOST = '127.0.0.1'
    PORT = 8080
    
    reseau = Reseau(HOST, PORT)
    reseau.connecter()
    agent = Agent()

    try:
        while True:
            donnees = reseau.recevoir(1024)
            if not donnees:
                break
                
            agent.mettre_a_jour_etat(donnees)
            action_a_envoyer = agent.agir()
            reseau.envoyer(action_a_envoyer)
            
    except KeyboardInterrupt:
        pass
    finally:
        reseau.fermer()

if __name__ == "__main__":
    main()
