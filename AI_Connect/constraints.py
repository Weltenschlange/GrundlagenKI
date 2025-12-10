class Constraint():
    def __init__(self, attributes: dict, clue: str):
        self.attributes = attributes
        self.clue = clue
        pass

    def _extract_attribute_from_text(self, text):
        for key in self.attributes.keys():
            for value in self.attributes[key]:
                if value in text:
                    return (value,key)
                
        return None
    def is_valid(self, attributes):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, attributes):
        raise NotImplementedError()
    
class IdentityConstrain(Constraint):

    # IDENTITY: the person's child is named fred is peter.
    # IDENTITY: alice is the person who is tall.
    def _parse_attributes(self):
        temp = self.clue.split(" is ")

        if len(temp) > 2:
            self.attr1 = None
            for attr_key in self.attributes.keys():
                if attr_key in temp[0]:
                    for value in self.attributes[attr_key]:
                        if value in temp[1]:
                            self.attr1 = (value, attr_key)
                            break
                    if self.attr1:
                        break
            
            # If not found, extract any attribute value from left side
            if not self.attr1:
                self.attr1 = self._extract_attribute_from_text(temp[0])
            

            self.attr2 = self._extract_attribute_from_text(temp[3])
        
        


    def __init__(self, attributes: dict, clue: str):
        super().__init__(attributes, clue)
        self.attr1:tuple = None
        self.attr2:tuple = None
        self._parse_attributes()


    def is_valid(self, currentSolution):
        raise NotImplementedError()
    
    def get_wrong_attributes(self, currentSolution):
        raise NotImplementedError()