import pandas as pd
import re

class CPSConstraint:
    """Base class for all constraint types."""

    def __init__(self, clue, symbols, groups):
        self.clue = clue
        self.symbols = symbols or {}
        self.groups = groups or ()

    def _known_values(self, attrs_df):
        values = set()
        for col in attrs_df.columns:
            values.update(attrs_df[col].dropna().astype(str).str.lower().tolist())
        return values

    def _entity_positions(self, entity, attrs_df):
        """Return list of row indices where the entity appears in any column."""
        positions = []
        for idx, row in attrs_df.iterrows():
            if any(str(cell).lower() == str(entity).lower() for cell in row.dropna()):
                positions.append(idx)
        return positions

    def is_valid(self, attrs_df):
        """Return True if the constraint only references known values/positions."""
        return len(self.invalid_positions(attrs_df)) == 0

    def invalid_positions(self, attrs_df):
        """Return a list of items describing missing entities or out-of-range positions."""
        raise NotImplementedError("Subclasses must implement invalid_positions")


class EntityPositionConstraint(CPSConstraint):
    """Shared logic for constraints that bind an entity to an explicit position."""

    def _validate_entity(self, attrs_df):
        entities = self.symbols.get("entities", []) or []
        if not entities:
            return [], ["missing entity"]
        ent = entities[0]
        positions = self._entity_positions(ent, attrs_df)
        if not positions:
            return [], [f"unknown entity: {ent}"]
        return positions, []

    def _validate_position(self, attrs_df):
        position = self.symbols.get("position")
        if position is None:
            return ["missing position"]
        if position < 0:
            return [f"invalid position: {position}"]
        if position >= len(attrs_df):
            return [f"position out of range: {position} >= {len(attrs_df)}"]
        return []


class AtPositionConstraint(EntityPositionConstraint):
    def invalid_positions(self, attrs_df):
        issues = []
        positions, ent_issues = self._validate_entity(attrs_df)
        issues.extend(ent_issues)
        issues.extend(self._validate_position(attrs_df))
        if issues:
            return issues

        target = self.symbols.get("position")
        if target not in positions:
            return [target]
        return []


class NotAtPositionConstraint(EntityPositionConstraint):
    def invalid_positions(self, attrs_df):
        issues = []
        positions, ent_issues = self._validate_entity(attrs_df)
        issues.extend(ent_issues)
        issues.extend(self._validate_position(attrs_df))
        if issues:
            return issues

        target = self.symbols.get("position")
        if target in positions:
            return [target]
        return []


class PairwiseConstraint(CPSConstraint):
    """Constraints that reference two entities without explicit positions."""

    def _pair_positions(self, attrs_df):
        entities = self.symbols.get("entities", []) or []

        if len(entities) >= 2:
            a, b = entities[0], entities[1]
        elif len(entities) == 1:
            # Duplicate the single entity if clue implies self-relation (e.g., "german is german").
            a, b = entities[0], entities[0]
        elif len(getattr(self, "groups", ())) >= 2:
            a, b = self.groups[0], self.groups[1]
        else:
            return [], [], ["missing pair entities"]

        pos_a = self._entity_positions(a, attrs_df)
        pos_b = self._entity_positions(b, attrs_df)
        issues = []
        if not pos_a:
            issues.append(f"unknown entity: {a}")
        if not pos_b:
            issues.append(f"unknown entity: {b}")
        return pos_a, pos_b, issues


class NextToConstraint(PairwiseConstraint):
    def invalid_positions(self, attrs_df):
        pos_a, pos_b, issues = self._pair_positions(attrs_df)
        if issues:
            return issues

        for a in pos_a:
            for b in pos_b:
                if abs(a - b) == 1:
                    return []
        return list(set(pos_a + pos_b))


class DirectLeftConstraint(PairwiseConstraint):
    def invalid_positions(self, attrs_df):
        pos_a, pos_b, issues = self._pair_positions(attrs_df)
        if issues:
            return issues

        for a in pos_a:
            for b in pos_b:
                if b - a == 1:
                    return []
        return list(set(pos_a + pos_b))


class LeftOfConstraint(PairwiseConstraint):
    def invalid_positions(self, attrs_df):
        pos_a, pos_b, issues = self._pair_positions(attrs_df)
        if issues:
            return issues

        for a in pos_a:
            for b in pos_b:
                if a < b:
                    return []
        return list(set(pos_a + pos_b))


class SameConstraint(PairwiseConstraint):
    def invalid_positions(self, attrs_df):
        pos_a, pos_b, issues = self._pair_positions(attrs_df)
        if issues:
            return issues

        for a in pos_a:
            for b in pos_b:
                if a == b:
                    return []
        return list(set(pos_a + pos_b))


class DistanceConstraint(PairwiseConstraint):
    def _distance_value(self, attrs_df):
        if not self.groups:
            return None, ["missing distance"]
        distance_word = self.groups[0]
        words_to_int = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }
        distance = words_to_int.get(str(distance_word).lower(), None)
        extra = []
        if distance is None:
            try:
                distance = int(distance_word)
            except (ValueError, TypeError):
                extra.append(f"unknown distance value: {distance_word}")
        if isinstance(distance, int) and distance >= len(attrs_df):
            extra.append(f"distance too large for grid: {distance} >= {len(attrs_df)}")
        return distance, extra

    def invalid_positions(self, attrs_df):
        pos_a, pos_b, issues = self._pair_positions(attrs_df)
        if issues:
            return issues

        distance, dist_issues = self._distance_value(attrs_df)
        issues.extend(dist_issues)
        if issues or distance is None:
            return issues

        target_diff = distance + 1
        for a in pos_a:
            for b in pos_b:
                if abs(a - b) == target_diff:
                    return []
        return list(set(pos_a + pos_b))


class UnknownConstraint(CPSConstraint):
    def invalid_positions(self, attrs_df):  # noqa: ARG002
        return ["unrecognized constraint type"]


class PreProcces:
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
        
        return pd.DataFrame(attributes)

    def normalize(self, clue):
        """
        Normalize clues by removing common linguistic variations.
        Examples:
        - "the german is bob" → "bob is german"
        - "the person who is german is bob" → "bob is german"
        """
        clue = clue.lower()
        clue = clue.replace("the person who is", "")
        clue = clue.replace("the person who loves", "")
        clue = clue.replace("the person whose", "")
        clue = clue.replace("the person ", "")
        return clue.strip()

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

    def parse_clue(self, clue, known_entities):
        """
        Parse a clue and identify its type and relevant symbols.
        
        Args:
            clue: The clue text
            known_entities: List of all known attribute values
        
        Returns:
            Tuple of (constraint_type, symbol_data, match_groups)
            symbol_data: Dict with 'entities' (list) and 'position' (int or None)
            Example: ("not_at_position", {"entities": ["eric"], "position": 1}, ("eric", "second"))
        
        Raises:
            ValueError: If clue doesn't match any known pattern
        """
        clue = self.normalize(clue)
        
        # Try to match against each pattern type (order matters - check specific patterns first)
        for ctype, pattern in self.PATTERNS.items():
            match = pattern.search(clue)
            if match:
                symbols = self.extract_symbols(clue, known_entities)
                return ctype, symbols, match.groups()
        
        # If no pattern matched, raise an error
        raise ValueError(f"Unrecognized clue format: {clue}")

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

    def build_constraints(self, parsed_clues):
        """Instantiate constraint objects for each parsed clue."""
        factory = {
            "at_position": AtPositionConstraint,
            "not_at_position": NotAtPositionConstraint,
            "next_to": NextToConstraint,
            "direct_left": DirectLeftConstraint,
            "left_of": LeftOfConstraint,
            "distance": DistanceConstraint,
            "same": SameConstraint,
        }

        constraints = []
        for clue, ctype, symbols, groups in parsed_clues:
            cls = factory.get(ctype, UnknownConstraint)
            constraints.append(cls(clue, symbols, groups))
        return constraints
    
    def proccess(self, puzzle_text):

        characteristics_text, clues = self.preprocess_puzzle(puzzle_text)

        attrs = self.extract_attributes(characteristics_text)

        parsed_clues = self.parse_puzzle_clues(attrs, clues)

        constraints = self.build_constraints(parsed_clues)

        return attrs, constraints

