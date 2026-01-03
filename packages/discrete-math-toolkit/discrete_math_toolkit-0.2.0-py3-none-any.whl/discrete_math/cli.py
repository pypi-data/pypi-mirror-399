"""
Discrete Math Toolkit CLI
=========================

Command-line interface for discrete mathematics operations.
Allows non-technical users to easily access all library functions.
"""

import argparse
import sys
import json
import ast
from typing import Any, Set, Tuple, Dict, List

# Import all modules
from . import (
    combinatorics,
    number_theory,
    logic,
    sets as sets_module,
    relations,
    functions,
    graphs
)


def parse_set(s: str) -> Set:
    """Parse a string representation of a set."""
    try:
        # Try parsing as Python set syntax
        parsed = ast.literal_eval(s)
        if isinstance(parsed, (set, list, tuple)):
            return set(parsed)
        return {parsed}
    except:
        # Try splitting by comma
        if ',' in s:
            items = [item.strip() for item in s.split(',')]
            try:
                return {ast.literal_eval(item) for item in items}
            except:
                return set(items)
        return {s}


def parse_relation(s: str) -> Set[Tuple]:
    """Parse a string representation of a relation."""
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, set):
            return parsed
        if isinstance(parsed, list):
            return set(tuple(item) if isinstance(item, list) else item for item in parsed)
        return set()
    except:
        return set()


def parse_list(s: str) -> List:
    """Parse a string representation of a list."""
    try:
        parsed = ast.literal_eval(s)
        if isinstance(parsed, (list, tuple)):
            return list(parsed)
        return [parsed]
    except:
        if ',' in s:
            items = [item.strip() for item in s.split(',')]
            try:
                return [ast.literal_eval(item) for item in items]
            except:
                return items
        return [s]


def parse_dict(s: str) -> Dict:
    """Parse a string representation of a dictionary."""
    try:
        return ast.literal_eval(s)
    except:
        return {}


def format_output(result: Any) -> str:
    """Format the output for display."""
    if isinstance(result, set):
        if not result:
            return "{}"
        if isinstance(next(iter(result)), frozenset):
            return "{\n  " + ",\n  ".join(str(sorted(list(s))) for s in sorted(result, key=lambda x: (len(x), sorted(list(x)) if x else []))) + "\n}"
        try:
            return str(sorted(list(result)))
        except:
            return str(result)
    elif isinstance(result, list) and result and isinstance(result[0], list):
        return "\n".join(str(row) for row in result)
    elif isinstance(result, dict):
        return json.dumps(result, indent=2, default=str)
    elif isinstance(result, tuple):
        return str(result)
    return str(result)


def format_truth_table(table: List[Dict]) -> str:
    """Format truth table for display."""
    if not table:
        return "Empty truth table"
    
    # Get column headers
    headers = list(table[0].keys())
    
    # Calculate column widths
    widths = {h: max(len(h), max(len(str(row[h])) for row in table)) for h in headers}
    
    # Build table
    lines = []
    header_line = " | ".join(h.center(widths[h]) for h in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    for row in table:
        line = " | ".join(str(row[h]).center(widths[h]) for h in headers)
        lines.append(line)
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Discrete Math Toolkit - Mathematical operations from the command line',
        epilog='For detailed help on a function: dmath <function-name> --help\nSee CLI_GUIDE.md for complete documentation.'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available functions')
    
    # ============================================================
    # COMBINATORICS FUNCTIONS
    # ============================================================
    
    # factorial
    p = subparsers.add_parser('factorial', help='Calculate factorial of n (n!)')
    p.add_argument('n', type=int, help='Non-negative integer')
    
    # permutations
    p = subparsers.add_parser('permutations', help='Calculate permutations P(n,r)')
    p.add_argument('n', type=int, help='Total number of items')
    p.add_argument('r', type=int, nargs='?', default=None, help='Number of items to arrange (default: n)')
    
    # combinations
    p = subparsers.add_parser('combinations', help='Calculate combinations C(n,r)')
    p.add_argument('n', type=int, help='Total number of items')
    p.add_argument('r', type=int, help='Number of items to choose')
    
    # binomial_coefficient
    p = subparsers.add_parser('binomial', help='Calculate binomial coefficient C(n,k)')
    p.add_argument('n', type=int, help='Total number')
    p.add_argument('k', type=int, help='Selection number')
    
    # permutations_with_repetition
    p = subparsers.add_parser('perm-rep', help='Calculate permutations with repetition (n^r)')
    p.add_argument('n', type=int, help='Number of distinct items')
    p.add_argument('r', type=int, help='Number of positions')
    
    # combinations_with_repetition
    p = subparsers.add_parser('comb-rep', help='Calculate combinations with repetition')
    p.add_argument('n', type=int, help='Number of distinct items')
    p.add_argument('r', type=int, help='Number of selections')
    
    # pascals_triangle
    p = subparsers.add_parser('pascal', help='Generate Pascal\'s triangle')
    p.add_argument('n', type=int, help='Number of rows')
    
    # catalan_number
    p = subparsers.add_parser('catalan', help='Calculate nth Catalan number')
    p.add_argument('n', type=int, help='Index (non-negative)')
    
    # stirling_second_kind
    p = subparsers.add_parser('stirling', help='Calculate Stirling number of second kind S(n,k)')
    p.add_argument('n', type=int, help='Number of elements')
    p.add_argument('k', type=int, help='Number of partitions')
    
    # bell_number
    p = subparsers.add_parser('bell', help='Calculate nth Bell number')
    p.add_argument('n', type=int, help='Index (non-negative)')
    
    # derangements
    p = subparsers.add_parser('derangements', help='Calculate number of derangements')
    p.add_argument('n', type=int, help='Number of elements')
    
    # multinomial_coefficient
    p = subparsers.add_parser('multinomial', help='Calculate multinomial coefficient')
    p.add_argument('values', type=int, nargs='+', help='Values k1, k2, ..., km')
    
    # fibonacci
    p = subparsers.add_parser('fibonacci', help='Calculate nth Fibonacci number')
    p.add_argument('n', type=int, help='Index (non-negative)')
    
    # generate_permutations
    p = subparsers.add_parser('gen-perms', help='Generate all permutations of items')
    p.add_argument('items', type=str, help='List of items (e.g., "[1,2,3]")')
    p.add_argument('r', type=int, nargs='?', default=None, help='Length of permutations (default: all)')
    
    # generate_combinations
    p = subparsers.add_parser('gen-combs', help='Generate all combinations of items')
    p.add_argument('items', type=str, help='List of items (e.g., "[1,2,3]")')
    p.add_argument('r', type=int, help='Number of items to choose')
    
    # generate_combinations_with_repetition
    p = subparsers.add_parser('gen-combs-rep', help='Generate combinations with repetition')
    p.add_argument('items', type=str, help='List of items (e.g., "[1,2,3]")')
    p.add_argument('r', type=int, help='Number of items to choose')
    
    # ============================================================
    # NUMBER THEORY FUNCTIONS
    # ============================================================
    
    # gcd
    p = subparsers.add_parser('gcd', help='Calculate greatest common divisor')
    p.add_argument('a', type=int, help='First integer')
    p.add_argument('b', type=int, help='Second integer')
    
    # lcm
    p = subparsers.add_parser('lcm', help='Calculate least common multiple')
    p.add_argument('a', type=int, help='First integer')
    p.add_argument('b', type=int, help='Second integer')
    
    # extended_gcd
    p = subparsers.add_parser('extended-gcd', help='Extended Euclidean algorithm (returns gcd, x, y)')
    p.add_argument('a', type=int, help='First integer')
    p.add_argument('b', type=int, help='Second integer')
    
    # is_prime
    p = subparsers.add_parser('is-prime', help='Check if number is prime')
    p.add_argument('n', type=int, help='Integer to check')
    
    # prime_factorization
    p = subparsers.add_parser('prime-factors', help='Find prime factorization')
    p.add_argument('n', type=int, help='Integer to factorize')
    
    # sieve_of_eratosthenes
    p = subparsers.add_parser('primes-upto', help='Find all primes up to n (Sieve of Eratosthenes)')
    p.add_argument('n', type=int, help='Upper limit')
    
    # mod_inverse
    p = subparsers.add_parser('mod-inverse', help='Calculate modular multiplicative inverse')
    p.add_argument('a', type=int, help='Number')
    p.add_argument('m', type=int, help='Modulus')
    
    # mod_exp
    p = subparsers.add_parser('mod-exp', help='Calculate modular exponentiation (base^exp mod m)')
    p.add_argument('base', type=int, help='Base')
    p.add_argument('exp', type=int, help='Exponent')
    p.add_argument('mod', type=int, help='Modulus')
    
    # euler_totient
    p = subparsers.add_parser('euler-phi', help='Calculate Euler\'s totient function φ(n)')
    p.add_argument('n', type=int, help='Integer')
    
    # chinese_remainder_theorem
    p = subparsers.add_parser('crt', help='Solve system using Chinese Remainder Theorem')
    p.add_argument('remainders', type=str, help='List of remainders (e.g., "[2,3,2]")')
    p.add_argument('moduli', type=str, help='List of moduli (e.g., "[3,5,7]")')
    
    # is_coprime
    p = subparsers.add_parser('is-coprime', help='Check if two numbers are coprime')
    p.add_argument('a', type=int, help='First integer')
    p.add_argument('b', type=int, help='Second integer')
    
    # divisors
    p = subparsers.add_parser('divisors', help='Find all divisors of n')
    p.add_argument('n', type=int, help='Integer')
    
    # sum_of_divisors
    p = subparsers.add_parser('sum-divisors', help='Calculate sum of divisors')
    p.add_argument('n', type=int, help='Integer')
    
    # is_perfect_number
    p = subparsers.add_parser('is-perfect', help='Check if number is perfect')
    p.add_argument('n', type=int, help='Integer to check')
    
    # ============================================================
    # LOGIC FUNCTIONS
    # ============================================================
    
    # generate_truth_table
    p = subparsers.add_parser('truth-table', help='Generate truth table for expression')
    p.add_argument('expression', type=str, help='Logical expression (e.g., "p AND q")')
    
    # is_tautology
    p = subparsers.add_parser('is-tautology', help='Check if expression is a tautology (always true)')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # is_contradiction
    p = subparsers.add_parser('is-contradiction', help='Check if expression is a contradiction (always false)')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # is_contingency
    p = subparsers.add_parser('is-contingency', help='Check if expression is contingent')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # convert_to_cnf
    p = subparsers.add_parser('to-cnf', help='Convert to Conjunctive Normal Form')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # convert_to_dnf
    p = subparsers.add_parser('to-dnf', help='Convert to Disjunctive Normal Form')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # are_equivalent
    p = subparsers.add_parser('logic-equiv', help='Check if two expressions are logically equivalent')
    p.add_argument('expr1', type=str, help='First expression')
    p.add_argument('expr2', type=str, help='Second expression')
    
    # simplify
    p = subparsers.add_parser('simplify-logic', help='Simplify logical expression')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # evaluate
    p = subparsers.add_parser('eval-logic', help='Evaluate logical expression with given values')
    p.add_argument('expression', type=str, help='Logical expression')
    p.add_argument('values', type=str, help='Variable values as dict (e.g., \'{"p": true, "q": false}\')')
    
    # get_minterms
    p = subparsers.add_parser('minterms', help='Get minterms (rows where expression is True)')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # get_maxterms
    p = subparsers.add_parser('maxterms', help='Get maxterms (rows where expression is False)')
    p.add_argument('expression', type=str, help='Logical expression')
    
    # ============================================================
    # SET THEORY FUNCTIONS
    # ============================================================
    
    # union
    p = subparsers.add_parser('set-union', help='Calculate union of sets')
    p.add_argument('sets', type=str, nargs='+', help='Sets (e.g., "{1,2,3}" "{3,4,5}")')
    
    # intersection
    p = subparsers.add_parser('set-intersect', help='Calculate intersection of sets')
    p.add_argument('sets', type=str, nargs='+', help='Sets')
    
    # difference
    p = subparsers.add_parser('set-diff', help='Calculate set difference A - B')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # symmetric_difference
    p = subparsers.add_parser('set-sym-diff', help='Calculate symmetric difference A △ B')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # complement
    p = subparsers.add_parser('set-complement', help='Calculate set complement')
    p.add_argument('set_a', type=str, help='Set to complement')
    p.add_argument('universal', type=str, help='Universal set')
    
    # power_set
    p = subparsers.add_parser('power-set', help='Generate power set (all subsets)')
    p.add_argument('set_input', type=str, help='Input set')
    
    # cartesian_product
    p = subparsers.add_parser('cartesian', help='Calculate Cartesian product A × B')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # cartesian_product_n
    p = subparsers.add_parser('cartesian-n', help='Calculate Cartesian product of n sets')
    p.add_argument('sets', type=str, nargs='+', help='Sets')
    
    # is_subset
    p = subparsers.add_parser('is-subset', help='Check if A ⊆ B')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # is_proper_subset
    p = subparsers.add_parser('is-proper-subset', help='Check if A ⊂ B (proper subset)')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # is_superset
    p = subparsers.add_parser('is-superset', help='Check if A ⊇ B')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # is_disjoint
    p = subparsers.add_parser('is-disjoint', help='Check if sets are disjoint (no common elements)')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # cardinality
    p = subparsers.add_parser('cardinality', help='Calculate set cardinality (size)')
    p.add_argument('set_input', type=str, help='Input set')
    
    # partition
    p = subparsers.add_parser('is-partition', help='Check if subsets form a partition of a set')
    p.add_argument('set_s', type=str, help='The set to partition')
    p.add_argument('subsets', type=str, nargs='+', help='Subsets')
    
    # are_equal
    p = subparsers.add_parser('sets-equal', help='Check if two sets are equal')
    p.add_argument('set_a', type=str, help='First set')
    p.add_argument('set_b', type=str, help='Second set')
    
    # power_set_cardinality
    p = subparsers.add_parser('power-set-size', help='Calculate power set cardinality (2^|S|)')
    p.add_argument('set_input', type=str, help='Input set')
    
    # ============================================================
    # RELATIONS FUNCTIONS
    # ============================================================
    
    # is_reflexive
    p = subparsers.add_parser('is-reflexive', help='Check if relation is reflexive')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # is_symmetric
    p = subparsers.add_parser('is-symmetric', help='Check if relation is symmetric')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # is_antisymmetric
    p = subparsers.add_parser('is-antisymmetric', help='Check if relation is antisymmetric')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # is_transitive
    p = subparsers.add_parser('is-transitive', help='Check if relation is transitive')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # is_equivalence_relation
    p = subparsers.add_parser('is-equivalence', help='Check if relation is equivalence relation')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # is_partial_order
    p = subparsers.add_parser('is-partial-order', help='Check if relation is partial order')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # reflexive_closure
    p = subparsers.add_parser('reflexive-closure', help='Calculate reflexive closure')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # symmetric_closure
    p = subparsers.add_parser('symmetric-closure', help='Calculate symmetric closure')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # transitive_closure
    p = subparsers.add_parser('transitive-closure', help='Calculate transitive closure')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # equivalence_classes
    p = subparsers.add_parser('equiv-classes', help='Compute equivalence classes')
    p.add_argument('relation', type=str, help='Equivalence relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # compose
    p = subparsers.add_parser('compose-rel', help='Compose two relations R1 ∘ R2')
    p.add_argument('relation1', type=str, help='First relation')
    p.add_argument('relation2', type=str, help='Second relation')
    
    # inverse_relation
    p = subparsers.add_parser('inverse-rel', help='Compute inverse of relation')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # get_domain (relations)
    p = subparsers.add_parser('rel-domain', help='Get domain of relation')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # get_range (relations)
    p = subparsers.add_parser('rel-range', help='Get range of relation')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    
    # relation_matrix
    p = subparsers.add_parser('rel-matrix', help='Convert relation to matrix representation')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # ============================================================
    # FUNCTION THEORY
    # ============================================================
    
    # is_function
    p = subparsers.add_parser('is-function', help='Check if relation is a function')
    p.add_argument('relation', type=str, help='Relation as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    
    # is_injective
    p = subparsers.add_parser('is-injective', help='Check if function is injective (one-to-one)')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    
    # is_surjective
    p = subparsers.add_parser('is-surjective', help='Check if function is surjective (onto)')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    p.add_argument('codomain', type=str, help='Codomain set')
    
    # is_bijective
    p = subparsers.add_parser('is-bijective', help='Check if function is bijective')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    p.add_argument('codomain', type=str, help='Codomain set')
    
    # compose_functions
    p = subparsers.add_parser('compose-func', help='Compose two functions f ∘ g')
    p.add_argument('f', type=str, help='First function')
    p.add_argument('g', type=str, help='Second function')
    
    # inverse_function
    p = subparsers.add_parser('inverse-func', help='Find inverse of bijective function')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    p.add_argument('domain', type=str, help='Domain set')
    p.add_argument('codomain', type=str, help='Codomain set')
    
    # get_domain (functions)
    p = subparsers.add_parser('func-domain', help='Get domain of function')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    
    # get_range (functions)
    p = subparsers.add_parser('func-range', help='Get range of function')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    
    # function_to_dict
    p = subparsers.add_parser('func-to-dict', help='Convert function to dictionary')
    p.add_argument('relation', type=str, help='Function as set of tuples')
    
    # ============================================================
    # GRAPH FUNCTIONS
    # ============================================================
    
    # create_complete_graph
    p = subparsers.add_parser('complete-graph', help='Create complete graph K_n')
    p.add_argument('n', type=int, help='Number of vertices')
    
    # create_cycle_graph
    p = subparsers.add_parser('cycle-graph', help='Create cycle graph C_n')
    p.add_argument('n', type=int, help='Number of vertices')
    
    # create_path_graph
    p = subparsers.add_parser('path-graph', help='Create path graph P_n')
    p.add_argument('n', type=int, help='Number of vertices')
    
    # Graph operations via edges
    p = subparsers.add_parser('graph-bfs', help='Perform BFS traversal')
    p.add_argument('edges', type=str, help='Edges as list of tuples (e.g., "[(0,1),(1,2)]")')
    p.add_argument('start', type=int, help='Starting vertex')
    p.add_argument('--directed', action='store_true', help='Create directed graph')
    
    p = subparsers.add_parser('graph-dfs', help='Perform DFS traversal')
    p.add_argument('edges', type=str, help='Edges as list of tuples')
    p.add_argument('start', type=int, help='Starting vertex')
    p.add_argument('--directed', action='store_true', help='Create directed graph')
    
    p = subparsers.add_parser('graph-connected', help='Check if graph is connected')
    p.add_argument('edges', type=str, help='Edges as list of tuples')
    p.add_argument('--directed', action='store_true', help='Create directed graph')
    
    p = subparsers.add_parser('graph-cycle', help='Check if graph has cycle')
    p.add_argument('edges', type=str, help='Edges as list of tuples')
    p.add_argument('--directed', action='store_true', help='Create directed graph')
    
    p = subparsers.add_parser('graph-bipartite', help='Check if graph is bipartite')
    p.add_argument('edges', type=str, help='Edges as list of tuples')
    
    p = subparsers.add_parser('graph-shortest-path', help='Find shortest path between vertices')
    p.add_argument('edges', type=str, help='Edges as list of tuples')
    p.add_argument('start', type=int, help='Starting vertex')
    p.add_argument('end', type=int, help='Ending vertex')
    p.add_argument('--directed', action='store_true', help='Create directed graph')
    
    p = subparsers.add_parser('graph-topo-sort', help='Topological sort (DAG only)')
    p.add_argument('edges', type=str, help='Edges as list of tuples')
    
    # ============================================================
    # LIST ALL FUNCTIONS
    # ============================================================
    p = subparsers.add_parser('list', help='List all available functions')
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    try:
        # Execute the requested function
        result = None
        
        # LIST ALL FUNCTIONS
        if args.command == 'list':
            print("""
╔══════════════════════════════════════════════════════════════════╗
║           DISCRETE MATH TOOLKIT - AVAILABLE FUNCTIONS            ║
╚══════════════════════════════════════════════════════════════════╝

📊 COMBINATORICS (16 functions):
   factorial, permutations, combinations, binomial, perm-rep, 
   comb-rep, pascal, catalan, stirling, bell, derangements,
   multinomial, fibonacci, gen-perms, gen-combs, gen-combs-rep

🔢 NUMBER THEORY (14 functions):
   gcd, lcm, extended-gcd, is-prime, prime-factors, primes-upto,
   mod-inverse, mod-exp, euler-phi, crt, is-coprime, divisors,
   sum-divisors, is-perfect

🧠 LOGIC (11 functions):
   truth-table, is-tautology, is-contradiction, is-contingency,
   to-cnf, to-dnf, logic-equiv, simplify-logic, eval-logic,
   minterms, maxterms

📦 SETS (17 functions):
   set-union, set-intersect, set-diff, set-sym-diff, set-complement,
   power-set, cartesian, cartesian-n, is-subset, is-proper-subset,
   is-superset, is-disjoint, cardinality, is-partition, sets-equal,
   power-set-size

🔗 RELATIONS (15 functions):
   is-reflexive, is-symmetric, is-antisymmetric, is-transitive,
   is-equivalence, is-partial-order, reflexive-closure,
   symmetric-closure, transitive-closure, equiv-classes,
   compose-rel, inverse-rel, rel-domain, rel-range, rel-matrix

🎯 FUNCTIONS (9 functions):
   is-function, is-injective, is-surjective, is-bijective,
   compose-func, inverse-func, func-domain, func-range, func-to-dict

📈 GRAPHS (10 functions):
   complete-graph, cycle-graph, path-graph, graph-bfs, graph-dfs,
   graph-connected, graph-cycle, graph-bipartite, graph-shortest-path,
   graph-topo-sort

──────────────────────────────────────────────────────────────────
TOTAL: 92 functions available via CLI

Use 'dmath <function-name> --help' for help on a specific function.
See CLI_GUIDE.md for complete documentation with examples.
""")
            return
        
        # COMBINATORICS
        if args.command == 'factorial':
            result = combinatorics.factorial(args.n)
        elif args.command == 'permutations':
            result = combinatorics.permutations(args.n, args.r)
        elif args.command == 'combinations':
            result = combinatorics.combinations(args.n, args.r)
        elif args.command == 'binomial':
            result = combinatorics.binomial_coefficient(args.n, args.k)
        elif args.command == 'perm-rep':
            result = combinatorics.permutations_with_repetition(args.n, args.r)
        elif args.command == 'comb-rep':
            result = combinatorics.combinations_with_repetition(args.n, args.r)
        elif args.command == 'pascal':
            result = combinatorics.pascals_triangle(args.n)
        elif args.command == 'catalan':
            result = combinatorics.catalan_number(args.n)
        elif args.command == 'stirling':
            result = combinatorics.stirling_second_kind(args.n, args.k)
        elif args.command == 'bell':
            result = combinatorics.bell_number(args.n)
        elif args.command == 'derangements':
            result = combinatorics.derangements(args.n)
        elif args.command == 'multinomial':
            result = combinatorics.multinomial_coefficient(*args.values)
        elif args.command == 'fibonacci':
            result = combinatorics.fibonacci(args.n)
        elif args.command == 'gen-perms':
            items = parse_list(args.items)
            result = list(combinatorics.generate_permutations(items, args.r))
        elif args.command == 'gen-combs':
            items = parse_list(args.items)
            result = list(combinatorics.generate_combinations(items, args.r))
        elif args.command == 'gen-combs-rep':
            items = parse_list(args.items)
            result = list(combinatorics.generate_combinations_with_repetition(items, args.r))
        
        # NUMBER THEORY
        elif args.command == 'gcd':
            result = number_theory.gcd(args.a, args.b)
        elif args.command == 'lcm':
            result = number_theory.lcm(args.a, args.b)
        elif args.command == 'extended-gcd':
            result = number_theory.extended_gcd(args.a, args.b)
        elif args.command == 'is-prime':
            result = number_theory.is_prime(args.n)
        elif args.command == 'prime-factors':
            result = number_theory.prime_factorization(args.n)
        elif args.command == 'primes-upto':
            result = number_theory.sieve_of_eratosthenes(args.n)
        elif args.command == 'mod-inverse':
            result = number_theory.mod_inverse(args.a, args.m)
        elif args.command == 'mod-exp':
            result = number_theory.mod_exp(args.base, args.exp, args.mod)
        elif args.command == 'euler-phi':
            result = number_theory.euler_totient(args.n)
        elif args.command == 'crt':
            remainders = parse_list(args.remainders)
            moduli = parse_list(args.moduli)
            result = number_theory.chinese_remainder_theorem(remainders, moduli)
        elif args.command == 'is-coprime':
            result = number_theory.is_coprime(args.a, args.b)
        elif args.command == 'divisors':
            result = number_theory.divisors(args.n)
        elif args.command == 'sum-divisors':
            result = number_theory.sum_of_divisors(args.n)
        elif args.command == 'is-perfect':
            result = number_theory.is_perfect_number(args.n)
        
        # LOGIC
        elif args.command == 'truth-table':
            table = logic.generate_truth_table(args.expression)
            print(format_truth_table(table))
            return
        elif args.command == 'is-tautology':
            result = logic.is_tautology(args.expression)
        elif args.command == 'is-contradiction':
            result = logic.is_contradiction(args.expression)
        elif args.command == 'is-contingency':
            result = logic.is_contingency(args.expression)
        elif args.command == 'to-cnf':
            result = logic.convert_to_cnf(args.expression)
        elif args.command == 'to-dnf':
            result = logic.convert_to_dnf(args.expression)
        elif args.command == 'logic-equiv':
            result = logic.are_equivalent(args.expr1, args.expr2)
        elif args.command == 'simplify-logic':
            result = logic.simplify(args.expression)
        elif args.command == 'eval-logic':
            values_str = args.values.lower().replace('true', 'True').replace('false', 'False')
            values = parse_dict(values_str)
            result = logic.evaluate(args.expression, values)
        elif args.command == 'minterms':
            result = logic.get_minterms(args.expression)
        elif args.command == 'maxterms':
            result = logic.get_maxterms(args.expression)
        
        # SETS
        elif args.command == 'set-union':
            parsed_sets = [parse_set(s) for s in args.sets]
            result = sets_module.union(*parsed_sets)
        elif args.command == 'set-intersect':
            parsed_sets = [parse_set(s) for s in args.sets]
            result = sets_module.intersection(*parsed_sets)
        elif args.command == 'set-diff':
            result = sets_module.difference(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'set-sym-diff':
            result = sets_module.symmetric_difference(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'set-complement':
            result = sets_module.complement(parse_set(args.set_a), parse_set(args.universal))
        elif args.command == 'power-set':
            result = sets_module.power_set(parse_set(args.set_input))
        elif args.command == 'cartesian':
            result = sets_module.cartesian_product(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'cartesian-n':
            parsed_sets = [parse_set(s) for s in args.sets]
            result = sets_module.cartesian_product_n(*parsed_sets)
        elif args.command == 'is-subset':
            result = sets_module.is_subset(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'is-proper-subset':
            result = sets_module.is_proper_subset(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'is-superset':
            result = sets_module.is_superset(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'is-disjoint':
            result = sets_module.is_disjoint(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'cardinality':
            result = sets_module.cardinality(parse_set(args.set_input))
        elif args.command == 'is-partition':
            s = parse_set(args.set_s)
            subsets = [parse_set(sub) for sub in args.subsets]
            result = sets_module.partition(s, *subsets)
        elif args.command == 'sets-equal':
            result = sets_module.are_equal(parse_set(args.set_a), parse_set(args.set_b))
        elif args.command == 'power-set-size':
            result = sets_module.power_set_cardinality(parse_set(args.set_input))
        
        # RELATIONS
        elif args.command == 'is-reflexive':
            result = relations.is_reflexive(parse_relation(args.relation), parse_set(args.domain))
        elif args.command == 'is-symmetric':
            result = relations.is_symmetric(parse_relation(args.relation))
        elif args.command == 'is-antisymmetric':
            result = relations.is_antisymmetric(parse_relation(args.relation))
        elif args.command == 'is-transitive':
            result = relations.is_transitive(parse_relation(args.relation))
        elif args.command == 'is-equivalence':
            result = relations.is_equivalence_relation(parse_relation(args.relation), parse_set(args.domain))
        elif args.command == 'is-partial-order':
            result = relations.is_partial_order(parse_relation(args.relation), parse_set(args.domain))
        elif args.command == 'reflexive-closure':
            result = relations.reflexive_closure(parse_relation(args.relation), parse_set(args.domain))
        elif args.command == 'symmetric-closure':
            result = relations.symmetric_closure(parse_relation(args.relation))
        elif args.command == 'transitive-closure':
            result = relations.transitive_closure(parse_relation(args.relation))
        elif args.command == 'equiv-classes':
            result = relations.equivalence_classes(parse_relation(args.relation), parse_set(args.domain))
        elif args.command == 'compose-rel':
            result = relations.compose(parse_relation(args.relation1), parse_relation(args.relation2))
        elif args.command == 'inverse-rel':
            result = relations.inverse_relation(parse_relation(args.relation))
        elif args.command == 'rel-domain':
            result = relations.get_domain(parse_relation(args.relation))
        elif args.command == 'rel-range':
            result = relations.get_range(parse_relation(args.relation))
        elif args.command == 'rel-matrix':
            result = relations.relation_matrix(parse_relation(args.relation), parse_set(args.domain))
        
        # FUNCTIONS
        elif args.command == 'is-function':
            result = functions.is_function(parse_relation(args.relation), parse_set(args.domain))
        elif args.command == 'is-injective':
            result = functions.is_injective(parse_relation(args.relation))
        elif args.command == 'is-surjective':
            result = functions.is_surjective(parse_relation(args.relation), parse_set(args.codomain))
        elif args.command == 'is-bijective':
            result = functions.is_bijective(parse_relation(args.relation), parse_set(args.domain), parse_set(args.codomain))
        elif args.command == 'compose-func':
            result = functions.compose_functions(parse_relation(args.f), parse_relation(args.g))
        elif args.command == 'inverse-func':
            result = functions.inverse_function(parse_relation(args.relation), parse_set(args.domain), parse_set(args.codomain))
        elif args.command == 'func-domain':
            result = functions.get_domain(parse_relation(args.relation))
        elif args.command == 'func-range':
            result = functions.get_range(parse_relation(args.relation))
        elif args.command == 'func-to-dict':
            result = functions.function_to_dict(parse_relation(args.relation))
        
        # GRAPHS
        elif args.command == 'complete-graph':
            g = graphs.create_complete_graph(args.n)
            result = f"Complete graph K_{args.n}\nVertices: {sorted(g.get_vertices())}\nEdges: {sorted(g.get_edges())}"
        elif args.command == 'cycle-graph':
            g = graphs.create_cycle_graph(args.n)
            result = f"Cycle graph C_{args.n}\nVertices: {sorted(g.get_vertices())}\nEdges: {sorted(g.get_edges())}"
        elif args.command == 'path-graph':
            g = graphs.create_path_graph(args.n)
            result = f"Path graph P_{args.n}\nVertices: {sorted(g.get_vertices())}\nEdges: {sorted(g.get_edges())}"
        elif args.command == 'graph-bfs':
            edges = parse_list(args.edges)
            g = graphs.Graph(directed=args.directed)
            for e in edges:
                g.add_edge(e[0], e[1])
            result = g.bfs(args.start)
        elif args.command == 'graph-dfs':
            edges = parse_list(args.edges)
            g = graphs.Graph(directed=args.directed)
            for e in edges:
                g.add_edge(e[0], e[1])
            result = g.dfs(args.start)
        elif args.command == 'graph-connected':
            edges = parse_list(args.edges)
            g = graphs.Graph(directed=args.directed)
            for e in edges:
                g.add_edge(e[0], e[1])
            result = g.is_connected()
        elif args.command == 'graph-cycle':
            edges = parse_list(args.edges)
            g = graphs.Graph(directed=args.directed)
            for e in edges:
                g.add_edge(e[0], e[1])
            result = g.has_cycle()
        elif args.command == 'graph-bipartite':
            edges = parse_list(args.edges)
            g = graphs.Graph()
            for e in edges:
                g.add_edge(e[0], e[1])
            result = g.is_bipartite()
        elif args.command == 'graph-shortest-path':
            edges = parse_list(args.edges)
            g = graphs.Graph(directed=args.directed)
            for e in edges:
                g.add_edge(e[0], e[1])
            path, dist = g.shortest_path(args.start, args.end)
            result = f"Path: {path}\nDistance: {dist}"
        elif args.command == 'graph-topo-sort':
            edges = parse_list(args.edges)
            g = graphs.Graph(directed=True)
            for e in edges:
                g.add_edge(e[0], e[1])
            result = g.topological_sort()
            if result is None:
                result = "No topological sort exists (graph has cycle or is not directed)"
        
        # Display result
        if result is not None:
            print(format_output(result))
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
