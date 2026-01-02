from nd_prover import *


tests = [
    # --- Nested implications / currying / composition ---
    (["P -> (Q -> R)", "P", "Q"], "R"),
    (["(P -> Q) -> (R -> S)", "P -> Q", "R"], "S"),
    (["P -> Q", "Q -> R"], "P -> R"),
    (["(P -> Q) and (Q -> R)"], "P -> R"),
    (["P -> (Q -> R)"], "(P and Q) -> R"),
    (["(P and Q) -> R"], "P -> (Q -> R)"),

    # --- Contradiction / explosion / nested negations ---
    (["not P", "P"], "Q"),
    (["not (P and Q)"], "P -> not Q"),
    (["not (P and Q)"], "Q -> not P"),
    (["not (P -> Q)", "P -> Q"], "R"),
    (["not not P"], "P"),  # classical
    (["not not (P or Q)"], "P or Q"),  # classical

    # --- De Morgan / distributivity-ish patterns ---
    (["not (P or Q)"], "not P and not Q"),
    (["not P and not Q"], "not (P or Q)"),  # FIX: double falsum (good now)
    (["not (P and Q)"], "not P or not Q"),  # FIX: double double falsum (1st fail with seen.copy())
    (["(P and Q) or (P and R)"], "P and (Q or R)"),  # FIX: slow
    (["P and (Q or R)"], "(P and Q) or (P and R)"),  # FIX: stuck here (2nd fail with seen.copy())

    # --- Disjunction elimination stress tests ---
    (["P or Q", "P -> R", "Q -> R"], "R"),
    (["(P -> R) and (Q -> R)", "P or Q"], "R"),
    (["(P or Q) and (P -> R) and (Q -> S)"], "R or S"),  # FIX: (3rd fail with seen.copy())
    (["(P or Q) -> R"], "(P -> R) and (Q -> R)"),

    # --- Biconditional nesting ---
    (["P <-> Q", "Q <-> R"], "P <-> R"),
    (["P <-> Q"], "(P -> Q) and (Q -> P)"),
    (["(P -> Q) and (Q -> P)"], "P <-> Q"),

    # --- “Irrelevant disjunction” traps (should NOT split early) ---
    ([], "(Q or not Q) -> (P or not P)"),
    (["Q or not Q"], "P or not P"),
    (["(Q or not Q) and (P -> R) and (R -> S)"], "P -> S"),

    # --- Nested mixed connectives (good for quality evaluation) ---
    (["(P -> Q) -> R", "P -> Q"], "R"),
    (["P -> (Q or R)", "not Q"], "P -> R"),
    (["(P or Q) -> (R or S)", "P", "not R"], "S"),  # FIX: not optimal
    (["(P -> Q) and (R -> S)", "P or R"], "Q or S"),
    (["(P -> Q) -> (R -> S)", "P -> Q", "R"], "S"),

    # --- Classic tautologies that can produce ugly proofs if IP/OrE is mismanaged ---
    ([], "(P -> Q) or (Q -> P)"),
    ([], "((P -> Q) -> P) -> P"),  # classical (Peirce's law)
    ([], "(not P -> P) -> P"),  # classical

    # --- Old ---
    ([], "not P or P"),
    ([], "P or not P"),
    (["P"], "P"),
    (["P and Q"], "P"),
    (["P and Q"], "Q"),
    (["P"], "Q or P"),
    (["P -> Q", "P"], "Q"),
    (["P"], "P or Q"),
    (["P -> Q"], "not Q -> not P"),
    (["P or Q", "not P"], "Q"),

    ([], "P <-> P"),
    (["P or P or P or P"], "P"),
]


for premises_str, conclusion_str in tests:
    premises = [parse_formula(p) for p in premises_str]
    conclusion = parse_formula(conclusion_str)

    print("=" * 70)
    print("Premises:", premises_str if premises_str else "∅")
    print("Conclusion:", conclusion_str)

    try:
        problem = prove(premises, conclusion)
        print(problem)
    except ProverError as e:
        print("No proof:", e)
