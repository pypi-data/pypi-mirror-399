from rep_grafos import RepSpatialXOR
import igraph
 
def teste_verifica_que_vizinhos_sao_todos_representados():
    N = 100
    d = 0.5
    M = int(((N*(N-1))/2)*d)
    G = igraph.Graph.Erdos_Renyi(n=N, m=M)

    hash_size = 8
    k = 5

    rep = RepSpatialXOR(hash_size, k)   
    rep.construir(G)

    for i in range(N):        
        vizinhos = G.neighbors(i) 

        for j in vizinhos:                       
            assert rep.contem(i,j)