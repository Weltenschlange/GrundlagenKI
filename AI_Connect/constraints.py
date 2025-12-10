class Constraint():

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
            
            # If not found, extract any attribute value from left side
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