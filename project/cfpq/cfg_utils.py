import pyformlang.cfg as c
from os import PathLike


def cfg_to_wcnf(cfg: str | c.CFG, start: str | None = None) -> c.CFG:
    if not isinstance(cfg, c.CFG):
        cfg = c.CFG.from_text(cfg, c.Variable(start if start is not None else "S"))
    tmp = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )
    new_productions = tmp._get_productions_with_only_single_terminals()
    new_productions = tmp._decompose_productions(new_productions)
    return c.CFG(start_symbol=cfg._start_symbol, productions=set(new_productions))


def read_cfg(path: PathLike, start: str = "S") -> c.CFG:
    with open(path, "r") as f:
        data = f.read()
    return c.CFG.from_text(data, c.Variable(start))


def accepts(cfg: c.CFG, word: str | list[c.Terminal]) -> bool:
    # Convert word into a more suitable format
    if isinstance(word, str):
        word = [c.Terminal(a) for a in word]

    # pyformlang discards epsilon during CNF conversion
    if len(word) == 0:
        return cfg.generate_epsilon()

    # After this all productions have a form of either A -> a or A -> B C
    cfg = cfg.to_normal_form()

    # Convert productions into a more efficient form
    vars_order = {v: i for i, v in enumerate(cfg.variables)}  # Order variables
    term_prods: dict[c.Variable, list[c.Terminal]] = {}  # A -> a
    var_prods: list[tuple[int, int, int]] = []  # A -> B C
    for p in cfg.productions:
        match len(p.body):
            case 1:
                term_prods.setdefault(p.head, []).append(p.body[0])
            case 2:
                var_prods.append(
                    (
                        vars_order[p.head],
                        vars_order[p.body[0]],
                        vars_order[p.body[1]],
                    )
                )

    # Initialize CYK matrix (performs step 0)
    m = [
        [
            [
                # true if exists var -> word[i], false otherwise
                i == j and var in term_prods and word[i] in term_prods[var]
                for var in vars_order
            ]
            for j in range(len(word))
        ]
        for i in range(len(word))
    ]

    # Run CYK steps >=1 by iterating over upper diagonals from center to corner
    for step in range(1, len(word)):
        # Iterate the diagonal from top-left to bottom-right
        for i in range(len(word) - step):
            j = step + i
            # Iterate over precalculated lists
            for k in range(i, j):
                # Iterate over productions and check if substring can be generated
                for (h, b1, b2) in var_prods:
                    # Using if not to overwrite previous Trues with False
                    if m[i][k][b1] and m[k + 1][j][b2]:
                        m[i][j][h] = True

    # Return whether start variable generates the whole word
    return m[0][len(word) - 1][vars_order[cfg.start_symbol]]
