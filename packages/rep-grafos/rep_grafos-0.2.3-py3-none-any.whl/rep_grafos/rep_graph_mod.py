import logging, math

class RepModular:    

    def __init__(self, c):                        
        self.c = c                        
        self.logger = logging.getLogger(__name__)        

    def gerarCoprimos(self, c, minimo):
        coprimos = []

        candidato = minimo
        while len(coprimos) < c:
            if all(math.gcd(candidato, cp) == 1 for cp in coprimos):
                coprimos.append(candidato)
            candidato += 1            
        
        return coprimos

    def encontraX(self, n, N):

        def extended_gcd(a, b):
            if b == 0:
                return a, 1, 0
            else:
                g, x, y = extended_gcd(b, a % b)
                return g, y, x - (a // b) * y

        g, x, _ = extended_gcd(N, n)
        if g != 1:
            raise ValueError("N não tem inverso módulo n")       
        
        return x % n

    def estaContido(self, A, B):        
        for i in B:
            if i not in A:
                return False
        return True
        
    def calcularSolucao(self, vizinhos, inicio):

        resultado = 0

        for i in range(len(self.parametros)):
            parametro = self.parametros[i]
            resultado += (parametro*vizinhos[inicio+i])
        
        return resultado % self.N_solucao


    def compactarVertice(self, i, vizinhos):
        
        for inicio in range(0, len(vizinhos), self.c):
        
            fim = inicio + self.c  

            if len(vizinhos) >= fim and (fim - inicio) == self.c:                             
                self.count_hash += 1            
                self.count_hash_tested += 1
                solucao = self.calcularSolucao(vizinhos, inicio)               
                self.HASHES[i]["hashes"].append(solucao)                
                
        if len(vizinhos) % self.c == 0:
            self.HASHES[i]["vertices"] = []
        else:            
            self.HASHES[i]["vertices"] = vizinhos[inicio:]


    def prepararParametros(self):
        coprimos = self.gerarCoprimos(self.c, minimo=self.minimo)
        N = math.prod(coprimos)
        parametros = []        

        for i, cp in enumerate(coprimos):
            ni = N//cp
            x = self.encontraX(cp, ni)
            parametros.append(ni*x)
        
        return N, parametros        

    def construir(self, G):
        
        self.G = G
        self.n = len(G.vs)

        self.minimo = self.n

        self.HASHES = {}
        self.count_hash = 0
        self.count_hash_tested = 0
               
        self.N_solucao, self.parametros = self.prepararParametros()

        for i in range(self.n):
            self.HASHES[i] = {"vertices":[],"hashes":[]}
            vizinhos = G.neighbors(i)                    
            self.compactarVertice(i, vizinhos)
            

    def contem(self, i, j):
        if j in self.HASHES[i]["vertices"]:
            return True

        coprimos = self.gerarCoprimos(self.c, minimo=self.minimo)

        for h in self.HASHES[i]["hashes"]:
                        
            for cp in coprimos:                
                if h % cp == j:
                    return True                   
                
        return False
    
    def obterDados(self):
        
        totalh = 0
        totalm = 0        
        total_bits_solucoes = 0      
        for i in range(self.n): 
            total_bits_solucoes += sum([int(x).bit_length() for x in self.HASHES[i]["hashes"]])
            totalh += len(self.HASHES[i]["hashes"])
            totalm += len(self.HASHES[i]["vertices"])            
        
        return totalh, totalm, total_bits_solucoes, self.N_solucao
    

    def obterVizinhos(self, i):
        yield from self.HASHES[i]["vertices"]
        
        coprimos = self.gerarCoprimos(self.c, minimo=self.minimo)

        for h in self.HASHES[i]["hashes"]:
            for cp in coprimos:
                yield h % cp
             

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