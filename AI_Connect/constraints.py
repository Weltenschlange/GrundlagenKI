class Constraint():

    def get_info(self):
        raise NotImplementedError()

    def _replace_edgecases(self, text:str):
        if text.endswith("ing"):
            text = text[:-3]
        if text.endswith("s"):
            text = text[:-1]
        if text == "swede":
            text = text[:-1]

        return text


    def __init__(self, attributes: dict, clue: str):
        self.attributes = attributes
        self.clue = clue
        pass

    def _extract_attribute_from_text(self, text):
        for key in self.attributes.keys():
            for value in self.attributes[key]:
                value = self._replace_edgecases(value)
                if value in text:
                    return (value,key)
                
        return None
    def is_valid(self, attributes):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, attributes):
        raise NotImplementedError()
    
class IdentityConstrain(Constraint):

    def get_info(self):
        return f"IdentityConstrain:  {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    # the person's child is named fred is peter.
    # alice is the person who is tall.
    # the person who uses an iphone 13 is the person who is a teacher.
    # the person whose mother's name is janelle is the person who is an artist.
    def _parse_attributes(self):
        temp = self.clue.split(" is ")

        if len(temp) == 4:
            # Structure: "subject1 is attr1 is subject2 is attr2"
            # temp[0] = subject1, temp[1] = attr1, temp[2] = subject2, temp[3] = attr2
            self.attr1 = self._extract_attribute_from_text(temp[1])
            self.attr2 = self._extract_attribute_from_text(temp[3])
        if len(temp) == 3:
            self.attr1 = None
            for attr_key in self.attributes.keys():
                if attr_key in temp[0]:
                    for value in self.attributes[attr_key]:
                        value = self._replace_edgecases(value)
                        if value in temp[1]:
                            self.attr1 = (value, attr_key)
                            break
                    if self.attr1:
                        break
            if not self.attr1:
                self.attr1 = self._extract_attribute_from_text(temp[1])
            if not self.attr1:
                self.attr1 = self._extract_attribute_from_text(temp[0])
            
            self.attr2 = self._extract_attribute_from_text(temp[2])
        elif len(temp) == 2:
            self.attr1 = self._extract_attribute_from_text(temp[0])
            self.attr2 = self._extract_attribute_from_text(temp[1])
        else:
            pass
        


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.attr2:tuple = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()
    
class NextToConstrain(Constraint):

    def get_info(self):
        return f"NextToConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    #the cat lover and the person who loves biography books are next to each other.
    #the person in a ranch style home and the person whose mother's name is kailyn are next to each other.
    def _parse_attributes(self):
        # Split by " and " to get the two entities
        parts = self.clue.split(" and ")
        
        if len(parts) >= 2:
            # Extract from the first part (before " and ")
            self.attr1 = self._extract_attribute_from_text(parts[0])
            
            # Extract from the second part (after " and ", before " are next to each other")
            # Remove the " are next to each other" suffix if present
            second_part = parts[1]
            if " are next to each other" in second_part:
                second_part = second_part.replace(" are next to each other", "")
            
            self.attr2 = self._extract_attribute_from_text(second_part)


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.attr2:tuple = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()
    
class DistanceConstrain(Constraint):
    def get_info(self):
        return f"DistanceConstrain: {self.clue}\ndistance:{self.distance}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    #DISTANCE: there is one house between X and Y
    #DISTANCE: there are two houses between X and Y
    def _parse_attributes(self):
        # Extract distance from clue
        distance_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10
        }
        
        self.distance = 1  # Default
        clue_lower = self.clue.lower()
        
        # Find the distance word in the clue
        for word, value in distance_words.items():
            if word in clue_lower:
                self.distance = value
                break
        
        # Extract entities from "between X and Y"
        if "between " in clue_lower:
            
            between_index = clue_lower.find("between ")
            after_between = self.clue[between_index + 8:]  
            
            parts = after_between.split(" and ")
            
            if len(parts) >= 2:
                self.attr1 = self._extract_attribute_from_text(parts[0])
                second_part = parts[1].rstrip(".")
                self.attr2 = self._extract_attribute_from_text(second_part)


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.attr2:tuple = None
        self.distance = 1
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()


class LeftConstrain(Constraint):

    def get_info(self):
        return f"LeftConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def _parse_attributes(self):
        if " is somewhere to the left of " in self.clue:
            parts = self.clue.split(" is somewhere to the left of ")
            
            if len(parts) == 2:
                self.attr1 = self._extract_attribute_from_text(parts[0])
                
                second_part = parts[1].rstrip(".")
                self.attr2 = self._extract_attribute_from_text(second_part)


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.attr2:tuple = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()
    
class RightConstrain(Constraint):

    def get_info(self):
        return f"RightConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def _parse_attributes(self):
        if " is somewhere to the right of " in self.clue:
            parts = self.clue.split(" is somewhere to the right of ")
            
            if len(parts) == 2:
                self.attr1 = self._extract_attribute_from_text(parts[0])
                
                second_part = parts[1].rstrip(".")
                self.attr2 = self._extract_attribute_from_text(second_part)


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.attr2:tuple = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()



