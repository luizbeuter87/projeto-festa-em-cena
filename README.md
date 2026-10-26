# Festa em Cena — Auditoria e Higienização de Vendas de Halloween

Projeto desenvolvido para Mini-Projeto Avaliativo da formação em Machine Learning e Visão Computacional. O sistema executa a higienização de strings, validação de regras de integridade e auditoria exploratória sobre os dados de vendas da empresa Festa em Cena.

---

## Contexto do Projeto e Dados

### O Problema de Negócio
A equipe da Festa em Cena identificou anomalias no fechamento das campanhas sazonais de Halloween no arquivo . Havia divergências na digitação de categorias, pontuações indevidas, inconsistências em canais de venda, quantidades nulas, preços ausentes e carimbos de data fora do padrão. Antes de realizar qualquer projeção de demanda ou modelagem preditiva, fez-se necessária uma auditoria completa.

### Estrutura dos Dados
* Significado de Uma Linha: Cada linha representa uma transação comercial única (um pedido) registrada em um dos canais da empresa.
* Quatro Colunas Analisadas em Detalhe:
  1. pedido_id: Identificador numérico exclusivo de cada pedido.
  2. categoria: Segmento do produto vendido (Fantasia, Acessório ou preenchido como Sem Categoria).
  3. quantidade: Volume de itens adquiridos (deve ser um número inteiro estritamente positivo).
  4. data_venda: Timestamp do registro da transação (formato esperado: ).

---

## Resultados Consolidados da Auditoria

Ao processar os 1.500 registros da base, obtiveram-se os seguintes resultados oficiais:

| Métrica Auditada | Quantidade | Regra / Significado |
| Linhas lidas | 1.500 | Total de registros importados do CSV. |
| Categorias vazias preenchidas | 18 | Substituídos por "Sem Categoria". |
| Categorias alteradas no texto | 131 | Exclamações (!) e espaços duplos removidos via Regex. |
| Canais padronizados | 45 | Grafias corrigidas para Mercado, Loja física ou Web. |
| Tamanhos não informados | 0 | Todas as dimensões físicas estavam preenchidas. |
| Quantidades inválidas | 7 | Valores inteiros menores ou iguais a zero. |
| Preços unitários inválidos | 12 | Registros com preço nulo ou ausente. |
| Pedidos com problemas numéricos | 19 | Pedidos distintos afetados (calculados via set() sem sobreposição). |
| Datas de venda inválidas | 4 | Strings que não atenderam ao formato strptime. |
| Total de pedidos cancelados | 109 | Registros Registros com status_pedido == "Cancelado". |

---

## Exploração de Dados e Duas Descobertas Estruturadas, pedidos registrados no sistema (incluindo compras canceladas e devolvidas), não representam receita financeira:

### Contagem por Canal de Venda (1.500 registros reconhecidos, 0 exclusões):
* Web: 666 pedidos (44,4%)
* Loja física: 551 pedidos (36,7%)
* Mercado: 283 pedidos (18,9%)

### Contagem por Período / Ano-Mês (1.496 válidos, 4 excluídos por data corrompida):
* 2024: 2024-08 (77) | 2024-09 (104) | 2024-10 (393) | 2024-11 (174)
* 2025: 2025-08 (62) | 2025-09 (94) | 2025-10 (410) | 2025-11 (182)

---

### Descoberta 1: Canal de Venda (Volume de Transações vs. Perfil de Volume)
* Evidência Numérica: O canal Web é o principal responsável pela frequência de compra, concentrando 44,4% dos pedidos (666 transações), seguido pela Loja física com 36,7% (551 transações) e Mercado com 18,9% (283 transações). No entanto, o canal Mercado apresenta uma média de 4,54 unidades por pedido, enquanto os canais Web e Loja física concentram vendas de menor volume unitário (1,97 unidades por pedido).
* Interpretação: A Web e a Loja física atendem ao consumidor final (compra de conveniência de fantasias unitárias). O canal Mercado, apesar de representar o menor número de pedidos, atua como canal distribuidor para compras corporativas ou revendedores locais.
* Limitação: A contagem é baseada em pedidos brutos cadastrados, incluindo transações canceladas ou devolvidas posteriormente, não refletindo faturamento financeiro ou margem de contribuição.

### Descoberta 2: Sazonalidade Anual (Efeito Halloween em Outubro)
* Evidência Numérica: Em ambos os anos analisados, o volume de pedidos em outubro quadruplica quando comparado ao início da campanha em agosto:
  * Em 2024: salto de 77 pedidos (agosto) para 393 pedidos (outubro) — alta de 410%.
  * Em 2025: salto de 62 pedidos (agosto) para 410 pedidos (outubro) — alta de 561%.
  Nos meses de novembro, a demanda arrefece abruptamente (174 em 2024 e 182 em 2025).
* Interpretação: A empresa opera sob forte dependência sazonal do feriado de 31 de outubro, demandando planejamento logístico de estoque e ampliação de servidores web concentrados exclusivamente nas primeiras três semanas de outubro.
* Limitação: A base cobre unicamente o quadrimestre de agosto a novembro em dois anos atípicos de campanha, impedindo a extrapolação do comportamento de vendas para o restante do ano.
