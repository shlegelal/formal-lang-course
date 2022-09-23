import pyformlang.regular_expression as re
import pyformlang.finite_automaton as fa
import networkx as nx


def regex_to_min_dfa(raw_regex: str) -> fa.DeterministicFiniteAutomaton:
    regex = re.Regex(raw_regex)
    min_dfa = regex.to_epsilon_nfa().minimize()
    return min_dfa


def graph_to_nfa(
    graph: nx.Graph,
    start_states: set | None = None,
    final_states: set | None = None,
) -> fa.EpsilonNFA:
    enfa = fa.EpsilonNFA()

    # Only iterating through edges as isolated nodes can be either start or final and
    # thus will be added later anyway
    for pred, succ, data in graph.edges.data():
        pred_state = fa.State(pred)
        succ_state = fa.State(succ)
        symbol = fa.Symbol(data["label"]) if "label" in data else fa.Epsilon
        enfa.add_transition(pred_state, symbol, succ_state)

    if start_states is None:
        start_states = set(graph.nodes)
    if final_states is None:
        final_states = set(graph.nodes)

    for state in start_states:
        enfa.add_start_state(state)
    for state in final_states:
        enfa.add_final_state(state)

    return enfa
