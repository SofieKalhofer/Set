import pygame
import random as rd
import copy

card_width = 70
card_height = 100
#abstand zwischen den karten auf der rechten seite
margin = 10
#koordinaten der linken oberen ecke des karten blocks rechts
block_x = 200
block_y = 90
#koordinaten der linken oberen ecke des next knopfes
nxt_x = block_x+2*(card_width+margin)-20
nxt_y = block_y+3*(card_height+margin)+10
#maße des next knopfes
nxt_xx = 200
nxt_yy = 45

pygame.init()

screen = pygame.display.set_mode((700,600))
pygame.display.set_caption('Set')

class Card:
    #eigenschaften für alle karten. eine instanz hat eigenschaften als int aus [0,1,2]
    #allprops wird in Card.repr() benutzt um das für den nutzer zu übersetzen
    allprops = [["leer",
                 "gestrichelt",
                 "voll"],
                ["eins",
                 "zwei",
                 "drei"],
                ["rot",
                 "grün",
                 "blau"],
                ["wurm",
                 "raute",
                 "oval"]]

    width = card_width
    height = card_height

    #constructor: nimmt eigenschaftenliste, wenn keine gegeben werden die random festgelegt
    def __init__(self, props = None):
        if not props == None:
            self.props = props
        else:
            self.props = [rd.randint(0,2) for i in range(0,4)]
        #bild abrufen
        s = ''
        for p in self.props:
            s += str(p)
        path = './pics/' + s + '.png'
        self.img = pygame.transform.scale(pygame.image.load(path).convert(),(self.width,self.height))
        #hitbox, erstmal oben links
        self.l = 0
        self.r = self.width
        self.t = 0
        self.b = self.height

    #eigenschaft von zahl zu wort übersetzen
    def get_prop(self,p):
        return self.allprops[p][self.props[p]]

    #alle eigenschaften ausdrucken
    def repr(self):
        for i in range(0,4):
            print(self.get_prop(i))

    #mit einer weiteren karte die dritte zurück geben, die das set vervollständigt
    def find_third(self,card2):
        def calc(a,b):
            su = int(a)+int(b)
            if su%2==0:
                return int(su/2)
            else:
                return (su+1)%4
        p = []
        for i in range(0,4):
            p.append(calc(self.props[i],card2.props[i]))
        return Card(p)

    #erzeugt neue karte die sich in eigenschaft p um x von self unterscheidet
    def mod(self,p,x):
        new_props = copy.deepcopy(self.props)
        new_props[p] = (new_props[p]+x)%3
        new_card = Card(new_props)
        return new_card

    #ändert die koordinaten
    def set_pos(self,x,y):
        self.l = x
        self.r = x+self.width
        self.t = y
        self.b = y+self.height

    #zeigt das bild der karte an seinen koordinaten an
    def displ(self):
        screen.blit(self.img,(self.l,self.t))

    #gibt zurück ob (x,y) im bereich der karte liegt
    def is_clicked(self,x,y):
        if self.l < x and self.r > x and self.t < y and self.b > y:
            is_clicked = True
        else:
            is_clicked = False
        return is_clicked

#zeigt zwei karten links, 18 karten rechts an und next-knopf
#attribute: card1, card2, right, third_exists
class run:
    def __init__(self,counter=0):
        self.counter = counter+1
        screen.fill((255,255,255))
        #next knopf
        nxt = pygame.transform.scale(pygame.image.load('./pics/next.png'),(nxt_xx,nxt_yy))
        screen.blit(nxt,(nxt_x,nxt_y))

        #linke karten erzeugen und anzeigen
        self.card1 = Card()
        self.card2 = Card()
        # die beiden karten sollten nicht gleich sein
        while(self.card1.props == self.card2.props):
            self.card2 = Card()
        self.card1.set_pos(50,145)
        self.card2.set_pos(50,255)
        self.card1.displ()
        self.card2.displ()

        #dritte karte erzeugen
        card3 = self.card1.find_third(self.card2)

        #aus den drei karten right befüllen und mischen
        self.right = [card.mod(p,x) for card in [self.card1,self.card2,card3] for p in range(4) for x in [1,2]]
        self.right.append(self.card1.find_third(self.card2))
        self.right.append(self.card1.find_third(self.card2))
        rd.shuffle(self.right)

        #die ersten 18 elemente anzeigen
        for i in range(6):
            for j in range(3):
                self.right[i*3+j].set_pos(block_x+i*(card_width+margin),block_y+j*(card_height+margin))
                self.right[i*3+j].displ()

        #third_exists gibt an ob die richtige karte unter den angezeigten ist
        self.third_exists = False
        for i in range(0,18):
            if self.right[i].props == self.card1.find_third(self.card2).props:
                self.third_exists = True
                break

        pygame.display.flip()

class score:
    def __init__(self):
        self.value = 0

    def increase(self,v):
        self.value += v

    def eval(self):
        def rep(x):
            m = str(int(int(x)/60))
            tmp = int(x)%60
            if tmp == 0:
                s = '00'
            elif tmp < 10:
                s = '0' + str(tmp)
            else:
                s = str(tmp)
            return m + ':' + s

        self.value += int((pygame.time.get_ticks()-250)/1000)

        try:
            with open("./highscore.txt", "r") as f:
                old_score = f.read()
        except FileNotFoundError:
            old_score = 3600

        if(self.value < int(old_score)):
            print("Neuer Highscore: " + rep(self.value) + " (alter Score: " + rep(old_score) + ")")
            f = open("./highscore.txt", "w")
            f.write(str(self.value))
            f.close()
        else:
            print("Score: " + rep(self.value))
            print("Highscore: " + rep(old_score))




if __name__ == "__main__":

    #initialer run
    s = score()
    game = run(0)

    status = True
    while (status):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                #wenn man nextknopf drückt wird geprüft ob dritte karte da ist, wenn nicht gehts weiter
                if (event.pos[0]>nxt_x and event.pos[0]<(nxt_x+nxt_xx) and event.pos[1]>nxt_y and event.pos[1]<(nxt_y+nxt_yy)):
                    if not game.third_exists:
                        #spiel vorbei nach 27 runs
                        if game.counter >= 27:
                            s.eval()
                            status = False
                        else:
                            game = run(game.counter)
                    else:
                        # fälschlicherweise nextknopf gedrückt -> 20 strafsekunden
                        print('yes there is a set')
                        s.increase(20)

                else:
                    for i in range(0,18):
                        if game.right[i].is_clicked(event.pos[0],event.pos[1]):
                            # richtige karte geklickt
                            if game.right[i].props == game.card1.find_third(game.card2).props:
                                print('correct')
                                # spiel vorbei nach 27 runs
                                if game.counter >= 27:
                                    s.eval()
                                    status = False
                                else:
                                    game = run(game.counter)
                            # falsche karte geklickt -> 20 strafsekunden
                            else:
                                print('incorrect')
                                s.increase(20)
                                break

    pygame.quit()
