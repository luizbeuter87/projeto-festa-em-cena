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
    
# Ponto de entrada do script
if __name__ == "__main__":
    dados = carregar_dados("halloween_vendas.csv")
    print(f"Total lido na Branch 1: {len(dados)} linhas.")
    print("Exemplo categoria limpa:", padronizar_categoria("Fantasia de Bruxa!!"))