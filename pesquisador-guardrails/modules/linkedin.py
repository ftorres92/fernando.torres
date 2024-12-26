from crewai import Agent, Task
import os

def combine_content_files(output_dir):
    """Combina o conteúdo dos arquivos em um único arquivo"""
    combined_content = ""
    combined_file = os.path.join(output_dir, "combined_content.md")
    
    try:
        # Ler noticias.md
        noticias_path = os.path.join(output_dir, "noticias_raw.md")
        if os.path.exists(noticias_path):
            with open(noticias_path, 'r', encoding='utf-8') as f:
                combined_content += "### CONTEÚDO DAS NOTÍCIAS:\n" + f.read() + "\n\n"
                
        # Ler scrap.md
        scrap_path = os.path.join(output_dir, "scrap.md")
        if os.path.exists(scrap_path):
            with open(scrap_path, 'r', encoding='utf-8') as f:
                combined_content += "### CONTEÚDO DETALHADO:\n" + f.read()
        
        # Salvar conteúdo combinado
        if combined_content:
            with open(combined_file, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            return combined_file
                
    except Exception as e:
        print(f"Erro ao combinar arquivos: {e}")
        return None

def create_linkedin_agent(tema, model_name):
    return Agent(
        role=f"Criar um texto jurídico original baseado em múltiplas fontes",
        goal=f"Escrever um artigo único e original sobre {tema}, sintetizando diferentes fontes e destacando insights jurídicos relevantes",
        verbose=True,
        memory=True,
        backstory="""Você é um advogado renomado e autor de artigos jurídicos influentes. 
        Sua especialidade é criar conteúdo original que sintetiza diferentes fontes de informação,
        oferecendo uma perspectiva única e valiosa sobre temas jurídicos complexos.
        Seu texto deve ser completamente original, evitando repetir exatamente o que está nas fontes.""",
        llm=model_name,
    )

def create_linkedin_task(tema, output_dir, agent):
    # Combinar arquivos
    combined_file = combine_content_files(output_dir)
    
    if not combined_file or not os.path.exists(combined_file):
        raise ValueError("Não foi possível criar o arquivo combinado de conteúdo")

    # Ler o conteúdo combinado
    with open(combined_file, 'r', encoding='utf-8') as f:
        content = f.read()

    return Task(
        description=(
            f"Analise o seguinte conteúdo e crie um artigo original sobre {tema}:\n\n{content}\n\n"
        ),
        expected_output=(
            "Um artigo jurídico original que sintetize as fontes e ofereça insights únicos, mas sem inventar qualquer informação"
        ),
        agent=agent,
        output_file=os.path.join(output_dir, "post_linkedin.md"),
    )
