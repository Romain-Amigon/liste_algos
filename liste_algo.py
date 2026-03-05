# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 01:46:56 2026

@author: amigo
"""

import heapq

def heuristique(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grille, depart, arrivee):
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
                    priorite = nouveau_cout + heuristique(arrivee, suivant)
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

from collections import deque

def bfs(grille, depart, arrivee):
    file = deque([depart])
    visites = set([depart])
    came_from = {depart: None}
    voisins = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while file:
        courant = file.popleft()

        if courant == arrivee:
            break

        for dx, dy in voisins:
            suivant = (courant[0] + dx, courant[1] + dy)
            if 0 <= suivant[0] < len(grille) and 0 <= suivant[1] < len(grille[0]) and grille[suivant[0]][suivant[1]] == 0:
                if suivant not in visites:
                    visites.add(suivant)
                    file.append(suivant)
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

import math

def minimax(etat, profondeur, maximisant, alpha=-math.inf, beta=math.inf):
    if profondeur == 0 or etat.est_terminal():
        return etat.evaluer()

    if maximisant:
        max_eval = -math.inf
        for enfant in etat.obtenir_enfants():
            evaluation = minimax(enfant, profondeur - 1, False, alpha, beta)
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for enfant in etat.obtenir_enfants():
            evaluation = minimax(enfant, profondeur - 1, True, alpha, beta)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break

        return min_eval


import math
import random

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_legal_moves()

    def uct_select_child(self):
        s = sorted(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))
        return s[-1]

    def add_child(self, move, state):
        n = Node(state=state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(n)
        return n

    def update(self, result):
        self.visits += 1
        self.wins += result

def mcts(root_state, iterations):
    root_node = Node(state=root_state)

    for _ in range(iterations):
        node = root_node
        state = root_state.clone()

        while not node.untried_moves and node.children:
            node = node.uct_select_child()
            state.make_move(node.move)

        if node.untried_moves:
            move = random.choice(node.untried_moves)
            state.make_move(move)
            node = node.add_child(move, state)

        while state.get_legal_moves():
            state.make_move(random.choice(state.get_legal_moves()))

        while node is not None:
            node.update(state.get_result(node.state.current_player))
            node = node.parent

    return sorted(root_node.children, key=lambda c: c.visits)[-1].move
