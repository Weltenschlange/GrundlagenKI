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
    
    def _extract_attribute_from_text_with_key(self, key, text):
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
        parts = self.clue.split(" is ")

        if len(parts) == 4:
            # Structure: "subject1 is attr1 is subject2 is attr2"
            # parts[0] = subject1, parts[1] = attr1, parts[2] = subject2, parts[3] = attr2
            self.attr1 = self._extract_attribute_from_text(parts[1])
            self.attr2 = self._extract_attribute_from_text(parts[3])
        if len(parts) == 3:
            self.attr1 = None
            # for attr_key in self.attributes.keys():
            #     if attr_key in temp[0]:
            #         for value in self.attributes[attr_key]:
            #             value = self._replace_edgecases(value)
            #             if value in temp[1]:
            #                 self.attr1 = (value, attr_key)
            #                 break
            #         if self.attr1:
            #             break
            if "person's child" in parts[0]:
                self.attr1 = self._extract_attribute_from_text_with_key("child", parts[1])

            if not self.attr1:
                self.attr1 = self._extract_attribute_from_text(parts[1])
            if not self.attr1:
                self.attr1 = self._extract_attribute_from_text(parts[0])
            
            self.attr2 = self._extract_attribute_from_text(parts[2])
        elif len(parts) == 2:
            self.attr1 = self._extract_attribute_from_text(parts[0])
            self.attr2 = self._extract_attribute_from_text(parts[1])
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
            if "person's child" in parts[0]:
                self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
            else:
                self.attr1 = self._extract_attribute_from_text(parts[0])
            
            # Extract from the second part (after " and ", before " are next to each other")
            # Remove the " are next to each other" suffix if present
            second_part = parts[1]
            if " are next to each other" in second_part:
                second_part = second_part.replace(" are next to each other", "")
            
            if "person's child" in second_part:
                self.attr2 = self._extract_attribute_from_text_with_key("child", second_part)
            else:
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
    
    def _parse_attributes(self):
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
        
        self.distance = 1 
        clue_lower = self.clue.lower()
        
        for word, value in distance_words.items():
            if word in clue_lower:
                self.distance = value
                break
        
        # Pattern: "there is [distance] house(s) between X and Y"
        # Split by " and " to separate the two entities
        if " and " in clue_lower:
            parts = self.clue.split(" and ")
            
            if len(parts) >= 2:
                # Extract attr1 from the first part (before " and ")
                if "person's child" in parts[0]:
                    self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
                else:
                    self.attr1 = self._extract_attribute_from_text(parts[0])
                
                # Extract attr2 from the second part (after " and ")
                second_part = parts[1].rstrip(".")
                if "person's child" in second_part:
                    self.attr2 = self._extract_attribute_from_text_with_key("child", second_part)
                else:
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
                if "person's child" in parts[0]:
                    self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
                else:
                    self.attr1 = self._extract_attribute_from_text(parts[0])
                
                second_part = parts[1].rstrip(".")
                if "person's child" in second_part:
                    self.attr2 = self._extract_attribute_from_text_with_key("child", second_part)
                else:
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
            
            if len(parts) != 2:
                return

            if "person's child" in parts[0]:
                self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
            else:
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
    
class DirectLeftConstrain(Constraint):

    def get_info(self):
        return f"DirectLeftConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def _parse_attributes(self):
        if " is directly left of " in self.clue:
            parts = self.clue.split(" is directly left of ")
            
            if len(parts) == 2:
                if "person's child" in parts[0]:
                    self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
                else:
                    self.attr1 = self._extract_attribute_from_text(parts[0])
                second_part = parts[1].rstrip(".")
                if "person's child" in second_part:
                    self.attr2 = self._extract_attribute_from_text_with_key("child", second_part)
                else:
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
    
class DirectRightConstrain(Constraint):

    def get_info(self):
        return f"DirectRightConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def _parse_attributes(self):
        if " is directly right of " in self.clue:
            parts = self.clue.split(" is directly right of ")
            
            if len(parts) == 2:
                if "person's child" in parts[0]:
                    self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
                else:
                    self.attr1 = self._extract_attribute_from_text(parts[0])
                second_part = parts[1].rstrip(".")
                if "person's child" in second_part:
                    self.attr2 = self._extract_attribute_from_text_with_key("child", second_part)
                else:
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

class PositionAbsoluteConstrain(Constraint):

    def get_info(self):
        return f"PositionAbsoluteConstrain: {self.clue}\nPosition:{self.pos}\nattr1:{self.attr1}\nattributes:{self.attributes}\n"
    
    def _parse_attributes(self):
        position_words = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "tenth": 10
        }
        
        self.pos = None
        clue_lower = self.clue.lower()
        
        for word, value in position_words.items():
            if word in clue_lower:
                self.pos = value
                break
        
        if " is in the " in clue_lower:
            parts = self.clue.split(" is in the ")
            
            if len(parts) >= 1:
                if "person's child" in parts[0]:
                    self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
                else:
                    self.attr1 = self._extract_attribute_from_text(parts[0])


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.pos = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()

class PositionAbsoluteNegativeConstrain(Constraint):

    def get_info(self):
        return f"PositionAbsoluteNegativeConstrain: {self.clue}\nPosition:{self.pos}\nattr1:{self.attr1}\nattributes:{self.attributes}\n"
    
    def _parse_attributes(self):
        # Pattern: "X is not in the [position] house."
        # Position mapping
        position_words = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4,
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eighth": 8,
            "ninth": 9,
            "tenth": 10
        }
        
        self.pos = None
        clue_lower = self.clue.lower()
        
        # Find position word in the clue
        for word, value in position_words.items():
            if word in clue_lower:
                self.pos = value
                break
        
        # Extract entity from "X is not in the [position] house"
        if " is not in the " in clue_lower:
            # Get the part before " is not in the "
            parts = self.clue.split(" is not in the ")
            
            if len(parts) >= 1:
                # Extract attribute from the first part
                if "person's child" in parts[0]:
                    self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
                else:
                    self.attr1 = self._extract_attribute_from_text(parts[0])

    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.pos = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()