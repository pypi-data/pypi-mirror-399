import mmh3, random, logging
from collections import deque

class RepProbabilistic:    

    def __init__(self, c, hash_size = 16, fator = 0.12):                        
        self.c = c        
        self.fator = fator
        self.H_INT_SIZE = hash_size 
        self.logger = logging.getLogger(__name__)

    def gerarSeed(self):      
        return random.randint(1, ((1 << self.H_INT_SIZE) - 1))

    def murmur64(self, x, seed):
        return mmh3.hash(str(x), seed = seed, signed=False)

    def estaContido(self, A, B):        
        for i in B:
            if i not in A:
                return False
        return True

    def selecionarVertices(self, i, n, k, seed):           
        
        selected = set()
        selected_add = selected.add
        indice = 1

        while len(selected) < k:               
            i = self.murmur64(indice, seed) % n      
            while i in selected:
                indice += 1
                i = self.murmur64(indice, seed) % n

            indice += 1
            selected_add(i)

        return list(selected)

    def removerArestas(self, ARESTAS, itens):
        for item in itens:
            ARESTAS.remove(item)

    def compactarVertice(self, i, vizinhos, E_MAX, CACHE = []):

        while len(vizinhos) > self.c and len(vizinhos) > E_MAX:

            h0 = self.gerarSeed()
            self.count_hash += 1            
            self.count_hash_tested += 1            

            vizinhosRemover = self.selecionarVertices(i, self.n, self.c, h0)            

            if self.estaContido(vizinhos, vizinhosRemover):                
                self.HASHES[i]["hashes"].append(h0)
                self.removerArestas(vizinhos, vizinhosRemover)
            else:
                CACHE.append((h0, vizinhosRemover))                
        
        self.HASHES[i]["vertices"] = vizinhos


    def construir(self, G):

        CACHE = deque(maxlen=10**8)

        self.G = G
        self.n = len(G.vs)

        self.HASHES = {}
        self.count_hash = 0
        self.count_hash_tested = 0

        for i in range(self.n):                            
            self.HASHES[i] = {"vertices":[],"hashes":[]}
            vizinhos = G.neighbors(i)    
            E_MAX = int(self.n * self.fator)            

            for h0, vizinhosRemover in CACHE:

                self.count_hash_tested += 1

                if len(vizinhos) <= E_MAX:
                    break

                if self.estaContido(vizinhos, vizinhosRemover):
                    self.HASHES[i]["hashes"].append(h0)
                    self.removerArestas(vizinhos, vizinhosRemover)                                                                                 

            self.compactarVertice(i, vizinhos, E_MAX, CACHE)        
            

    def contem(self, i, j):
        if j in self.HASHES[i]["vertices"]:
            return True

        for h in self.HASHES[i]["hashes"]:

            if j in self.selecionarVertices(i, self.n, self.c, h):
                return True
        
        return False
    
    def obterDados(self):
        
        totalh = 0
        totalm = 0        
        for i in range(self.n):  
            totalh += len(self.HASHES[i]["hashes"])
            totalm += len(self.HASHES[i]["vertices"])            
        
        return totalh, totalm                 
    
    def obterVizinhos(self, i):
        yield from self.HASHES[i]["vertices"]
        for h in self.HASHES[i]["hashes"]:
            yield from self.selecionarVertices(i, self.n, self.c, h)


    def adicionar(self, arestas):

        RECOMPACTAR = set()

        for i, j in arestas:
            self.HASHES[i]["vertices"].append(j)
            self.HASHES[j]["vertices"].append(i)
            RECOMPACTAR.add(i)
            RECOMPACTAR.add(j)

        for v in RECOMPACTAR:             
             vizinhos = self.HASHES[v]["vertices"]
             E_MAX = int(((len(self.HASHES[v]["hashes"]) * 3) + len(vizinhos)) * self.fator)
             self.compactarVertice(v, vizinhos, E_MAX)          
    
    def removerDoVertice(self, i, j):
        if j in self.HASHES[i]["vertices"]:
            self.HASHES[i]["vertices"].remove(j)
        else:                 
            for h in self.HASHES[i]["hashes"]:
                vertices = self.selecionarVertices(i, self.n, self.c, h)
                if j in vertices:
                    self.HASHES[i]["hashes"].remove(h)
                    self.HASHES[i]["vertices"].extend([v for v in vertices if v != j])                    
                    break

    def remover(self, arestas):

        RECOMPACTAR = set()

        for i, j in arestas:
            self.removerDoVertice(i, j)
            self.removerDoVertice(j, i)
            RECOMPACTAR.add(i)
            RECOMPACTAR.add(j)

        for v in RECOMPACTAR:             
             vizinhos = self.HASHES[v]["vertices"]
             E_MAX = int(((len(self.HASHES[v]["hashes"]) * 3) + len(vizinhos)) * self.fator)                         
             self.compactarVertice(v, vizinhos, E_MAX)          

    def checks(self):
        for i in range(self.n):        
            vizinhos = self.G.neighbors(i) 

            for j in vizinhos:
                assert self.contem(i,j)

        G_C = self.G.complementer(loops=False)

        for i in range(self.n):        
            vizinhos = G_C.neighbors(i) 

            for j in vizinhos:
                assert not self.contem(i,j)

        for i in range(self.n):
            assert self.estaContido(self.G.neighbors(i), self.obterVizinhos(i))     

        return True   