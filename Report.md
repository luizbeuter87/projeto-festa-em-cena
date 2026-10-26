# Relatório Técnico de Avaliação (Report.md) — Festa em Cena

Este relatório técnico documenta as regras de negócio, decisões arquiteturais e métricas de qualidade obtidas na higienização e validação da base , estruturado rigorosamente conforme a rúbrica de avaliação.

---

## 1. Manipulação e Ingestão de Dados (Critério 2)

A ingestão do arquivo foi realizada através da função carregar_dados() com a biblioteca Pandas:
python
df = pd.read_csv(halloween_vendas, dtype=str, keep_default_na=False)
return df.to_dict(orient='records')

### Decisões Técnicas Fundamentadas:
* Uso dedtype=str: Por padrão, o Pandas tenta inferir tipos automaticamente, convertendo colunas de identificadores (pedido_id) ou códigos em valores numéricos (int ou float). Forçar dtype=str garante que 100% dos registros entrem como texto bruto, permitindo que a validação lógica seja realizada manualmente.
* Uso de keep_default_na=False: O comportamento padrão do Pandas é converter células vazias (""), espaços ou strings como "NA" no tipo de ponto flutuante NaN (Not a Number). Com esse parâmetro desativado, campos em branco continuam sendo strings vazias nativas (""), evitando quebras de tipos (TypeError) e permitindo validações diretas com .strip() == "".
* Conversão com .to_dict(orient='records'): Permite processar os registros linha por linha como dicionários nativos do Python, garantindo controle procedural sem dependência de métodos vetorizados adicionais.

---

## 2. Tratamento de Nulos e Condicionais (Critério 3)

### Tratamento de Categorias Vazias
Implementado através da função tratar_categoria() utilizando estrutura condicional if/else:
* Se o texto higienizado estiver vazio ("") ou for None, preenche-se com "Sem Categoria" (18 ocorrências preenchidas).
* Caso contrário, preserva-se o valor higienizado original.

### Tratamento e Justificativa de Dimensões Físicas (tamanho)
Implementado na função tratar_dimensao_fisica():
* Os produtos da loja física e web possuem tamanhos como P, M, M ou Unico.
* Regra e Justificativa: Caso um registro apresente tamanho vazio, o valor é classificado como "Não Informado". Não se deve imputar tamanhos arbitrários ou moda estatística, pois inventar uma dimensão corporal de uma fantasia induz o cliente ao erro, gerando devoluções, trocas e custos logísticos adicionais. Na base avaliada, foram encontrados 0 tamanhos vazios (todos estavam preenchidos).

### Validação Numérica e Princípio da Não Imputação
* validar_quantidade(): Exige conversão para número inteiro estritamente positivo (> 0). Foram identificadas 7 quantidades inválidas (valores menores ou iguais a zero).
* validar_preco(): Exige preenchimento e conversão para ponto flutuante não negativo (>= 0.0). Foram identificados 12 preços unitários vazios ou inválidos.
* Uso da Estrutura set(): Utilizou-se pedidos_com_problema_numerico = set(). Como conjuntos não armazenam elementos duplicados, caso um mesmo pedido apresentasse erro em quantidade E preço simultaneamente, seu pedido_id seria contabilizado apenas uma vez. O resultado final registrou exatamente 19 pedidos distintos afetados.
* Por que não imputar média ou mediana? Em auditorias transacionais, preencher valores financeiros por média mascara fraudes, erros de integração de API e anomalias sistêmicas de caixas registradores. A diretriz foi isolar e reportar a inconsistência sem criar receitas fictícias.

---

## 3. Regras de Negócio e Módulo Datetime (Critério 4)

### Conversão Temporal com datetime.strptime
A conversão foi feita pela função  no formato  dentro de um bloco :
* Por que usar try/except? A base contém 4 registros com datas corrompidas. A captura da exceção impede que a aplicação seja interrompida bruscamente, retornando None e permitindo que os outros 1.496 registros continuem sendo processados.
* Não substituição pela data atual: Preencher datas com datetime.now() introduziria um viés severo de série temporal, alocando artificialmente pedidos sazonais antigos no ano corrente.

### Teste da Hipótese: "Data de Entrega Vazia Implica Status Cancelado"
Investigou-se se todo pedido com data_entrega vazia possui status_pedido == "Cancelado".
* Total de pedidos sem data de entrega: 143 pedidos
* Pedidos sem entrega e Cancelados: 109 pedidos
* Pedidos sem entrega e com Outros Status (Contraexemplos): 34 pedidos

Conclusão da Hipótese: A hipótese é FALSA.  
Identificaram-se 34 pedidos com status_pedido == "Concluído" que não possuem data de entrega preenchida.  
Exemplos de Contraexemplos Separados:
1. *Pedido #1170* | Status: Concluído | Produto: *Fantasia de abobora* | Tamanho: *P*
2. *Pedido #990* | Status: Concluído | Produto: *Fantasia de fantasma* | Tamanho: *M*
3. *Pedido #740* | Status: Concluído | Produto: *Fantasia de abobora* | Tamanho: *P*

*Interpretação:* A ausência de data de entrega reflete pedidos retirados presencialmente no balcão de lojas físicas ou falhas operacionais na baixa do rastreio logístico, e não o cancelamento da transação.

---

## 4. Limpeza de Strings e Módulo  (Critério 5)

### Padronização de Categorias com Expressões Regulares
A função padrinizar_categoria() aplicou:
1. .strip() e .lower() para remoção de bordas e uniformização.
2. re.sub(r"[^a-z ]", "", limpo) para expurgar pontuações indesejadas (como exclamações "!" e ruídos de teclado), preservando letras sem acento e espaços.
3. re.sub(r"\s+", " ", limpo).strip() para eliminar múltiplos espaços em branco.
* Total de categorias não vazias que sofreram alteração: 131 registros.

### Padronização de Canais de Venda
A função padronizar_canal() uniformizou as strings para os três canais homologados:
* "Mercado"
* "Loja física"(unificando entradas como "loja fisica" e "loja física")
* "Web"
* Total de canais que necessitaram de ajuste de escrita: 45 registros.
