import pandas as pd
import re
from typing import List, Tuple, Set, Dict, Optional

class AttributeValue:
    """Represents a value with its source column information."""
    
    def __init__(self, value: str, column: str):
        self.value = value.lower()
        self.column = column.lower()
    
    def __eq__(self, other):
        if isinstance(other, AttributeValue):
            return self.value == other.value and self.column == other.column
        return False
    
    def __hash__(self):
        return hash((self.value, self.column))
    
    def __repr__(self):
        return f"AttributeValue({self.value!r}, {self.column!r})"
    
    def matches(self, value_str: str) -> bool:
        """Check if this value matches a string (case-insensitive)."""
        return self.value == value_str.lower()


class CPSConstraint:
    """Base class for all constraint types."""

    def __init__(self, clue, symbols, groups):
        self.clue = clue
        self.symbols = symbols or {}
        self.groups = groups or ()

    def _known_values(self, attr_values: Set[AttributeValue]) -> Set[AttributeValue]:
        """Return set of known AttributeValue objects."""
        return attr_values

    def _entity_positions(self, attr_value: AttributeValue, attrs_df) -> List[int]:
        """
        Return list of row indices where the entity appears in its specific column.
        
        Args:
            attr_value: AttributeValue object with value and column info
            attrs_df: The attributes DataFrame
        
        Returns:
            List of row indices where this value appears in its column
        """
        positions = []
        if attr_value.column not in attrs_df.columns:
            return positions
        
        col = attrs_df[attr_value.column]
        for idx, cell in col.items():
            if cell is not None and str(cell).lower() == attr_value.value:
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
        """Validate that entity exists in its specified column."""
        entities = self.symbols.get("entities", []) or []
        if not entities:
            return [], ["missing entity"]
        
        # entities is now a list of AttributeValue objects
        # Try each one until we find a valid position
        all_positions = []
        issues = []
        
        for attr_val in entities:
            positions = self._entity_positions(attr_val, attrs_df)
            if positions:
                all_positions.extend(positions)
            else:
                issues.append(f"unknown entity: {attr_val.value} (column: {attr_val.column})")
        
        if all_positions:
            return list(set(all_positions)), []
        return [], issues if issues else ["no valid entity found"]

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
        """Get positions for entity pairs with column awareness."""
        entities = self.symbols.get("entities", []) or []

        if len(entities) >= 2:
            entities_to_use = entities[:2]
        elif len(entities) == 1:
            # Duplicate the single entity if clue implies self-relation
            entities_to_use = [entities[0], entities[0]]
        elif len(getattr(self, "groups", ())) >= 2:
            # Fallback to groups (legacy support)
            return [], [], ["missing pair entities with column context"]
        else:
            return [], [], ["missing pair entities"]

        # entities are now AttributeValue objects
        a, b = entities_to_use[0], entities_to_use[1]
        
        pos_a = self._entity_positions(a, attrs_df)
        pos_b = self._entity_positions(b, attrs_df)
        issues = []
        
        if not pos_a:
            issues.append(f"unknown entity: {a.value} (column: {a.column})")
        if not pos_b:
            issues.append(f"unknown entity: {b.value} (column: {b.column})")
        
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

    def extract_attributes(self, characteristics_text) -> Tuple[pd.DataFrame, Set[AttributeValue]]:
        """
        Extract attribute columns from characteristics section.
        
        Returns:
            Tuple of (attributes_df, attr_values_set)
            - attributes_df: DataFrame with attribute columns
            - attr_values_set: Set of AttributeValue objects tracking (value, column) pairs
        """
        attributes = {}
        attr_values = set()
        
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
                    # Create AttributeValue objects for this column
                    for val in values:
                        attr_values.add(AttributeValue(val, attr_name))
        
        return pd.DataFrame(attributes), attr_values

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

    def extract_symbols(self, clue: str, attr_values: Set[AttributeValue]) -> Dict:
        """
        Extract entity references from a clue based on known attribute values.
        Matches both the value and its column.
        
        Args:
            clue: The normalized clue text
            attr_values: Set of AttributeValue objects tracking (value, column) pairs
        
        Returns:
            Dict with 'entities' (list of AttributeValue objects) and 'position' (int or None)
        """
        entities = []
        clue_lower = clue.lower()
        
        # Find all matching attribute values in the clue
        for attr_val in attr_values:
            if attr_val.value in clue_lower:
                entities.append(attr_val)
        
        # Extract position if present (first, second, third, etc.)
        position_map = {
            'first': 0, 'second': 1, 'third': 2, 'fourth': 3, 'fifth': 4,
            'sixth': 5, 'seventh': 6, 'eighth': 7, 'ninth': 8, 'tenth': 9
        }
        position = None
        for pos_word, pos_num in position_map.items():
            if pos_word in clue_lower:
                position = pos_num
                break
        
        return {'entities': entities, 'position': position}

    def parse_clue(self, clue: str, attr_values: Set[AttributeValue]) -> Tuple[str, Dict, Tuple]:
        """
        Parse a clue and identify its type and relevant symbols.
        
        Args:
            clue: The clue text
            attr_values: Set of AttributeValue objects tracking (value, column) pairs
        
        Returns:
            Tuple of (constraint_type, symbol_data, match_groups)
            symbol_data: Dict with 'entities' (list of AttributeValue objects) and 'position' (int or None)
        
        Raises:
            ValueError: If clue doesn't match any known pattern
        """
        clue = self.normalize(clue)
        
        # Try to match against each pattern type (order matters - check specific patterns first)
        for ctype, pattern in self.PATTERNS.items():
            match = pattern.search(clue)
            if match:
                symbols = self.extract_symbols(clue, attr_values)
                return ctype, symbols, match.groups()
        
        # If no pattern matched, raise an error
        raise ValueError(f"Unrecognized clue format: {clue}")

    def parse_puzzle_clues(self, attrs_df: pd.DataFrame, clues: List[str], attr_values: Set[AttributeValue]) -> List[Tuple]:
        """
        Parse all clues from the puzzle using the full pipeline.
        
        Args:
            attrs_df: The attributes DataFrame
            clues: List of clue strings
            attr_values: Set of AttributeValue objects
        
        Returns:
            List of tuples: (original_clue, constraint_type, symbols, match_groups)
        """
        parsed_clues = []
        
        for _, clue in enumerate(clues, 1):
            try:
                ctype, symbols, groups = self.parse_clue(clue, attr_values)
                parsed_clues.append((clue, ctype, symbols, groups))
            except ValueError as e:
                parsed_clues.append((clue, "UNKNOWN", {}, ()))
        
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
    
    def process(self, puzzle_text: str) -> Tuple[pd.DataFrame, List, Set[AttributeValue]]:
        """
        Process puzzle text and return attributes, constraints, and attribute values.
        
        Returns:
            Tuple of (attrs_df, constraints, attr_values)
        """
        characteristics_text, clues = self.preprocess_puzzle(puzzle_text)

        attrs, attr_values = self.extract_attributes(characteristics_text)

        parsed_clues = self.parse_puzzle_clues(attrs, clues, attr_values)

        constraints = self.build_constraints(parsed_clues)

        return attrs, constraints, attr_values

