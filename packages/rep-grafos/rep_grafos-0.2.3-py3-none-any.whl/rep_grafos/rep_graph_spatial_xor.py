import mmh3, random, logging
from collections import deque
from .xor_descascavel_by_f import SpatialXorFilter

class RepSpatialXOR:    

    def func_size(self, n):

        ALFA_A = 0.446
        ALFA_B = 0.269

        ALFA_V = 1/(1+(1/(ALFA_A * (n ** ALFA_B))))
        
        return 1/ALFA_V

    def func_size_z(self, n):

        Z_A = 3.04
        Z_B = 0.64

        R = Z_A * (n ** Z_B)
        
        return R

    def __init__(self, tamanho_fingerprint = 8, k = 5):                        
        self.H_INT_SIZE = tamanho_fingerprint 
        self.logger = logging.getLogger(__name__)
        self.k = k

    def estaContido(self, A, B):        
        for i in B:
            if i not in A:
                return False
        return True


    def construir(self, G):

        self.G = G
        self.n = len(G.vs)        

        self.FILTROS = []
        for i in range(self.n):    
            vizinhos = self.G.neighbors(i) 
            X = SpatialXorFilter(self.func_size, self.func_size_z, self.k)
            res = X.construir(vizinhos)

            if(res):
                self.FILTROS.append((i, True, X, vizinhos))
            else:
                self.FILTROS.append((i, False, vizinhos))        
            

    def contem(self, i, j):

        i, eh_filtro, filtro, vizinhos = self.FILTROS[i]

        if eh_filtro:
            res = filtro.contem(j)
        else:
            res = j in filtro

        return res

    def checks(self):
        for i in range(self.n):        
            vizinhos = self.G.neighbors(i) 

            for j in vizinhos:
                assert self.contem(i,j)

        return True  