# Representação de grafos Las Vegas

São disponibilizadas duas classes ``RepProbabilistic``, ``RepSpatialXOR`` e ``RepModular`` para representação de grafos.

# Para executar
Primeiro instale o pacote:
> pip install rep-grafos

# Como usar

Aqui estão as instruções para utilização das classes:

## A classe ``RepProbabilistic``

São disponibilizados três parâmetros ``c``, ``hash_size`` e ``fator``. O parâmetro ``c`` indica que cada função hash em ``H[v]`` deve representar pelo menos ``c`` vizinhos de ``v``. O parâmetro ``hash_size`` diz o tamanho em bits das funções hash.  Já o parâmetro  ``q``,  refere-se à fração máxima de vizinhos de ``v`` que cada vértice ``v`` devem ser permitidos não serem representados pelas funções hash, isto é, presentes em ``D[v]``.

O método ``construir`` deve ser executado passando-se uma instância ``igraph.Graph`` ou qualquer instância que implemente os métodos ``neighbors`` que retorna os vizinhos de um determinado vértice e ``complementer`` que retorna o complemento de um grafo.

## A classe ``RepModular``

São disponibilizados os parâmetro ``c``. O parâmetro ``c`` indica que cada função hash em ``H[v]`` deve representar pelo menos ``c`` vizinhos de ``v``.

O método ``construir`` deve ser executado passando-se uma instância ``igraph.Graph`` ou qualquer instância que implemente os métodos ``neighbors`` que retorna os vizinhos de um determinado vértice e ``complementer`` que retorna o complemento de um grafo.

## A classe ``RepSpatialXOR``

São disponibilizados os parâmetro ``tamanho_fingerprint`` e ``k``. O parâmetro ``tamanho_fingerprint`` indica o tamanho em bits das funções hash dos filtros SpatialXOR. O parâmetro ``k`` é o número de funções hash utilizadas pelos filtros SpatialXOR.

O método ``construir`` deve ser executado passando-se uma instância ``igraph.Graph`` ou qualquer instância que implemente os métodos ``neighbors`` que retorna os vizinhos de um determinado vértice e ``complementer`` que retorna o complemento de um grafo.


A pasta ``data`` tem os dados do artigo, separados por ``;``.