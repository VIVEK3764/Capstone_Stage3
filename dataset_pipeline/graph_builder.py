import networkx as nx


def build_graph(slither):
    G = nx.DiGraph()

    for contract in slither.contracts:
        for f in contract.functions:
            caller = f.full_name

            # internal calls
            for callee in getattr(f, "internal_calls", []):
                try:
                    G.add_edge(caller, callee.full_name)
                except:
                    pass

            # external calls
            for call in getattr(f, "high_level_calls", []):
                try:
                    G.add_edge(caller, call[1].full_name)
                except:
                    pass

            # low level
            for call in getattr(f, "low_level_calls", []):
                G.add_edge(caller, "external_call")

    return G