import pandas as pd
from preProccesPuzzle import PreProcess
from clue_classifier import ClueClassifier
from constraints import Constraint, IdentityConstrain, NextToConstrain, DistanceConstrain, RightConstrain, LeftConstrain, DirectRightConstrain, DirectLeftConstrain, PositionAbsoluteConstrain, PositionAbsoluteNegativeConstrain
from constraint_solver import ConstraintSolver
from concurrent.futures import ProcessPoolExecutor


def constraint_factory(attrs, clues):
    constrains: list[Constraint] = []
    classifier = ClueClassifier()
    for c in clues:
        clue, clue_type = classifier.classify(c)

        if clue_type == "IDENTITY":
            constrains.append(IdentityConstrain(attrs, clue))
        if clue_type == "NEXT_TO":
            constrains.append(NextToConstrain(attrs, clue))
        if clue_type == "LEFT":
            constrains.append(LeftConstrain(attrs, clue))
        if clue_type == "RIGHT":
            constrains.append(RightConstrain(attrs, clue))
        if clue_type == "DISTANCE":
            constrains.append(DistanceConstrain(attrs, clue))
        if clue_type == "DIRECT_LEFT":
            constrains.append(DirectLeftConstrain(attrs, clue))
        if clue_type == "DIRECT_RIGHT":
            constrains.append(DirectRightConstrain(attrs, clue))
        if clue_type == "POSITION_ABSOLUTE":
            constrains.append(PositionAbsoluteConstrain(attrs, clue))
        if clue_type == "POSITION_ABSOLUTE_NEGATIVE":
            constrains.append(PositionAbsoluteNegativeConstrain(attrs, clue))
        if clue_type == "UNKNOWN":
            raise TypeError
    
    return constrains


def solve_puzzle(idx, puzzle_text):
    ppp = PreProcess()
    attrs, clues = ppp.proccess(puzzle_text)
    constrains = constraint_factory(attrs, clues)
    Cs = ConstraintSolver(attrs, constrains)
    solution = Cs.solve()
    return idx, solution


def main():
    gridmode = pd.read_parquet("Gridmode-00000-of-00001.parquet")
    
    total_puzzles = len(gridmode)
    puzzles = [(idx, gridmode.puzzle.iloc[idx].lower()) for idx in range(total_puzzles)]
    
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(solve_puzzle, idx, puzzle_text) 
                   for idx, puzzle_text in puzzles]
        
        for completed_idx, future in enumerate(futures):
            print(f"Progress: {completed_idx + 1}/{total_puzzles}", end='\r')
            try:
                puzzle_idx, solution = future.result()
                if solution is None:
                    print(f"No solution found for puzzle at index {puzzle_idx}")
            except Exception as e:
                print(f"Error at puzzle {completed_idx}: {e}")


if __name__ == "__main__":
    main()
