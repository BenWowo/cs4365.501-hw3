import argparse
from typing import List
from typing import Union
from typing import Tuple

# Clause -> Literal or Literal or ... or Literal
# Literal -> ~Atom | Atom
# Atom -> True | False | P | Q | ...

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
        return ''.join([str(literal) + ' ' for literal in self.literals])

    def __hash__(self) -> int:
        # My hash needs to be the same for things that contain same literals...
        return hash(frozenset(self.literals))

class KnowledgeBase:
    def __init__(self, clauses: List[Clause]) -> None:
        self.clauses = clauses
        self.clause_set = set(clauses)
        self.LINE_NUMBER = 1

        for clause in clauses:
            print(f'{self.LINE_NUMBER}. {clause}{{}}')
            self.LINE_NUMBER += 1
        
    def resolution_principle_algorithm(self, theorem: Clause) -> None:
        for literal in theorem.get_negation():
            new_clause = Clause()
            new_clause.literals.append(literal)
            if not self.is_redundant_clause(new_clause):
                print(f'{self.LINE_NUMBER}. {new_clause}{{}}')
                self.LINE_NUMBER += 1
                self.clauses.append(new_clause)
                self.clause_set.add(new_clause)

        i = 0
        while i < len(self.clauses):
            j = 0
            while j < i:
                new_clause = self.attempt_resolution(self.clauses[i], self.clauses[j])
                if new_clause == False:
                    print(f'{self.LINE_NUMBER}. Contradiction {{{i+1}, {j+1}}}')
                    print('Valid', end='')
                    return
                elif not self.is_redundant_clause(new_clause):
                    print(f'{self.LINE_NUMBER}. {new_clause}{{{i+1}, {j+1}}}')
                    self.LINE_NUMBER += 1
                    self.clauses.append(new_clause)
                    self.clause_set.add(new_clause)
                j += 1
            i += 1
        print('Fail', end='')
        return

    def is_redundant_clause(self, new_clause: Clause) -> bool:
        if new_clause == False:
            return False

        if new_clause == None or new_clause == True:
            return True

        return new_clause in self.clause_set
    
    def attempt_resolution(self, clause1: Clause, clause2: Clause) -> Union[Clause, bool, None]:
        resolutionAtom = None
        invertedPairs = 0
        for lit1 in clause1.literals:
            for lit2 in clause2.literals:
                if lit1.atom == lit2.atom and lit1.get_negation() == lit2:
                    invertedPairs += 1
                    resolutionAtom = lit1.atom
        
        if invertedPairs == 0:
            return None
        if invertedPairs > 1:
            return True
        if len(clause1.literals) == 1 and len(clause2.literals) == 1:
            return False
        
        resolution_set = set()
        resolution = Clause()
        for lit1 in clause1.literals:
            if lit1.atom != resolutionAtom and lit1 not in resolution_set:
                resolution.literals.append(lit1)
                resolution_set.add(lit1)

        for lit2 in clause2.literals:
            if lit2.atom != resolutionAtom and lit2 not in resolution_set:
                resolution.literals.append(lit2)
                resolution_set.add(lit2)

        return resolution

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
    clauses, theorem = parse_KB(kb_path)

    KB = KnowledgeBase(clauses)
    KB.resolution_principle_algorithm(theorem)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Theorm prover")
    parser.add_argument("kb_path", help="Path to kb file")

    args = parser.parse_args()

    main(kb_path=args.kb_path)

