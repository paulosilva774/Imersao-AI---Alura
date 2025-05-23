# -*- coding: utf-8 -*-
"""OK_melhoriaRH

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1R5jteKJoXZFCTDECkU1HNTdksH69r3-d
"""

# Instalar Framework de agentes do Google e o pacote google-genai
# (Conforme o anexo, google-genai também é necessário)
!pip install -q google-genai google-adk

# Configura a API Key do Google Gemini
import os
from google.colab import userdata

os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')

# Configura o cliente da SDK do Gemini
from google import genai

client = genai.Client()

# Define os modelos a serem usados (conforme o arquivo anexo)
MODELO_RAPIDO = "gemini-2.0-flash"
MODELO_ROBUSTO = "gemini-2.0-flash" # Modelo mais robusto do anexo

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types  # Para criar conteúdos (Content e Part)
from datetime import date, datetime
import textwrap # Para formatar melhor a saída de texto
from IPython.display import display, Markdown, HTML # Para exibir a tabela formatada no Colab
import requests # Para fazer requisições HTTP (mantido para compatibilidade, mesmo não usado diretamente no fluxo principal do agente)
import warnings
import re
import pandas as pd

warnings.filterwarnings("ignore")

# Cria um serviço de sessão em memória (MOVIDO PARA FORA DA FUNÇÃO, INICIALIZADO APENAS UMA VEZ)
session_service = InMemorySessionService()

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
# (Tornada assíncrona e corrigida conforme o anexo)
async def call_agent(agent: Agent, message_text: str) -> str:
    # Cria uma nova sessão (você pode personalizar os IDs conforme necessário)
    session = await session_service.create_session(app_name=agent.name, user_id="user1")
    # Cria um Runner para o agente
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    # Cria o conteúdo da mensagem de entrada
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    # Itera assincronamente pelos eventos retornados durante a execução do agente
    async for event in runner.run_async(user_id="user1", session_id=session.id, new_message=content):
        if event.is_final_response():
          for part in event.content.parts:
            if part.text is not None:
              final_response += part.text
              final_response += "\n"
    return final_response

# Função auxiliar para exibir texto formatado em Markdown no Colab
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

##########################################
# --- Agente 1: Analisador de Nascimento --- #
##########################################
# Usando MODELO_RAPIDO conforme o anexo
async def agente_analisador(data_nascimento):
    analisador = Agent(
        name="agente_analisador",
        model=MODELO_RAPIDO,
        instruction="""
        Você é um analista de personalidade e propósito de vida com base na data de nascimento.
        Sua tarefa é fornecer análises profundas e precisas sobre a personalidade, padrões emocionais,
        caminhos de carreira e desafios pessoais com base na data de nascimento fornecida.
        Use a ferramenta de busca do Google (google_search) para obter informações relevantes e
        garantir que as análises sejam fundamentadas e úteis.
        """,
        description="Agente que analisa a personalidade e o propósito de vida com base na data de nascimento",
        tools=[google_search]
    )

    entrada_do_agente_analisador = f"""
    Data de Nascimento: {data_nascimento}

    Realize as seguintes análises:

    1. Decodificador de Personalidade pela Data de Nascimento
    “Com base na data de nascimento {data_nascimento}, descreva meus pontos fortes naturais, padrões emocionais e como me comporto em relacionamentos — que seja profundo, específico e psicologicamente preciso.”

    2. Roteiro da Infância
    “Usando a data de nascimento {data_nascimento}, escreva um perfil psicológico de como minha infância moldou minha personalidade, hábitos e tomada de decisões hoje — seja gentil, mas revelador.”

    3. Analisador de Propósito Profissional
    “Dada a data de nascimento {data_nascimento}, quais caminhos de carreira combinam com meus traços de personalidade, valores e talentos naturais? Sugira áreas, funções e ambientes de trabalho.”

    4. Detector de Auto-Sabotagem
    “Com base na data {data_nascimento}, quais são meus hábitos de auto-sabotagem mais prováveis e como eles aparecem no dia a dia? Dê soluções práticas com base na psicologia.”

    5. Mapa de Gatilhos Emocionais
    “Usando a data de nascimento {data_nascimento}, explique o que geralmente me desencadeia emocionalmente, como eu costumo reagir e como posso desenvolver resiliência emocional em torno desses padrões.”

    6. Escaneamento de Energia nos Relacionamentos
    “Com base na data de nascimento {data_nascimento}, descreva como eu dou e recebo amor, o que preciso de um parceiro e que tipo de pessoa eu naturalmente atraio.”
    """

    analises = await call_agent(analisador, entrada_do_agente_analisador)
    return analises

################################################
# --- Agente 2: Identificador de Melhorias --- #
################################################
# Usando MODELO_RAPIDO conforme o anexo
async def agente_melhorias(data_nascimento, analises_agente1):
    melhorias = Agent(
        name="agente_melhorias",
        model=MODELO_RAPIDO,
        instruction="""
        Você é um consultor de desenvolvimento pessoal. Sua tarefa é analisar as análises fornecidas
        pelo Agente 1 (analisador de nascimento) e identificar áreas de melhoria em cada uma das seis
        categorias. Seja específico e forneça sugestões práticas para o desenvolvimento pessoal.
        """,
        description="Agente que identifica pontos de melhoria nas análises do Agente 1",
        tools=[google_search]
    )

    entrada_do_agente_melhorias = f"""
    Data de Nascimento: {data_nascimento}
    Análises do Agente 1: {analises_agente1}

    Para cada uma das seis análises fornecidas pelo Agente 1, identifique áreas de melhoria e
    forneça sugestões práticas para o desenvolvimento pessoal.
    """

    pontos_de_melhoria = await call_agent(melhorias, entrada_do_agente_melhorias)
    return pontos_de_melhoria

######################################
# --- Agente 3: Buscador de Pessoas de Sucesso --- #
######################################
# Usando MODELO_ROBUSTO (assumindo que a versão 'flash-preview' mais avançada se alinha ao "robusto" do anexo)
async def agente_buscador_sucesso(data_nascimento):
    buscador_sucesso = Agent(
        name="agente_buscador_sucesso",
        model=MODELO_ROBUSTO, # Alterado de "gemini-2.5-flash-preview-04-17" para MODELO_ROBUSTO
        instruction="""
            Você é um pesquisador de pessoas de sucesso brasileiras. Sua tarefa é buscar na internet 5 homens e 5 mulheres
            que nasceram na mesma data fornecida e que alcançaram sucesso em suas áreas de atuação, e que sejam brasileiros.
            Monte uma tabela com as seguintes colunas: nome, profissão, no que a pessoa tem sucesso e site da informação.
            Ao realizar a busca no Google, certifique-se de incluir o termo "brasileiro" ou "brasileira" para garantir que os resultados sejam apenas de pessoas do Brasil.
            Use a ferramenta de busca do Google (google_search) para encontrar as informações e o site de onde tirou a informação.
            """,
        description="Agente que busca pessoas de sucesso nascidas na mesma data",
        tools=[google_search]
    )

    entrada_do_agente_buscador_sucesso = f"""
    Data de Nascimento: {data_nascimento}

    Busque na internet 5 homens e 5 mulheres que nasceram na mesma data e que alcançaram sucesso
    em suas áreas de atuação e que sejam brasileiros. Monte uma tabela com as seguintes colunas:
    nome, profissão, no que a pessoa tem sucesso e site da informação. Ao realizar a busca no Google, certifique-se de incluir o termo "brasileiro" ou "brasileira" para garantir que os resultados sejam apenas de pessoas do Brasil. Seja claro e objetivo
    """

    tabela_sucesso = await call_agent(buscador_sucesso, entrada_do_agente_buscador_sucesso)

    # Extract data for DataFrame
    # Note: This parsing relies heavily on the model's output format.
    # It might need adjustment if the model output varies.
    data_lines = tabela_sucesso.strip().split('\n')

    # Try to find the header line to start parsing from there
    header_index = -1
    for i, line in enumerate(data_lines):
        if "Nome" in line and "Profissão" in line and "Sucesso" in line and "Site da Informação" in line:
            header_index = i
            break

    data = []
    if header_index != -1:
        # Assuming the next line after header is the separator, and then data starts
        # A more robust parsing would involve regex or a more structured output from the agent
        for line in data_lines[header_index+2:]: # Skip header and separator line
            # Ensure line is not empty and contains expected delimiters
            if line.strip() and '|' in line:
                values = re.split(r"\|", line.strip())
                # Remove empty strings from split and filter out the first/last empty parts
                cleaned_values = [v.strip() for v in values if v.strip()]

                # Expecting 4 columns
                if len(cleaned_values) >= 4:
                    nome, profissao, sucesso, site = cleaned_values[:4]
                    data.append([nome, profissao, sucesso, site])
                elif len(cleaned_values) > 0: # Handle cases where output might be truncated
                    # Attempt to salvage data even if not all columns are present
                    data.append(cleaned_values + [''] * (4 - len(cleaned_values))) # Pad with empty strings

    df = pd.DataFrame(data, columns=["Nome", "Profissão", "Sucesso", "Site da Informação"])
    html_table = df.to_html(index=False)

    return html_table

##########################################
# --- Agente 4: Gerador de Relatório Final --- #
##########################################
# Usando MODELO_RAPIDO conforme o anexo
async def agente_relatorio_final(data_nascimento, analises, melhorias, tabela_sucesso):
    relatorio = Agent(
        name="agente_relatorio",
        model=MODELO_RAPIDO,
        instruction="""
        Você é um gerador de relatórios finais. Sua tarefa é combinar as análises do Agente 1,
        os pontos de melhoria do Agente 2 e a tabela de pessoas de sucesso do Agente 3 em um
        relatório final otimista e motivador. Conclua o relatório com uma mensagem de incentivo.
        """,
        description="Agente que gera o relatório final",
        #tools=[google_search] # Remova a ferramenta de busca, pois não é necessária aqui
    )

    entrada_do_agente_relatorio = f"""
    Data de Nascimento: {data_nascimento}
    Análises do Agente 1: {analises}
    Pontos de Melhoria do Agente 2: {melhorias}
    Tabela de Pessoas de Sucesso do Agente 3: {tabela_sucesso}

    Combine as informações acima em um relatório final otimista e motivador.
    Conclua o relatório com uma mensagem de incentivo.
    """

    relatorio_final = await call_agent(relatorio, entrada_do_agente_relatorio)
    return relatorio_final

##########################################
# --- Execução do Sistema de Agentes --- #
##########################################

# A função principal é agora assíncrona para permitir o uso de 'await'
async def run_analysis_system():
    print("🚀 Iniciando o Sistema de Análise de Personalidade e Propósito de Vida 🚀")

    # --- Obter a Data de Nascimento do Usuário ---
    while True:
        data_nascimento = input("❓ Por favor, digite sua DATA DE NASCIMENTO no formato DD/MM/AAAA: ")
        try:
            datetime.strptime(data_nascimento, '%d/%m/%Y')
            break  # Sai do loop se a data estiver no formato correto
        except ValueError:
            print("Formato de data incorreto. Use o formato DD/MM/AAAA.")

    # Inserir lógica do sistema de agentes
    if not data_nascimento:
        print("Você esqueceu de digitar a data de nascimento!")
    else:
        print(f"Maravilha! Vamos analisar sua personalidade e propósito de vida com base em {data_nascimento}")

        print("\n--- 📝 Executando o Agente 1 (Analisador de Nascimento) ---\n")
        analises_agente1 = await agente_analisador(data_nascimento)
        print("\n--- ✅ Resultado do Agente 1 (Analisador de Nascimento) ---\n")
        display(to_markdown(analises_agente1))
        print("--------------------------------------------------------------")

        print("\n--- 📝 Executando o Agente 2 (Identificador de Melhorias) ---\n")
        pontos_de_melhoria = await agente_melhorias(data_nascimento, analises_agente1)
        print("\n--- ✅ Resultado do Agente 2 (Identificador de Melhorias) ---\n")
        display(to_markdown(pontos_de_melhoria))
        print("--------------------------------------------------------------")

        print("\n--- 📝 Executando o Agente 3 (Buscador de Pessoas de Sucesso) ---\n")
        tabela_sucesso = await agente_buscador_sucesso(data_nascimento)
        print("\n--- ✅ Resultado do Agente 3 (Buscador de Pessoas de Sucesso) ---\n")
        display(HTML(tabela_sucesso))
        print("--------------------------------------------------------------")

        print("\n--- 📝 Executando o Agente 4 (Gerador de Relatório Final) ---\n")
        relatorio_final = await agente_relatorio_final(data_nascimento, analises_agente1, pontos_de_melhoria, tabela_sucesso)
        print("\n--- ✅ Resultado do Agente 4 (Gerador de Relatório Final) ---\n")
        display(to_markdown(relatorio_final))
        print("--------------------------------------------------------------")

# Executa a função principal assíncrona
# Em ambientes como Jupyter/Colab, 'await' no nível superior de uma célula funciona.
# Para scripts Python puros, você usaria asyncio.run(run_analysis_system()).
await run_analysis_system()