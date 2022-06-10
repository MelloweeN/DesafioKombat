# -*- coding: utf-8 -*-
from flask import render_template
from flask.views import View
from app import app

player_techniques = {
    "base": {
        "S": {
            "name": "Abajo",
            "action": "se mueve"
        },
        "W": {
            "name": "Arriba",
            "action": "se mueve"
        },
        "A": {
            "name": "Izquierda",
            "action": "se mueve a la"
        },
        "D": {
            "name": "Derecha",
            "action": "se mueve a la"
        },
        "P": {
            "name": "Puñetazo",
            "combo_points": 1,
            "action": "ataca con un"
        },
        "K": {
            "name": "Patada",
            "combo_points": 1,
            "action": "ataca con una"
        }
    },
    "super": {
        "DSD": {
            "name": "Taladoken",
            "combo_points": 3,
            "hit": "P",
            "action": "conecta un"
        },
        "SD": {
            "name": "Remuyuken",
            "combo_points": 2,
            "hit": "K",
            "action": "usa un"
        },
        "SA": {
            "name": "Remuyuken",
            "combo_points": 3,
            "hit": "K",
            "action": "usa un"
        },
        "ASA": {
            "name": "Taladoken",
            "combo_points": 2,
            "hit": "P",
            "action": "conecta un"
        }
    }
}


class Base(View):

    def player_start(self, fight_combination):
        player1_movements = len([x for x in fight_combination[self.PLAYER1]['movimientos'] if x])
        player1_hits = len([x for x in fight_combination[self.PLAYER1]['golpes'] if x])
        player1_combination = player1_movements + player1_hits

        player2_movements = len([x for x in fight_combination[self.PLAYER2]['movimientos'] if x])
        player2_hits = len([x for x in fight_combination[self.PLAYER2]['golpes'] if x])
        player2_combination = player2_movements + player2_hits

        if player1_combination < player2_combination:
            return self.PLAYER1

        if player1_combination == player2_combination:
            if player1_movements < player2_movements:
                return self.PLAYER1
            elif player1_movements > player2_movements:
                return self.PLAYER2

            if player1_hits < player2_hits:
                return self.PLAYER1
            elif player1_hits > player2_hits:
                return self.PLAYER2

            return self.PLAYER1

        return self.PLAYER2
        

    def find_superpower(self, movement, hit):
        all_movements = []
        save_mov = ''
        for m, h in player_techniques['super'].items():
            if m in movement:
                if player_techniques['super'][m]['hit'] == hit:
                    save_mov = player_techniques['super'][m]
                    movement = movement.replace(m, ' ')
                    hit = ''
                    break

        for c in movement:
            if c != ' ':
                all_movements.append(player_techniques['base'][c])
            elif save_mov:
                all_movements.append(save_mov)

        if hit:
            all_movements.append(player_techniques['base'][hit])

        return all_movements

    def format_relator(self, move, movement, qty_movements):
        string = "{concat} {type} {name}".format(concat=" y" if movement == qty_movements and qty_movements > 1 else '' if movement == 1 else ",", type=move["action"], name=move['name'])
        if move.get('combo_points', None):
            string += ". Quitando {} puntos".format(move["combo_points"])
        return string
   

    def execute_movement(self, fight_combination, fighter, opponent, turn):
        msg = []
        if len(fight_combination[fighter]['movimientos']) > turn:
            mov = fight_combination[fighter]['movimientos'][turn]
            hit = fight_combination[fighter]['golpes'][turn]

            movements = self.find_superpower(mov, hit)
            msg.append(self.PLAYER_CHOICES[fighter]['name'])
            qty_movements = len(movements)
            movement = 1

            for mov in movements:
                self.PLAYER_CHOICES[opponent]['energy'] = int(self.PLAYER_CHOICES[opponent]['energy']) - mov.get('combo_points', 0)
                msg.append(self.format_relator(mov, movement, qty_movements))
                movement += 1
        return "".join(msg)

        
    def fight(self, fight_combination):
        relator = []
        finish_him = False
        start_fight = self.player_start(fight_combination)
        opponent = self.PLAYER1 if start_fight == self.PLAYER2 else self.PLAYER2
        turn = 0
        
        while not finish_him:
            if self.PLAYER_CHOICES[start_fight]['energy'] > 0:
                message = self.execute_movement(fight_combination, start_fight, opponent, turn)
                if message:
                    relator.append(message)
            
            if self.PLAYER_CHOICES[opponent]['energy'] > 0:
                message = self.execute_movement(fight_combination, opponent, start_fight, turn)
                if message:
                    relator.append(message)

            turn += 1

            if self.PLAYER_CHOICES[start_fight]['energy'] <= 0 or self.PLAYER_CHOICES[opponent]['energy'] <= 0:
                finish_him = True
                winner_is = start_fight if self.PLAYER_CHOICES[start_fight]['energy'] > 0 else opponent
                relator.append("{} Gana la pelea y queda con {} puntos de energía".format(self.PLAYER_CHOICES[winner_is]['name'], self.PLAYER_CHOICES[winner_is]['energy']))

        return [relator, "Inicia la Pelea: {}".format(self.PLAYER_CHOICES[start_fight].get('name'))]

    
    def dispatch_request(self):
        self.ENERGY_MAX = 6
        self.PLAYER1 = 'player1'
        self.PLAYER2 = 'player2'

        self.PLAYER_CHOICES = {
            self.PLAYER1: {
                "name": 'Tonyn Stallone',
                "energy": self.ENERGY_MAX
            },
            self.PLAYER2:  {
                "name": 'Arnaldor Shuatseneguer',
                "energy": self.ENERGY_MAX
            }
        }

        relator, fight_first = self.fight(self.fight_combination)
    
        return render_template('fight.html', relator=relator, fight_first=fight_first)


class Fight1(Base):

    def __init__(self):
        self.fight_combination = {
            "player1": {
                "movimientos": ["D", "DSD", "S", "DSD", "SD"],
                "golpes": ["K", "P", "", "K", "P"]
            },
            "player2": {
                "movimientos": ["SA", "SA", "SA", "ASA", "SA"],
                "golpes": ["K", "", "K", "P", "P"]
            }
        }

class Fight2(Base):

    def __init__(self):
        self.fight_combination = {
            "player1": {
                "movimientos": ["SDD", "DSD", "SA", "DSD"],
                "golpes": ["K", "P", "K", "P"]
            }, 
            "player2": {
                "movimientos": ["DSD", "WSAW", "ASA", "", "ASA", "SA"],
                "golpes": ["P", "K", "K", "K", "P", "K"]
            }
        }


class Fight3(Base):

    def __init__(self):
        self.fight_combination = {
            "player1": {
                "movimientos": ["DSD", "S"],
                "golpes": ["P", ""]
            },
            "player2": {
                "movimientos": ["", "ASA", "DA", "AAA", "", "SA"],
                "golpes": ["P", "", "P", "K", "K", "K"]
            }
        }


class Home(View):

    def dispatch_request(self):
    
        return render_template('index.html')
        

app.add_url_rule('/', view_func=Home.as_view(''))
app.add_url_rule('/fight1', view_func=Fight1.as_view('fight1'))
app.add_url_rule('/fight2', view_func=Fight2.as_view('fight2'))
app.add_url_rule('/fight3', view_func=Fight3.as_view('fight3'))
