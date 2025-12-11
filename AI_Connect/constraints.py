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
                value_modified = self._replace_edgecases(value)
                if value_modified in text:
                    return (value, key)
    
    def _extract_attribute_from_text_with_key(self, key, text):
        for value in self.attributes[key]:
            value_modified = self._replace_edgecases(value)
            if value_modified in text:
                return (value, key)
                
        return None
    def is_valid(self, attributes):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, attributes):
        raise NotImplementedError()
    
    def _get_position_by_attribute(self, attr_value, attr_key, currentSolution):
        """Find the position of a person with a specific attribute value."""
        for pos, attrs in currentSolution.items():
            if attrs.get(attr_key) == attr_value:
                return pos
        return None
    
class IdentityConstrain(Constraint):

    def get_info(self):
        return f"IdentityConstrain:  {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"

    def is_valid(self, currentSolution):
        """Identity constraint: attr1 and attr2 must belong to the same person."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        # If both are unassigned, constraint is satisfied (can be assigned later)
        if pos1 is None and pos2 is None:
            return True
        
        # If one is assigned and the other is not, it's still potentially valid
        if pos1 is None or pos2 is None:
            return True
        
        # If both are assigned, they must be to the same position
        return pos1 == pos2
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        # If both are assigned to different positions, both are wrong
        if pos1 is not None and pos2 is not None and pos1 != pos2:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []

    def _parse_attributes(self):
        parts = self.clue.split(" is ")

        if len(parts) == 4:
            self.attr1 = self._extract_attribute_from_text(parts[1])
            self.attr2 = self._extract_attribute_from_text(parts[3])
        if len(parts) == 3:
            self.attr1 = None
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

class NextToConstrain(Constraint):

    def get_info(self):
        return f"NextToConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"

    def is_valid(self, currentSolution):
        """Next-to constraint: attr1 and attr2 must be in adjacent positions."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is None or pos2 is None:
            return True
        
        return abs(pos1 - pos2) == 1
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is not None and pos2 is not None and abs(pos1 - pos2) != 1:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []

    def _parse_attributes(self):
        parts = self.clue.split(" and ")
        
        if len(parts) >= 2:
            if "person's child" in parts[0]:
                self.attr1 = self._extract_attribute_from_text_with_key("child", parts[0])
            else:
                self.attr1 = self._extract_attribute_from_text(parts[0])
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

class DistanceConstrain(Constraint):
    def get_info(self):
        return f"DistanceConstrain: {self.clue}\ndistance:{self.distance}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Distance constraint: attr1 and attr2 must be exactly 'distance' positions apart."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is None or pos2 is None:
            return True
        
        return abs(pos1 - pos2) == self.distance + 1  # +1 because there are N houses between means distance N+1
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is not None and pos2 is not None and abs(pos1 - pos2) != self.distance + 1:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []
    
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
        

        if " and " in clue_lower:
            parts = self.clue.split(" and ")
            
            if len(parts) >= 2:

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
        self.distance = 1
        self._parse_attributes()

class LeftConstrain(Constraint):

    def get_info(self):
        return f"LeftConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Left constraint: attr1 must be somewhere to the left of attr2."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is None or pos2 is None:
            return True
        
        return pos1 < pos2
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is not None and pos2 is not None and pos1 >= pos2:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []
    
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

class RightConstrain(Constraint):

    def get_info(self):
        return f"RightConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Right constraint: attr1 must be somewhere to the right of attr2."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is None or pos2 is None:
            return True
        
        return pos1 > pos2
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is not None and pos2 is not None and pos1 <= pos2:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []
    
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

class DirectLeftConstrain(Constraint):

    def get_info(self):
        return f"DirectLeftConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Direct left constraint: attr1 must be directly left of attr2 (adjacent, attr1 first)."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is None or pos2 is None:
            return True
        
        return pos2 - pos1 == 1
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is not None and pos2 is not None and pos2 - pos1 != 1:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []
    
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

class DirectRightConstrain(Constraint):

    def get_info(self):
        return f"DirectRightConstrain: {self.clue}\nattr1:{self.attr1}\nattr2:{self.attr2}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Direct right constraint: attr1 must be directly right of attr2 (adjacent, attr1 second)."""
        if not self.attr1 or not self.attr2:
            return True
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is None or pos2 is None:
            return True
        
        return pos1 - pos2 == 1
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or not self.attr2:
            return []
        
        attr1_val, attr1_key = self.attr1
        attr2_val, attr2_key = self.attr2
        
        pos1 = self._get_position_by_attribute(attr1_val, attr1_key, currentSolution)
        pos2 = self._get_position_by_attribute(attr2_val, attr2_key, currentSolution)
        
        if pos1 is not None and pos2 is not None and pos1 - pos2 != 1:
            return [(attr1_val, attr1_key), (attr2_val, attr2_key)]
        
        return []
    
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

class PositionAbsoluteConstrain(Constraint):

    def get_info(self):
        return f"PositionAbsoluteConstrain: {self.clue}\nPosition:{self.pos}\nattr1:{self.attr1}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Absolute position constraint: attr1 must be in position self.pos."""
        if not self.attr1 or self.pos is None:
            return True
        
        attr_val, attr_key = self.attr1
        pos = self._get_position_by_attribute(attr_val, attr_key, currentSolution)
        
        if pos is None:
            return True
        
        return pos == self.pos
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or self.pos is None:
            return []
        
        attr_val, attr_key = self.attr1
        pos = self._get_position_by_attribute(attr_val, attr_key, currentSolution)
        
        if pos is not None and pos != self.pos:
            return [(attr_val, attr_key)]
        
        return []
    
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

class PositionAbsoluteNegativeConstrain(Constraint):

    def get_info(self):
        return f"PositionAbsoluteNegativeConstrain: {self.clue}\nPosition:{self.pos}\nattr1:{self.attr1}\nattributes:{self.attributes}\n"
    
    def is_valid(self, currentSolution):
        """Negative absolute position constraint: attr1 must NOT be in position self.pos."""
        if not self.attr1 or self.pos is None:
            return True
        
        attr_val, attr_key = self.attr1
        pos = self._get_position_by_attribute(attr_val, attr_key, currentSolution)
        
        if pos is None:
            return True
        
        return pos != self.pos
    
    def get_wrong_attributes(self, currentSolution):
        """Return attributes that violate this constraint."""
        if not self.attr1 or self.pos is None:
            return []
        
        attr_val, attr_key = self.attr1
        pos = self._get_position_by_attribute(attr_val, attr_key, currentSolution)
        
        if pos is not None and pos == self.pos:
            return [(attr_val, attr_key)]
        
        return []
    
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
        
        if " is not in the " in clue_lower:
            parts = self.clue.split(" is not in the ")
            
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