import random, math, mmh3, time, sys
from ctypes import c_int32, c_int64, c_uint64, c_uint32, c_ulonglong


class SpatialXorFilter:    
    
    ARRAY_SIZE = 0
    WINDOW = 0
    HASHES = 5
    BITS_PER_FINGERPRINT = 8             
    FUNC_SIZE_ARRAY = None       
    FUNC_SIZE_Z = None       

    def __init__(self, func_size, func_size_z, hashes = 5, iteracoes=500, tamanho_fingerprint = 8):
      self.HASHES = hashes
      self.BITS_PER_FINGERPRINT = tamanho_fingerprint      
      self.MAX_ITERATIONS = iteracoes      
      self.FUNC_SIZE_ARRAY = func_size      
      self.FUNC_SIZE_Z = func_size_z      
      assert self.FUNC_SIZE_ARRAY is not None
      assert self.FUNC_SIZE_Z is not None

    def fingerprint(self, x):
        return int(hash(x) & ((1 << self.BITS_PER_FINGERPRINT) - 1))    
    
    def murmur64(self, x):
        key = x.to_bytes((x.bit_length() + 7) // 8, 'big')
        return mmh3.hash64(key, seed = self.seed, signed=False)[0]    

    def hashIndependente(self, key, seed):
        return c_uint64(self.murmur64(key + c_uint64(seed).value)).value
    
    def hn(self, x, n, delta):
        return self.hashIndependente(x, self.seed + n) % delta

    def construir(self, S):

        iteracoes = 0

        self.ARRAY_SIZE = int(self.FUNC_SIZE_ARRAY(len(S)) * len(S))
        self.WINDOW = int(self.FUNC_SIZE_Z(len(S)))

        while True:

            self.seed = random.getrandbits(32)    

            sucesso, pilha = self.mapear(S)

            if sucesso:
              break

            iteracoes += 1

            if iteracoes == self.MAX_ITERATIONS:
              raise Exception("ERROU")

        self.atribuir(S, pilha)        

        return True, iteracoes



    def mapear(self, S):                      

        t = []

        H = [t[:] for _ in range(self.ARRAY_SIZE)]           

        for x in S:
            values = self.hns(x)            
            for ind in values:
              H[ind].append(x)

        Q = []

        for i in range(len(H)):
          if len(H[i]) == 1:
            Q.append(i)                

        sigma = []

        while len(Q) > 0:
          i = Q.pop()          

          if len(H[i]) == 1:
            x = H[i][0]
            sigma.append((x, i))                       

            values = self.hns(x)

            for ind in values:              

              if(x in H[ind]):
                H[ind].remove(x)

              if len(H[ind]) == 1:
                Q.append(ind)        

        if len(sigma) == len(S):                    
          return True, sigma
        else:
          return False, []
      
    def atribuir(self, S, sigma):
      self.B = [0] * self.ARRAY_SIZE

      while len(sigma) > 0:
        x, i = sigma.pop()
        values = self.hns(x)

        res = 0

        for item in values:
          res ^= self.B[item]

        self.B[i] = 0        
        self.B[i] = self.fingerprint(x) ^ res           

    def contem(self, x):
        values = self.hns(x)

        res = 0

        for item in values:
          res ^= self.B[item]

        return self.fingerprint(x) == res

    def hns(self, x):

        values = []

        start = self.hn(x, 0, self.ARRAY_SIZE - self.WINDOW) 
        block = self.WINDOW // self.HASHES        

        for i in range(self.HASHES):
          values.append(start + self.hn(x, i, block) + (i * block))        

        return values

    def espaco(self):
      return self.ARRAY_SIZE * self.BITS_PER_FINGERPRINT