from datetime import datetime
import pandas as pd
import re

# Leitura e extruturação com pandas, garantindo que os dados entrem como texto bruto e extrai para registros estruturados nativos.
# dtype=str e keep_default_na=False garantem ingestão como texto bruto.
# Impedindo que o Pandas converta strings vazias em NaN ou force tipos numéricos, antes das validações manuais via condicionais.
def carregar_dados(halloween_vendas: str) -> list[dict]: 
    df = pd.read_csv(halloween_vendas, dtype=str, keep_default_na=False) 
    return df.to_dict(orient='records') 

# Limpeza de strings com metodos nativos e regex
def padronizar_categoria(texto: str) -> str:
    limpo = texto.strip().lower()
    limpo = re.sub(r"[^a-z ]", "", limpo) # re.sub para remover caracteres especiais, mantendo apenas letras e espaços
    limpo = re.sub(r"\s+", " ", limpo).strip()
    return limpo

# Padroniza de canais de venda Para os padroes oficiais
def padronizar_canal(texto: str) -> str | None:
    canal = texto.strip().lower()
    if canal == "mercado":
        return "Mercado"
    elif canal in ["loja física", "loja fisica"]:
        return "Loja física"
    elif canal == "web":
        return "Web"
    else:
        return None

# Tratando nulos com If e Else:
def tratar_categoria(texto_limpo: str) -> str: # preenche categorias vazias com "Sem Categoria"
    if texto_limpo == "" or texto_limpo is None:
        return "Sem Categoria"
    else:
        return texto_limpo

# tratando dimensões fisicas
def tratar_dimensao_fisica(tamanho: str) -> str: # Trata e valida a dimensão física/tamanho do produto (ex.: P, M, G, Unico), se estiver vazio é marcado como "Não Informado" sem inventar medidas.
    tamanho_limpo = tamanho.strip()
    if tamanho_limpo == "":
        return "não informado"
    else:
        return tamanho_limpo

# Verifica se a quantidade é um número inteiro válido e positivo (> 0). Pedidos com quantidade zero ou negativa representam inconsistência de registro.
def validar_quantidade(texto: str) -> bool: 
    try:
        qtd = int(texto)
        if qtd > 0:
            return True
        else:
            return False
    except ValueError: 
        return False

# Valida se o preço unitário está presente e não é negativo (>= 0.0)
def validar_preco(texto: str) -> bool:
    preco_limpo = texto.strip()
    if preco_limpo == "":
        return False
    try:
        valor = float(preco_limpo)
        if valor >= 0.0:
            return True
        else:
            return False
    except ValueError:
        return False

# Converte a string 'data_venda' usando datetime.strptime no padrão 'AAAA-MM-DD HH:MM:SS'
# O try/except captura datas corrompidas retornando None, evitando a interrupção do programa e impedindo a substituição indevida pela data atual.
def converter_data_venda(texto: str) -> datetime | None:
    try:
        return datetime.strptime(texto.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    
# Pipeline de processamento e contagem
def processar_pedidos(registros: list[dict]):  # Contadores de Strings e nulos
    categorias_vazias_preenchidas = 0
    categorias_alteradas = 0
    canais_padronizados = 0
    dimensoes_nao_informadas = 0

    # Contadores Numericos e Datas
    quantidades_invalidas = 0
    precos_invalidos = 0
    datas_invalidas = 0
    pedidos_com_problema_numerico = set()  # O set armazena IDs únicos de pedidos com falha em quantidade ou preço, evitando dupla contagem caso um pedido tenha múltiplos erros numéricos.

    # Separação dos registros da Regra de Negócio
    pedidos_sem_entrega_cancelados = []
    pedidos_sem_entrega_outros = []
    total_cancelados = 0

    # Agrupamentos
    pedidos_por_canal = {"web": 0, "loja física": 0, "mercado": 0}
    pedidos_por_ano_mes = {}

    for registro in registros:
        pid = registro["pedido_id"]

        # Tratamento de Categorias com regex e if/else
        categoria_original = registro["categoria"]
        categoria_limpa = padronizar_categoria(categoria_original)
        categoria_final = tratar_categoria(categoria_limpa)

        if categoria_original.strip() == "":
            categorias_vazias_preenchidas += 1
        elif categoria_original != categoria_limpa and ( "!" in categoria_original or " " in categoria_original):
            categorias_alteradas += 1

        # Tratamento da dimensão física
        dimensao = tratar_dimensao_fisica(registro.get("tamanho", ""))  # Usando get para evitar KeyError
        if dimensao == "não informado":
            dimensoes_nao_informadas += 1

        # Padronização de canal
        canal_original = registro["canal_venda"]
        canal_padronizado = padronizar_canal(canal_original)
        if canal_padronizado is not None:
            pedidos_por_canal[canal_padronizado.lower()] += 1
            if canal_original != canal_padronizado:
                canais_padronizados += 1

        # Validação numérica
        if not validar_quantidade(registro["quantidade"]):
            quantidades_invalidas += 1
            pedidos_com_problema_numerico.add(pid)

        if not validar_preco(registro["preco_unitario"]):
            precos_invalidos += 1
            pedidos_com_problema_numerico.add(pid)

        # Validação de data
        dt = converter_data_venda(registro["data_venda"])
        if dt is not None:
            chave_ano_mes = dt.strftime("%Y-%m")
            if chave_ano_mes not in pedidos_por_ano_mes:
                pedidos_por_ano_mes[chave_ano_mes] = 1
            else:
                pedidos_por_ano_mes[chave_ano_mes] += 1
        else:
            datas_invalidas += 1

        # Separação de pedidos cancelados e outros, Investigação da Regra de Negócio: data_entrega x Cancelado
        status = registro["status_pedido"].strip()
        if registro["data_entrega"].strip() == "":
            if status.lower() == "cancelado":
                pedidos_sem_entrega_cancelados.append(registro)
            else:
                pedidos_sem_entrega_outros.append(registro)

        if status.lower() == "cancelado":
            total_cancelados += 1
    
    # Regra de integridade: registros inconsistentes são isolados e contabilizados, sem imputação (média/mediana), preservando a fidelidade da auditoria.
    return {
    "total_lidos": len(registros),
    "categorias_vazias": categorias_vazias_preenchidas,
    "categorias_alteradas": categorias_alteradas,
    "canais_padronizados": canais_padronizados, 
    "dimensoes_nao_informadas": dimensoes_nao_informadas,
    "quantidades_invalidas": quantidades_invalidas,
    "precos_invalidos": precos_invalidos,
    "pedidos_com_problema_numerico": pedidos_com_problema_numerico,
    "datas_invalidas": datas_invalidas,
    "total_cancelados": total_cancelados,
    "pedidos_sem_entrega_cancelados": pedidos_sem_entrega_cancelados,
    "pedidos_sem_entrega_outros": pedidos_sem_entrega_outros, 
    "exemplos_contraexemplos": pedidos_sem_entrega_outros[:3], # Retorna apenas os 3 primeiros exemplos de pedidos sem entrega e não cancelados
    "pedidos_por_canal": pedidos_por_canal,
    "pedidos_por_ano_mes": dict(sorted(pedidos_por_ano_mes.items()))  # Ordena por ano e mês
}
    # Apresenta os resultados consolidados da auditoria no terminal
def exibir_relatorio(res: dict):
    print("=" * 70) # Separador visual
    print("Relatório de Avaliação Oficial - Festa em Cena")
    print("=" * 70)
    print(f"Total de registros lidos: {res['total_lidos']}")
    print(f"Total de categorias vazias preenchidas: {res['categorias_vazias']}")
    print(f"Total de categorias alteradas: {res['categorias_alteradas']}")
    print(f"Total de canais padronizados: {res['canais_padronizados']}")
    print(f"Total tamanhos não informados: {res['dimensoes_nao_informadas']}")
    print(f"Quantidades menores ou iguais a zero: {res['quantidades_invalidas']}")
    print(f"Preços unitários vazios ou inválidos: {res['precos_invalidos']}")
    print("Pedidos com problemas numéricos, sem sobreposição:" f" {len(res['pedidos_com_problema_numerico'])}")
    print(f"Datas de venda inválidas: {res['datas_invalidas']}")
    print(f"Total geral de pedidos cancelados: {res['total_cancelados']}")
    print("Pedidos sem entrega e cancelados:" f" {len(res['pedidos_sem_entrega_cancelados'])}")
    print("Pedidos sem entrega e outros Status (Contraexemplos):" f" {len(res['pedidos_sem_entrega_outros'])}")

    # Conclusão lógica sobre a hipótese de entrega
    hipotese = "FALSA" if len(res["pedidos_sem_entrega_outros"]) > 0 else "VERDADEIRA"
    print(f"Conclusão da Hipótese: {hipotese}")
    print("Exemplos de contraexemplos separados:")
    for exemplo in res['exemplos_contraexemplos']:
        print(f" * Pedido #{exemplo['pedido_id']} | Status: {exemplo['status_pedido']} |" f" Produto: {exemplo['produto']} | Tamanho: {exemplo['tamanho']}")
    
    print("\n[Exploração por Canal de Venda]")
    for canal, qtd in res['pedidos_por_canal'].items():
        print(f" - {canal:12}: {qtd:4d} pedidos")

    print("\n[Exploração por Ano e Mês]")
    for ano_mes, qtd in res['pedidos_por_ano_mes'].items():
        print(f" - {ano_mes}: {qtd:4d} pedidos")
    print("=" * 70)

# Ponto de entrada do script
if __name__ == "__main__":
    dados = carregar_dados("halloween_vendas.csv")
    metricas = processar_pedidos(dados)
    exibir_relatorio(metricas)