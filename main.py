import networkx as nx
from collections import deque, defaultdict
from itertools import combinations

def outerplanar_maximum_independent_set(G):
    def solve_cc(H):
        n = H.number_of_nodes()
        if n == 0:
            return set(), 0
        if n == 1:
            v = next(iter(H.nodes()))
            return {v}, 1

        deg = dict(H.degree())
        nbrs = {v: set(H[v]) for v in H}
        fill = []
        q = deque(v for v,d in deg.items() if d <= 2)
        removed = set()

        while q:
            v = q.popleft()
            if v in removed:
                continue
            removed.add(v)
            vs = [u for u in nbrs[v] if u not in removed]
            if len(vs) == 2:
                u, w = vs
                if w not in nbrs[u]:
                    fill.append((u, w))
                    nbrs[u].add(w)
                    nbrs[w].add(u)
                    deg[u] += 1
                    deg[w] += 1
            for u in vs:
                deg[u] -= 1
                if deg[u] == 2:
                    q.append(u)

        chordal = H.copy()
        chordal.add_edges_from(fill)

        cliques = list(nx.find_cliques(chordal))
        Q = nx.Graph()
        for i, C in enumerate(cliques):
            Q.add_node(i, nodes=C)
        for i in range(len(cliques)):
            for j in range(i+1, len(cliques)):
                inter = set(cliques[i]) & set(cliques[j])
                if inter:
                    Q.add_edge(i, j, weight=len(inter))
        if Q.number_of_edges() > 0:
            T = nx.maximum_spanning_tree(Q, weight='weight')
        else:
            T = nx.Graph()
            T.add_nodes_from(Q.nodes())
        root = next(iter(T.nodes()))

        parent = {root: None}
        children = defaultdict(list)
        seen = {root}
        stk = [root]
        while stk:
            u = stk.pop()
            for w in T[u]:
                if w not in seen:
                    seen.add(w)
                    parent[w] = u
                    children[u].append(w)
                    stk.append(w)

        H_adj = {v: set(H[v]) for v in H}
        dp = {}

        def dfs(u):
            for c in children[u]:
                dfs(c)
            bag = Q.nodes[u]['nodes']
            subs = []
            for r in range(len(bag)+1):
                for comb in combinations(bag, r):
                    ok = True
                    for i in range(r):
                        for j in range(i+1, r):
                            if comb[j] in H_adj[comb[i]]:
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        subs.append(comb)

            dp[u] = {}
            if not children[u]:
                for U in subs:
                    dp[u][U] = (len(U), {})
            else:
                for U in subs:
                    Uset = set(U)
                    total = len(U)
                    choices = {}
                    feas = True
                    for c in children[u]:
                        best = None
                        bestW = None
                        for W, (val, _) in dp[c].items():
                            inter = set(Q.nodes[u]['nodes']) & set(Q.nodes[c]['nodes'])
                            if set(W) & inter == Uset & inter:
                                overlap = len(set(W) & Uset)
                                score = val - overlap
                                if best is None or score > best:
                                    best, bestW = score, W
                        if bestW is None:
                            feas = False
                            break
                        total += best
                        choices[c] = bestW
                    if feas:
                        dp[u][U] = (total, choices)

        dfs(root)

        bestU, (bestScore, _) = max(dp[root].items(), key=lambda x: x[1][0])
        sol = set(bestU)

        def collect(u, U):
            for c in children[u]:
                W = dp[u][U][1][c]
                sol.update(W)
                collect(c, W)

        collect(root, bestU)
        return sol, bestScore

    total_sol = set()
    total_size = 0
    for comp in nx.connected_components(G):
        H = G.subgraph(comp).copy()
        mis_nodes, mis_size = solve_cc(H)
        total_sol |= mis_nodes
        total_size += mis_size
    return total_size, list(total_sol)

if __name__ == "__main__":
    G = nx.path_graph(5)
    size, nodes = outerplanar_maximum_independent_set(G)
    print(f"Path_graph(5): MIS tamaño = {size}, nodos = {sorted(nodes)}")



test_graphs = []

G1 = nx.path_graph(6)
test_graphs.append(("Camino de 6 vértices", G1))

G2 = nx.cycle_graph(5)
test_graphs.append(("Ciclo de 5 vértices (C5)", G2))

G3 = nx.star_graph(4) 
test_graphs.append(("Estrella K1,4", G3))

G4 = nx.cycle_graph(3)
G4.add_node(3)
G4.add_edge(0, 3)
test_graphs.append(("Triángulo con una hoja", G4))

G5 = nx.cycle_graph(6)
G5.add_edge(0, 3)
test_graphs.append(("Ciclo de 6 vértices con cuerda (0-3)", G5))

G6 = nx.Graph()
G6.add_edges_from([
    (0, 1), (1, 2), (2, 3),
    (0, 4), (4, 3),  
    (1, 5), (5, 2) 
])
test_graphs.append(("Serie-paralelo simple", G6))

G7 = nx.Graph()
n = 6
for i in range(n - 1):
    G7.add_edge(i, i + 1)      
    G7.add_edge(i + n, i + 1 + n)  
    G7.add_edge(i, i + n)       
G7.add_edge(n - 1, 2 * n - 1)
test_graphs.append(("Grafo escalera de 5 peldaños", G7))

G8 = nx.balanced_tree(r=2, h=2)
test_graphs.append(("Árbol binario (profundidad 2)", G8))

for name, G in test_graphs:
    size, nodes = outerplanar_maximum_independent_set(G)
    print(f"{name}:\n - Tamaño MIS = {size}\n - Nodos: {sorted(nodes)}\n")