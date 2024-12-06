from crewai import Agent, Task
from crewai_tools import SerperDevTool
import os

def create_pesquisador_agent(tema, model_name):
    search_tool = SerperDevTool(n_results=10)
    return Agent(
        role=f"pesquisar as principais notícias sobre {tema}",
        goal=f"Encontrar e organizar as 10 principais notícias sobre o {tema}",
        backstory="""Você é um investigador incansável, 
        com um faro apurado para detectar as notícias mais relevantes e impactantes na vasta paisagem da internet sobre o mundo jurídico. 
        Como Pesquisador de Notícias, você utiliza suas habilidades para vasculhar a web sobre o tema e encontrar as 10 principais notícias sobre o tema.
        Sua pesquisa é focada em sites dados confiáveis, garantindo que seus relatórios sejam uma referência de qualidade e precisão. 
        Sua dedicação à verdade e à clareza faz de você uma peça-chave na formação das estratégias de comunicação e na tomada de decisões informadas.""",
        memory=True,
        verbose=True,
        tools=[search_tool],
        llm=model_name,
    )

def create_pesquisa_task(tema, output_dir, agent):
    search_tool = agent.tools[0]
    raw_file = os.path.join(output_dir, "noticias_raw.md")

    return Task(
        description=(
            f"Pesquisar informações detalhadas e relevantes sobre o {tema}, sempre fornecendo os respectivos links. "
            "Concentre-se em aspectos únicos e dados importantes que podem enriquecer o texto, como leis, doutrinas e jurisprudência sobre o tema. "
            "Todo o texto deve estar em Português Brasil."
        ),
        expected_output=f"Um documento estruturado com as 10 principais informações e dados sobre o {tema}, juntamente com os seus respectivos links.",
        tools=[search_tool],
        output_file=raw_file,
        agent=agent,
    )

