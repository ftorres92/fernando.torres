from crewai import Agent, Task
from crewai_tools import ScrapeWebsiteTool
from typing import List, Optional
import os
from utils.guardrails import filter_valid_links
from pydantic import Field

class SafeScrapeWebsiteTool(ScrapeWebsiteTool):
    disallowed_domains: List[str] = Field(default_factory=list)

    def __init__(self, disallowed_domains: Optional[List[str]] = None):
        super().__init__()
        self.disallowed_domains = disallowed_domains or []

    def _execute(self, url: str) -> str:
        if isinstance(url, dict):
            url = url.get("website_url", "")
            
        if any(domain in url for domain in self.disallowed_domains):
            print(f"🚫 Tentativa de acessar domínio proibido bloqueada: {url}")
            return None
            
        return super()._execute(url)

def create_scraper_agent(tema, model_name):
    scrap_tool = SafeScrapeWebsiteTool(disallowed_domains=["www.youtube.com", "www.jusbrasil.com", "gov.br"])
    return Agent(
        role="Preparar um texto com as informações extraídas de cinco sites mencionados em um noticias_filtradas.md. Sites ilegíveis devem ser ignorados.",
        goal="Fazer um jurídico, perfeitamente escrito e bem estruturado com base nas informações informações encontradas nos sites mencionados pelo agente pesquisador sobre o tema, extraindo as principais informações para fins jurídicos, como leis, jurisprudência e doutrinas mencionados.",
        backstory="""Você é um profundo conhecedor do direito brasileiro. Sua principal qualidade é conseguir compilar informações de um site para sempre fornecer o máximo de informações para os outros agentes. 
        O texto deve ser o mais completo possível e preparado para fornecer informações relevantes e corretas sobre o tema aos demais agentes. Ignore sites ilegíveis.
        """,
        verbose=True,
        tools=[scrap_tool],
        llm=model_name,
        max_inter=5,
    )

# modules/scraper.py

def create_scrap_task(tema, output_dir, agent, filtered_links, disallowed_domains):
    """
    Cria uma tarefa para o agente Scraper com links já filtrados.

    Args:
        tema (str): Tema da pesquisa.
        output_dir (str): Diretório de saída.
        agent (Agent): Agente responsável pela tarefa.
        filtered_links (list): Lista de links filtrados.
        disallowed_domains (list): Lista de domínios proibidos.

    Returns:
        Task: Objeto de tarefa configurado.
    """
    try:
        # Filtrar links proibidos
        filtered_links = filter_valid_links(filtered_links, disallowed_domains)

        # Verificar se há links válidos após o filtro
        if not filtered_links:
            raise ValueError(f"⚠️ A lista de links fornecida não contém links válidos após o filtro.")

        # Criar a tarefa usando os links validados
        return Task(
            description=(
                f"Usar os links filtrados para compilar informações jurídicas "
                f"relevantes sobre o tema {tema}."
            ),
            expected_output=f"Texto completo sobre {tema} com links válidos extraídos dos sites mencionados.",
            tools=agent.tools,
            inputs={"links": filtered_links},  # Passar links como entrada
            output_file=os.path.join(output_dir, "scrap.md"),
            agent=agent,
        )
    except ValueError as e:
        print(f"⚠️ {e}")
        return None