import re

class PreProcess:
    PATTERNS = {
        "not_at_position": re.compile(r"(.+)\s+is\s+not\s+in\s+the\s+(\w+)\s+house"),
        "at_position": re.compile(r"(.+)\s+(?:is\s+)?in\s+the\s+(\w+)\s+house"),
        "next_to": re.compile(r"(.+)\s+and\s+(.+)\s+are\s+next\s+to\s+each\s+other"),
        "direct_left": re.compile(r"(.+)\s+is\s+directly\s+(?:left|to\s+the\s+left)\s+of\s+(.+)"),
        "left_of": re.compile(r"(.+)\s+is\s+(?:somewhere\s+)?to\s+the\s+left\s+of\s+(.+)"),
        "distance": re.compile(r"there\s+(?:is|are)\s+(\w+)\s+house[s]?\s+between\s+(.+?)\s+and\s+(.+)"),
        "same": re.compile(r"(.+)\s+is\s+(.+)")
    }

    def preprocess_puzzle(self, puzzle_text):

        parts = re.split(r'##\s*clues:', puzzle_text, flags=re.IGNORECASE)
        
        if len(parts) < 2:
            return "", []
        
        characteristics_text = parts[0]
        clues_text = parts[1]
        
        # Extract clues, removing the number prefix (e.g., "1. ", "2. ")
        clues = []
        for line in clues_text.split('\n'):
            line = line.strip()
            if line:
                # Remove leading number and period (e.g., "1. ", "2. ")
                clue = re.sub(r'^\d+\.\s+', '', line)
                if clue:
                    clues.append(clue)
        
        return characteristics_text, clues

    def extract_attributes(self, characteristics_text):
        """Extract attribute columns from characteristics section."""
        attributes = {}
        
        lines = characteristics_text.split('\n')
        
        for line in lines:
            # Match lines that have format: " - Description: `value1`, `value2`, ..."
            match = re.match(r'\s*-\s*(.+?):\s*(.+)', line)
            if match:
                description = match.group(1).strip()
                values_str = match.group(2)

                words = description.split()
                attr_name = words[-1] if words else "unknown"
                
                # Extract all backtick-quoted values
                values = re.findall(r'`([^`]+)`', values_str)
                
                if values:
                    attributes[attr_name] = values
        
        return attributes

    def extract_symbols(self, clue, known_entities):
        """
        Extract entity references from a clue based on known entities.
        Also extract position numbers (first, second, third, etc.)
        
        Args:
            clue: The normalized clue text
            known_entities: List of all known attribute values
        
        Returns:
            Dict with 'entities' (list) and 'position' (int or None)
        """
        entities = [e for e in known_entities if e.lower() in clue.lower()]
        
        # Extract position if present (first, second, third, etc.)
        position_map = {
            'first': 0, 'second': 1, 'third': 2, 'fourth': 3, 'fifth': 4,
            'sixth': 5, 'seventh': 6, 'eighth': 7, 'ninth': 8, 'tenth': 9
        }
        position = None
        for pos_word, pos_num in position_map.items():
            if pos_word in clue.lower():
                position = pos_num
                break
        
        return {'entities': entities, 'position': position}

    def parse_puzzle_clues(self, attrs_df, clues):
        """
        Parse all clues from the puzzle using the full pipeline.
        
        Args:
            puzzle_text: The raw puzzle text
        
        Returns:
            List of tuples: (original_clue, constraint_type, symbols, match_groups)
        """
        known_entities = []
        for col in attrs_df.columns:
            known_entities.extend(attrs_df[col].tolist())
        
        parsed_clues = []
        
        for _, clue in enumerate(clues, 1):
            try:
                ctype, symbols, groups = self.parse_clue(clue, known_entities)
                parsed_clues.append((clue, ctype, symbols, groups))
            except ValueError as e:
                parsed_clues.append((clue, "UNKNOWN", [], ()))
        
        return parsed_clues
    
    def proccess(self, puzzle_text):
        characteristics_text, clues = self.preprocess_puzzle(puzzle_text)

        attrs = self.extract_attributes(characteristics_text)

        return attrs, clues

