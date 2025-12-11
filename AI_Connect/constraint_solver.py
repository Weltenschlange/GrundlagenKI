from typing import Dict, List, Tuple, Optional
from constraints import Constraint
import copy


class ConstraintSolver:
    """
    Smart Constraint Satisfaction Problem (CSP) solver for logic puzzles.
    
    Uses:
    - Constraint propagation (AC-3 like) for domain pruning
    - Backtracking search with Minimum Remaining Values (MRV) heuristic
    - Forward checking to reduce search space
    """
    
    def __init__(self, attributes: Dict[str, List[str]], constraints: List[Constraint]):
        """
        Initialize the constraint solver.
        
        Args:
            attributes: Dictionary mapping attribute keys to lists of possible values
                       e.g., {'name': ['alice', 'bob'], 'color': ['red', 'blue']}
            constraints: List of Constraint objects to satisfy
        """
        self.attributes = attributes
        self.constraints = constraints
        self.num_positions = len(next(iter(attributes.values())))
        
        # Initialize domains: {position: {attr_key: set(possible_values)}}
        self.domains = self._initialize_domains()
        
        # Track the current assignment: {position: {attr_key: value}}
        self.assignment = {}
        
        # Statistics
        self.backtrack_count = 0
        self.propagation_calls = 0
        
    def _initialize_domains(self) -> Dict[int, Dict[str, set]]:
        """Initialize each position with all possible values for each attribute."""
        domains = {}
        for pos in range(1, self.num_positions + 1):
            domains[pos] = {}
            for attr_key, attr_values in self.attributes.items():
                domains[pos][attr_key] = set(attr_values)
        return domains
    
    def solve(self) -> Optional[Dict[int, Dict[str, str]]]:
        """
        Solve the constraint satisfaction problem.
        
        Returns:
            Dictionary mapping positions to assignments if solution found, None otherwise
        """
        # Apply initial constraint propagation
        if not self._propagate():
            return None
        
        # Start backtracking search
        result = self._backtrack({})
        
        print(f"Backtrack count: {self.backtrack_count}")
        print(f"Propagation calls: {self.propagation_calls}")
        
        return result
    
    def _propagate(self) -> bool:
        """
        Apply constraint propagation to reduce domains.
        Enforces all-different constraint and constraint rules.
        
        Returns:
            False if inconsistency detected, True otherwise
        """
        self.propagation_calls += 1
        
        changed = True
        while changed:
            changed = False
            
            # 1. Apply all-different constraint: each value can only appear once per attribute
            for attr_key in self.attributes.keys():
                for value in self.attributes[attr_key]:
                    positions_with_value = []
                    for pos in range(1, self.num_positions + 1):
                        if value in self.domains[pos][attr_key]:
                            positions_with_value.append(pos)
                    
                    # If value can only go in one position, assign it there
                    if len(positions_with_value) == 1:
                        pos = positions_with_value[0]
                        if len(self.domains[pos][attr_key]) > 1:
                            self.domains[pos][attr_key] = {value}
                            changed = True
                    
                    # If value has nowhere to go, inconsistency
                    elif len(positions_with_value) == 0:
                        return False
            
            # 2. If position has only one value for an attribute, remove it from other positions
            for pos in range(1, self.num_positions + 1):
                for attr_key in self.attributes.keys():
                    if len(self.domains[pos][attr_key]) == 1:
                        value = list(self.domains[pos][attr_key])[0]
                        for other_pos in range(1, self.num_positions + 1):
                            if other_pos != pos and value in self.domains[other_pos][attr_key]:
                                self.domains[other_pos][attr_key].discard(value)
                                changed = True
                                if len(self.domains[other_pos][attr_key]) == 0:
                                    return False
            
            # 3. Apply unary constraints (constraints with single attributes)
            for pos in range(1, self.num_positions + 1):
                for attr_key in self.attributes.keys():
                    if len(self.domains[pos][attr_key]) == 0:
                        return False  # Empty domain = inconsistency
                    
                    # Remove values that would violate position-specific constraints
                    values_to_remove = set()
                    for value in self.domains[pos][attr_key]:
                        test_solution = self._build_partial_solution()
                        test_solution[pos][attr_key] = value
                        
                        if not self._is_consistent(test_solution):
                            values_to_remove.add(value)
                    
                    if values_to_remove:
                        self.domains[pos][attr_key] -= values_to_remove
                        changed = True
                        if len(self.domains[pos][attr_key]) == 0:
                            return False
            
            # 4. Apply binary constraint propagation (between positions)
            for pos1 in range(1, self.num_positions + 1):
                for pos2 in range(pos1 + 1, self.num_positions + 1):
                    for attr_key1 in self.attributes.keys():
                        for value1 in list(self.domains[pos1][attr_key1]):
                            # Check if this value can be paired with any value in pos2
                            has_support = False
                            for attr_key2 in self.attributes.keys():
                                for value2 in self.domains[pos2][attr_key2]:
                                    test_solution = self._build_partial_solution()
                                    test_solution[pos1][attr_key1] = value1
                                    test_solution[pos2][attr_key2] = value2
                                    
                                    if self._is_consistent(test_solution):
                                        has_support = True
                                        break
                                if has_support:
                                    break
                            
                            if not has_support:
                                self.domains[pos1][attr_key1].discard(value1)
                                changed = True
                                if len(self.domains[pos1][attr_key1]) == 0:
                                    return False
        
        return True
    
    def _backtrack(self, assignment: Dict[int, Dict[str, str]]) -> Optional[Dict[int, Dict[str, str]]]:
        """
        Backtracking search with MRV heuristic.
        
        Args:
            assignment: Current partial assignment
            
        Returns:
            Complete assignment if solution found, None otherwise
        """
        # Check if complete
        if self._is_complete(assignment):
            return assignment
        
        self.backtrack_count += 1
        
        # Select unassigned variable using MRV heuristic
        var = self._select_unassigned_variable(assignment)
        if var is None:
            return None
        
        pos, attr_key = var
        
        # Try values in order of least constraining value heuristic
        for value in self._order_domain_values(pos, attr_key, assignment):
            # Create new assignment
            new_assignment = copy.deepcopy(assignment)
            if pos not in new_assignment:
                new_assignment[pos] = {}
            new_assignment[pos][attr_key] = value
            
            # Check if consistent
            if self._is_consistent(new_assignment):
                # Save current domains
                saved_domains = copy.deepcopy(self.domains)
                
                # Perform forward checking
                self.domains[pos][attr_key] = {value}
                
                # Apply propagation with reduced domains
                if self._propagate():
                    result = self._backtrack(new_assignment)
                    if result is not None:
                        return result
                
                # Restore domains
                self.domains = saved_domains
        
        return None
    
    def _is_complete(self, assignment: Dict[int, Dict[str, str]]) -> bool:
        """Check if assignment is complete (all positions have all attributes assigned)."""
        if len(assignment) != self.num_positions:
            return False
        
        for pos in range(1, self.num_positions + 1):
            if pos not in assignment:
                return False
            if len(assignment[pos]) != len(self.attributes):
                return False
        
        return True
    
    def _is_consistent(self, assignment: Dict[int, Dict[str, str]]) -> bool:
        """Check if assignment satisfies all constraints and uniqueness constraints."""
        # Check global constraints: each value must be used at most once per attribute
        for attr_key in self.attributes.keys():
            used_values = []
            for pos in range(1, self.num_positions + 1):
                if pos in assignment and attr_key in assignment[pos]:
                    value = assignment[pos][attr_key]
                    if value in used_values:
                        return False  # Value used more than once
                    used_values.append(value)
        
        # Check all constraint-specific rules
        for constraint in self.constraints:
            if not constraint.is_valid(assignment):
                return False
        
        return True
    
    def _select_unassigned_variable(self, assignment: Dict[int, Dict[str, str]]) -> Optional[Tuple[int, str]]:
        """
        Select unassigned variable using MRV (Minimum Remaining Values) heuristic.
        
        Returns:
            (position, attribute_key) with smallest domain, or None if all assigned
        """
        min_domain_size = float('inf')
        best_var = None
        
        for pos in range(1, self.num_positions + 1):
            for attr_key in self.attributes.keys():
                # Skip if already assigned
                if pos in assignment and attr_key in assignment[pos]:
                    continue
                
                domain_size = len(self.domains[pos][attr_key])
                if domain_size == 0:
                    return (pos, attr_key)  # Empty domain = failure
                
                if domain_size < min_domain_size:
                    min_domain_size = domain_size
                    best_var = (pos, attr_key)
        
        return best_var
    
    def _order_domain_values(self, pos: int, attr_key: str, assignment: Dict[int, Dict[str, str]]) -> List[str]:
        """
        Order domain values using Least Constraining Value heuristic.
        
        Returns values that rule out fewer choices for neighboring variables.
        """
        # For simplicity, return in order of current domain
        # Can be enhanced to count conflicts
        return list(self.domains[pos][attr_key])
    
    def _build_partial_solution(self) -> Dict[int, Dict[str, str]]:
        """Build a partial solution from assignment and domains with single values."""
        solution = copy.deepcopy(self.assignment)
        
        for pos in range(1, self.num_positions + 1):
            if pos not in solution:
                solution[pos] = {}
            
            for attr_key in self.attributes.keys():
                # If domain has single value, assign it
                if len(self.domains[pos][attr_key]) == 1:
                    value = list(self.domains[pos][attr_key])[0]
                    if attr_key not in solution[pos]:
                        solution[pos][attr_key] = value
        
        return solution
    
    def print_solution(self, solution: Dict[int, Dict[str, str]]) -> None:
        """Pretty print the solution."""
        if solution is None:
            print("No solution found.")
            return
        
        print("\n=== Solution ===")
        for pos in sorted(solution.keys()):
            print(f"\nPosition {pos}:")
            for attr_key, value in sorted(solution[pos].items()):
                print(f"  {attr_key}: {value}")
    
    def print_domains(self) -> None:
        """Print current domains for debugging."""
        print("\n=== Current Domains ===")
        for pos in sorted(self.domains.keys()):
            print(f"\nPosition {pos}:")
            for attr_key, values in sorted(self.domains[pos].items()):
                print(f"  {attr_key}: {values}")
