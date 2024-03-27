import argparse
from typing import Set
from typing import List
from typing import Union
from typing import Tuple

# Clause -> Literal or Literal or ... or Literal
# Literal -> ~Atom | Atom
# Atom -> True | False | P | Q | ...

LINE_NUMBER = 1

class Literal:
    def __init__(self, atom: str, is_negative: bool):
        self.atom = atom
        self.is_negative = is_negative

    def get_negation(self):
        return Literal(atom=self.atom, is_negative=not self.is_negative)

    def __eq__(self, other):
        return type(self) == type(other) and self.atom == other.atom and self.is_negative == other.is_negative

    def __repr__(self) -> str:
        sign = '~' if self.is_negative else '' 
        return sign + self.atom 
    
    def __hash__(self) -> int:
        return hash(self.__repr__())

class Clause:
    def __init__(self):
        self.literals: List[Literal] = list()

    def get_negation(self) -> List[Literal]:
        return [literal.get_negation() for literal in self.literals]
    
    def __eq__(self, other) -> bool:
        return type(self) == type(other) and set(self.literals) == set(other.literals)

    def __repr__(self) -> str:
        result = ''
        for literal in self.literals:
            result += str(literal) + ' '
        return result

    def __hash__(self) -> int:
        return hash(self.__repr__())

class KnowledgeBase:
    def __init__(self, clauses: List[Clause]):
        self.clauses = clauses

        global LINE_NUMBER
        for clause in clauses:
            print(f'{LINE_NUMBER}. {clause}{{}}')
            LINE_NUMBER += 1
        
    def resolution_principle_algorithm(self, theorem: Clause) -> None:
        # 1 negate the theorm and add each literal to set of valid clauses
        for literal in theorem.get_negation():
            new_clause = Clause()
            new_clause.literals.append(literal)
            if not self.is_redundant_clause(new_clause):
                global LINE_NUMBER
                print(f'{LINE_NUMBER}. {new_clause}{{}}')
                LINE_NUMBER += 1
                self.clauses.append(new_clause)

        # 2 While there still exists resolutable clauses ...
        i = 0
        while i < len(self.clauses):
            j = 0
            while j < i:
                new_clause = self.attempt_resolution(self.clauses[i], self.clauses[j])

                if new_clause == True:
                    j += 1
                    continue

                if new_clause == False:
                    print(f'{LINE_NUMBER}. Contradiction {{{i+1},{j+1}}}')
                    print('valid')
                    return

                if not self.is_redundant_clause(new_clause):
                    print(f'{LINE_NUMBER}. {new_clause}{{{i+1}, {j+1}}}')
                    LINE_NUMBER += 1
                    self.clauses.append(new_clause)
                j += 1
            i += 1
        print('failure')
        return

    def is_redundant_clause(self, new_clause) -> bool:
        for clause in self.clauses:
            if new_clause == clause:
                return True
        return False
    
    def attempt_resolution(self, clause1: Clause, clause2: Clause) -> Union[bool | Clause]:
        # if the clauses contain a same literal return True
        # if the clauses contain an inverted pair can produce resolution
        invertedPairsCount = 0
        resolutionLiteral = None
        for lit1 in clause1.literals:
            for lit2 in clause2.literals:
                if lit1 == lit2:
                    return True
                if lit1.get_negation() == lit2:
                    resolutionLiteral = lit1

                    invertedPairsCount += 1
                    if invertedPairsCount > 1:
                        return True

        if invertedPairsCount == 0:
            return True
            
        if resolutionLiteral is None:
            return True

        if len(clause1.literals) == 1 and len(clause2.literals) == 1:
            return False
        
        resolution = Clause()
        s1 = set(clause1.literals)
        s2 = set(clause2.literals)
        s = set.union(s1, s2)
        s.remove(resolutionLiteral)
        s.remove(resolutionLiteral.get_negation())
            
        resolution.literals = list(s)
        return resolution

    # def attempt_resolution(self, clause1: Clause, clause2: Clause) -> Union[bool | Clause]:
    #     # my code is so fucking slow I need to do it the ugly way :(
    #     # hmmm let me try and optimize this code a bit
    #     skip = True
    #     for lit1 in clause1.literals:
    #         for lit2 in clause2.literals:
    #             if lit1.get_negation == lit2:
    #                 skip = False
    #                 break
    #         if skip == False:
    #             break

    #     if not skip:
    #         return True

    #     lit1_set = set(clause1.literals)
    #     lit2_set = set(clause2.literals)
    #     inv1_set = set(clause1.get_negation())
    #     inv2_set = set(clause2.get_negation())
    #     inv_pairs = set.intersection(inv1_set, lit2_set)

    #     ### new notes for optimization ###
    #     # if there is any same pair return true
    #     # if there is at least one pair with inverted literals then can perform resolution

    #     # if the size of the two things are 1 


    #     # non zero if resolution is possible
    #     # greater than one is always true
    #     if len(inv_pairs) == 0 or len(inv_pairs) > 1:
    #         return True

    #     if len(lit1_set) == 1 and len(lit2_set) == 1:
    #         return False

    #     s = set()
    #     resolution = Clause()
    #     for literal in clause1.literals:
    #         if literal not in inv2_set: 
    #             # resolution.literals.append(literal)
    #             s.add(literal)

    #     for literal in clause2.literals:
    #         if literal not in inv1_set: 
    #             # resolution.literals.append(literal)
    #             s.add(literal)
        
        
    #     resolution.literals = list(s)

    #     if len(resolution.literals) == 0:
    #         return True

    #     return resolution

def parse_KB(kb_path: str) -> Tuple[List[Clause], Clause]:
    clauses = list()
    theorem = Clause()

    with open(kb_path, 'r') as file:
        num_lines = len(file.readlines())

    with open(kb_path, 'r') as file:
        for lineNum, line in enumerate(file):
            clause = Clause()
            literals = line.strip().split()

            for chunk in literals:
              clause.literals.append(Literal(
                  atom=chunk if chunk[0] != '~' else chunk[1:],
                  is_negative=chunk[0] == '~'
              ))
            
            if lineNum == num_lines - 1:
                theorem = clause
            else:
                clauses.append(clause)

    return (clauses, theorem)

def main(kb_path: str) -> None:
    clauses, therom = parse_KB(kb_path)

    KB = KnowledgeBase(clauses)
    KB.resolution_principle_algorithm(therom)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Theorm prover")
    parser.add_argument("kb_path", help="Path to kb file")

    args = parser.parse_args()

    main(kb_path=args.kb_path)

