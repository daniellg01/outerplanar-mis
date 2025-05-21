import networkx as nx
from collections import deque, defaultdict
from itertools import combinations
import time

def outerplanar_maximum_independent_set(G):
    start_total = time.perf_counter()

    total_sol = set()
    total_size = 0

    start_cc = time.perf_counter()
    connected_components = list(nx.connected_components(G))
    end_cc = time.perf_counter()
    print(f"  - Tiempo Descomposición CC: {end_cc - start_cc:.6f} segundos")

    for i, comp in enumerate(connected_components):
        H = G.subgraph(comp).copy()
        print(f" Procesando Componente Conectado {i+1}/{len(connected_components)} (Nodos: {H.number_of_nodes()})")
        mis_nodes, mis_size, timings_cc = solve_cc(H)
        total_sol |= mis_nodes
        total_size += mis_size

        print(f"    - Tiempos dentro de solve_cc para Componente {i+1}:")
        for stage, duration in timings_cc.items():
            print(f"      - {stage}: {duration:.6f} segundos")

    end_total = time.perf_counter()
    print(f"Tiempo Total (outerplanar_maximum_independent_set): {end_total - start_total:.6f} segundos")

    return total_size, list(total_sol)

def solve_cc(H):
    timings = {}
    start_solve_cc = time.perf_counter()

    n = H.number_of_nodes()
    if n == 0:
        return set(), 0, timings
    if n == 1:
        v = next(iter(H.nodes()))
        return {v}, 1, timings

    start_fill_in = time.perf_counter()
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
    end_fill_in = time.perf_counter()
    timings['Reducción y Fill-in'] = end_fill_in - start_fill_in

    start_cliques = time.perf_counter()
    cliques = list(nx.find_cliques(chordal))
    end_cliques = time.perf_counter()
    timings['Identificación de Cliques'] = end_cliques - start_cliques

    start_build_Q = time.perf_counter()
    Q = nx.Graph()
    for i, C in enumerate(cliques):
        Q.add_node(i, nodes=C)
    for i in range(len(cliques)):
        for j in range(i+1, len(cliques)):
            inter = set(cliques[i]) & set(cliques[j])
            if inter:
                Q.add_edge(i, j, weight=len(inter))
    end_build_Q = time.perf_counter()
    timings['Construcción Grafo de Cliques (Q)'] = end_build_Q - start_build_Q

    start_build_T = time.perf_counter()
    if Q.number_of_edges() > 0:
        T = nx.maximum_spanning_tree(Q, weight='weight')
    else:
        T = nx.Graph()
        T.add_nodes_from(Q.nodes())
    end_build_T = time.perf_counter()
    timings['Construcción Árbol Expansión (T)'] = end_build_T - start_build_T

    start_build_tree_struct = time.perf_counter()
    if T.number_of_nodes() > 0:
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
    else:
        root = None
        parent = {}
        children = defaultdict(list)

    end_build_tree_struct = time.perf_counter()
    timings['Construcción Estructura Árbol'] = end_build_tree_struct - start_build_tree_struct


    H_adj = {v: set(H[v]) for v in H}
    dp = {}

    start_dp = time.perf_counter()
    def dfs(u):
        if u is None: return
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
                    inter_nodes_u_c = set(Q.nodes[u]['nodes']) & set(Q.nodes[c]['nodes'])
                    for W, (val, _) in dp[c].items():
                        if set(W) & inter_nodes_u_c == Uset & inter_nodes_u_c:
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

    if root is not None:
        dfs(root)
    end_dp = time.perf_counter()
    timings['Programación Dinámica (DFS)'] = end_dp - start_dp

    start_reconstruction = time.perf_counter()
    sol = set()
    bestScore = 0
    if root is not None and root in dp and dp[root]:
        bestU, (bestScore, _) = max(dp[root].items(), key=lambda x: x[1][0])
        sol = set(bestU)

        def collect(u, U):
            if u is None: return
            if u in dp and U in dp[u] and len(dp[u][U]) > 1:
                for c in children[u]:
                    if c in dp[u][U][1]:
                        W = dp[u][U][1][c]
                        sol.update(W)
                        collect(c, W)

        collect(root, bestU)
    end_reconstruction = time.perf_counter()
    timings['Reconstrucción Solución'] = end_reconstruction - start_reconstruction

    end_solve_cc = time.perf_counter()
    timings['Total solve_cc'] = end_solve_cc - start_solve_cc

    return sol, bestScore, timings

def mis_brute_force(graph):
    start_bf = time.perf_counter()
    max_independent_set = set()
    max_size = 0
    nodes = list(graph.nodes())
    for i in range(1, len(nodes) + 1):
        for subset_nodes in combinations(nodes, i):
            is_independent = True
            for u in subset_nodes:
                for v in subset_nodes:
                    if u != v and graph.has_edge(u, v):
                        is_independent = False
                        break
                if not is_independent:
                    break

            if is_independent:
                if len(subset_nodes) > max_size:
                    max_size = len(subset_nodes)
                    max_independent_set = set(subset_nodes)

    end_bf = time.perf_counter()
    print(f"Tiempo Total (mis_brute_force): {end_bf - start_bf:.6f} segundos")

    return max_size, list(max_independent_set)


if __name__ == "__main__":
    print("--- Ejecutando Algoritmo Outerplanar ---")
    G_path5 = nx.path_graph(5)
    size_op, nodes_op = outerplanar_maximum_independent_set(G_path5)
    print(f"Path_graph(5): MIS tamaño = {size_op}, nodos = {sorted(nodes_op)}\n")

    print("--- Ejecutando Fuerza Bruta (para comparación) ---")
    size_bf, nodes_bf = mis_brute_force(G_path5)
    print(f"Path_graph(5): MIS tamaño = {size_bf}, nodos = {sorted(nodes_bf)}\n")


    test_graphs = []

    G1_large = nx.path_graph(20)
    test_graphs.append(("Camino de 20 vértices", G1_large))

    G2_large = nx.star_graph(19)
    test_graphs.append(("Estrella K1,19", G2_large))

    G3_large = nx.cycle_graph(18) 
    G3_large.add_edge(0, 9)
    test_graphs.append(("Ciclo de 18 vértices con cuerda (0-9)", G3_large))

    def ladder_graph(n):
        G = nx.Graph()
        for i in range(n):
            G.add_node(i)
            G.add_node(i + n)
        for i in range(n - 1):
            G.add_edge(i, i + 1)
            G.add_edge(i + n, i + 1 + n)
        for i in range(n):
            G.add_edge(i, i + n)
        return G

    G4_large = ladder_graph(10)
    test_graphs.append(("Grafo escalera de 10 peldaños", G4_large))

    G5_large = nx.balanced_tree(r=2, h=3)
    test_graphs.append(("Árbol binario (profundidad 3)", G5_large))

    G6_larger_path = nx.path_graph(25)
    test_graphs.append(("Camino de 25 vértices", G6_larger_path))


    print("\n--- Ejecutando Algoritmo Outerplanar en Grafos de Prueba Grandes ---")
    for name, G in test_graphs:
        print(f"\nProcesando: {name}")
        size_op, nodes_op = outerplanar_maximum_independent_set(G)
        print(f"Resultado {name}: MIS tamaño = {size_op}, nodos = {sorted(nodes_op)}")

    print("\n--- Ejecutando Fuerza Bruta en Grafos de Prueba (sin límite) ---")
    for name, G in test_graphs:
        print(f"\nProcesando (Fuerza Bruta): {name}")
        size_bf, nodes_bf = mis_brute_force(G)
        print(f"Resultado (Fuerza Bruta) {name}: MIS tamaño = {size_bf}, nodos = {sorted(nodes_bf)}")

