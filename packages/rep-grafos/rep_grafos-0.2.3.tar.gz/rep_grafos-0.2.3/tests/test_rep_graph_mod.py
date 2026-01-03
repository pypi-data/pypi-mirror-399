from rep_grafos import RepModular
import igraph
 
def teste_verificar_se_vizinhos_sao_todos_representados():
    N = 100
    d = 0.5
    M = int(((N*(N-1))/2)*d)
    G = igraph.Graph.Erdos_Renyi(n=N, m=M)

    c = 3

    rep = RepModular(c)    
    rep.construir(G)

    for i in range(N):        
        vizinhos = G.neighbors(i) 

        for j in vizinhos:                       
            assert rep.contem(i,j)

def teste_verificar_se_nao_vizinhos_nao_sao_representados():
    N = 100
    d = 0.5
    M = int(((N*(N-1))/2)*d)
    G = igraph.Graph.Erdos_Renyi(n=N, m=M)

    c = 3

    rep = RepModular(c)    
    rep.construir(G)

    G_C = G.complementer(loops=False)

    for i in range(N):        
        vizinhos = G_C.neighbors(i) 

        for j in vizinhos:
            assert not rep.contem(i,j)

def teste_verificar_se_metodo_vizinhos_retorna_vizinhaca_correta():
    N = 100
    d = 0.5
    M = int(((N*(N-1))/2)*d)
    G = igraph.Graph.Erdos_Renyi(n=N, m=M)

    c = 3

    rep = RepModular(c)    
    rep.construir(G)

    for i in range(N):
        assert rep.estaContido(G.neighbors(i), rep.obterVizinhos(i))