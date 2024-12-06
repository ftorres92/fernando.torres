from crewai import Agent, Task
from crewai_tools import ScrapeWebsiteTool
import os

def create_scraper_agent(tema, model_name):
    scrap_tool = ScrapeWebsiteTool()
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

def create_scrap_task(tema, output_dir, agent, filtered_links_file):
    """
    Cria uma tarefa para o agente Scraper com links já filtrados.

    Args:
        tema (str): Tema da pesquisa.
        output_dir (str): Diretório de saída.
        agent (Agent): Agente responsável pela tarefa.
        filtered_links_file (str): Caminho para o arquivo com links filtrados.

    Returns:
        Task: Objeto de tarefa configurado.
    """
    try:
        # Garantir a leitura do arquivo de links filtrados
        with open(filtered_links_file, 'r') as f:
            filtered_links = [line.strip() for line in f.readlines() if line.strip()]

        # Verificar se há links no arquivo
        if not filtered_links:
            raise ValueError(f"⚠️ O arquivo {filtered_links_file} não contém links válidos.")

        # Criar a tarefa usando os links validados
        return Task(
            description=(
                f"Usar os links filtrados no arquivo {filtered_links_file} para compilar informações jurídicas "
                f"relevantes sobre o tema {tema}."
            ),
            expected_output=f"Texto completo sobre {tema} com links válidos extraídos dos sites mencionados.",
            tools=agent.tools,
            inputs={"links": filtered_links},  # Passar links como entrada
            output_file=os.path.join(output_dir, "scrap.md"),
            agent=agent,
        )
    except FileNotFoundError:
        raise FileNotFoundError(f"❌ O arquivo {filtered_links_file} não foi encontrado!")
    except ValueError as e:
        print(f"⚠️ {e}")
        return None
