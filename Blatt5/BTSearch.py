import random

class CSP:
    def __init__(self):
        self.constraints = [] 
        self.needs2Houses = False
    def consistent(self, house1, house2):
        if not self.needs2Houses:
            for c in self.constraints:
                if not c(house1):
                    return False
        else:
            for c in self.constraints:
                if not c(house1, house2):
                    return False
        return True
        

class House:
    def __init__(self):
        self.number = None
        self.color = None
        self.nationality = None
        self.pet = None
        self.drink = None
        self.cigarres = None
    
    def Solved(self):
        return self.number is not None and self.color is not None and self.nationality is not None and self.pet is not None and self.drink is not None and self.cigarres is not None
    def PrintMe(self):
        print(f"{self.number}, {self.color}, {self.nationality}, {self.pet}, {self.drink}, {self.cigarres}")



def CheckConstraints(CSPs, houses):
    for i in range(len(CSPs)):
        c = CSPs[i]
        if c.needs2Houses:
            for h1 in houses:
                for h2 in houses:
                    if(h1 != h2):
                        if(not c.consistent(h1, h2)):
                            return False
        else:
            for h1 in houses:
                if(not c.consistent(h1, None)):
                    return False
    return True

def AllSolved(houses):
    for h in houses:
        if(not h.Solved()):
            return False
    return True

def removeFromList(list_, e):
    result = [i for i in list_ if i != e]
    return result


def BTSearch(houses, CSPs, numbers, colors, nationalities, pets, drinks, cigarettes, index, value):
    if(AllSolved(houses) and CheckConstraints(CSPs, houses)):
        return True
    
    if(index >= len(houses)):
        return False

    if(value == 0):
        for n in numbers:
            houses[index].number = n
            if(CheckConstraints(CSPs, houses)):
                if(BTSearch(houses, CSPs, removeFromList(numbers, n) , colors, nationalities, pets, drinks, cigarettes, index, value+1)):
                    return True
        houses[index].number = None
        return False
    if(value == 1):
        for n in colors:
            houses[index].color = n
            if(CheckConstraints(CSPs, houses)):
                if(BTSearch(houses, CSPs, numbers , removeFromList(colors, n), nationalities, pets, drinks, cigarettes, index, value+1)):
                    return True
        houses[index].color = None
        return False
    if(value == 2):
        for n in nationalities:
            houses[index].nationality = n
            if(CheckConstraints(CSPs, houses)):
                if(BTSearch(houses, CSPs, numbers , colors, removeFromList(nationalities, n), pets, drinks, cigarettes, index, value+1)):
                    return True
        houses[index].nationality = None
        return False
    if(value == 3):
        for n in pets:
            houses[index].pet = n
            if(CheckConstraints(CSPs, houses)):
                if(BTSearch(houses, CSPs, numbers , colors, nationalities, removeFromList(pets, n), drinks, cigarettes, index, value+1)):
                    return True
        houses[index].pet = None
        return False
    if(value == 4):
        for n in drinks:
            houses[index].drink = n
            if(CheckConstraints(CSPs, houses)):
                if(BTSearch(houses, CSPs, numbers , colors, nationalities, pets, removeFromList(drinks, n), cigarettes, index, value+1)):
                    return True
        houses[index].drink = None
        return False
    if(value == 5):
        for n in cigarettes:
            houses[index].cigarres = n
            if(CheckConstraints(CSPs, houses)):
                if(BTSearch(houses, CSPs, numbers , colors, nationalities, pets, drinks, removeFromList(cigarettes, n), index+1, 0)):
                    return True
        houses[index].cigarres = None
        return False
    return False
    
    
    

houses = [House() for i in range(5)]
numbers = [1,2,3,4,5]
colors = ["gelb","blau","rot","weiß","grün"]
nationalities = ["Norweger","Ukrainer","Engländer","Spanier","Japaner"]
pets = ["Fuchs","Pferd","Schnecken","Hund","Zebra"]
drinks = ["Wasser","Tee","Milch","O-Saft","Kaffee"]
cigarettes = ["Kools", "Chesterfield", "OldGold", "LuckyStrike", "Parliaments"]

random.shuffle(numbers)
random.shuffle(colors)
random.shuffle(nationalities)
random.shuffle(pets)
random.shuffle(drinks)
random.shuffle(cigarettes)

CSPs = [CSP() for i in range(14)]

#Der Engländer wohnt im roten Haus.
CSPs[0].needs2Houses = False
CSPs[0].constraints.append(lambda a : a.color == None or a.nationality == None or (a.color == "rot") == (a.nationality == "Engländer" ))

#Der Spanier hat einen Hund.
CSPs[1].needs2Houses=False
CSPs[1].constraints.append(lambda a : a.pet == None or a.nationality == None or (a.pet == "Hund") == (a.nationality == "Spanier"))

#Kaffee wird im grünen Haus getrunken.
CSPs[2].needs2Houses=False
CSPs[2].constraints.append(lambda a : a.drink ==None or a.color == None or (a.drink == "Kaffee") == (a.color == "grün"))

#Der Ukrainer trinkt Tee.
CSPs[3].needs2Houses=False
CSPs[3].constraints.append(lambda a :  a.drink == None or a.nationality == None or (a.drink == "Tee" ) == (a.nationality == "Ukrainer"))

#Das grüne Haus ist direkt rechts vom weißen Haus.
CSPs[4].needs2Houses = True
CSPs[4].constraints.append(lambda a, b : (a.color == None or b.color == None or not ((a.color == "grün") and (b.color == "weiß")) or a.number==None or b.number==None or (a.number - b.number == 1)))

#Der Raucher von Old-Gold-Zigaretten hält Schnecken als Haustiere.
CSPs[5].needs2Houses=False
CSPs[5].constraints.append(lambda a : a.cigarres ==None or a.pet == None or (a.cigarres == "OldGold") == (a.pet == "Schnecken"))

#Die Zigaretten der Marke Kools werden im gelben Haus geraucht.
CSPs[6].needs2Houses=False
CSPs[6].constraints.append(lambda a :  a.cigarres ==None or a.color == None or (a.cigarres == "Kools") == (a.color == "gelb" ))

#Milch wird im mittleren Haus getrunken.
CSPs[7].needs2Houses=False
CSPs[7].constraints.append(lambda a : a.number == None or a.drink == None or ((a.drink == "Milch") == (a.number == 3)))

#Der Norweger wohnt im ersten Haus.
CSPs[8].needs2Houses=False
CSPs[8].constraints.append(lambda a : a.number == None or a.nationality == None or ((a.nationality == "Norweger") == (a.number == 1)))

#Der Mann, der Chesterfield raucht, wohnt neben dem Mann mit dem Fuchs.
CSPs[9].needs2Houses = True
CSPs[9].constraints.append(lambda a, b : (a.cigarres==None or b.pet == None or not ((a.cigarres == "Chesterfield") and (b.pet == "Fuchs")) or a.number==None or b.number==None or (abs(a.number - b.number) == 1)) and not(a.cigarres=="Chesterfield" and a.pet=="Fuchs") )

#Die Marke Kools wird geraucht im Haus neben dem Haus mit dem Pferd.
CSPs[10].needs2Houses = True
CSPs[10].constraints.append(lambda a, b :(a.cigarres == None or b.pet == None or not ((a.cigarres == "Kools") and (b.pet == "Pferd" )) or a.number ==None or b.number==None or (abs(a.number - b.number) == 1)) and not(a.cigarres=="Kools" and a.pet=="Pferd"))
#Der Lucky-Strike-Raucher trinkt am liebsten Orangensaft.
CSPs[11].needs2Houses = False
CSPs[11].constraints.append(lambda a : a.cigarres == None or a.drink == None or (a.cigarres == "LuckyStrike") == (a.drink == "O-Saft"))
#Der Japaner raucht Zigaretten der Marke Parliaments.
CSPs[12].needs2Houses = False
CSPs[12].constraints.append(lambda a : a.cigarres == None or a.nationality == None or (a.cigarres == "Parliaments") == (a.nationality == "Japaner"))
#Der Norweger wohnt neben dem blauen Haus.
CSPs[13].needs2Houses = True
CSPs[13].constraints.append(lambda a, b : (a.nationality == None or b.color == None or not ((a.nationality == "Norweger") and (b.color == "blau")) or a.number ==None or b.number==None or (abs(a.number - b.number) == 1)) and not (a.nationality=="Norweger" and a.color=="blau"))



print (BTSearch(houses, CSPs, numbers, colors, nationalities, pets, drinks, cigarettes, 0, 0))
for h in houses:
    h.PrintMe()