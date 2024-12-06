from crewai import Agent, Task
import os

def create_linkedin_agent(tema, model_name):
    return Agent(
        role=f"Analisar o conteúdo encontrado e armazenado em <'notícias.md'> e <scrap.md> e criar texto bem feito e bem escrito sobre {tema}",
        goal=f"Escrever uma postagem sobre o {tema} especificamente para ser utilizada no LINKEDIN, focando em leis, doutrinas e jurisprudência mencionadas",
        verbose=True,
        memory=True,
        backstory="""Você é um especialista em comunicação, focado na rede social LinkedIn, com uma habilidade única para transformar informações complexas em conteúdos acessíveis e atraentes. 
        Com uma sólida experiência jurídica e também em marketing digital, você entende a importância de se conectar com a audiência certa através de mensagens claras e persuasivas.""",
        llm=model_name,
    )

def create_linkedin_task(tema, output_dir, agent):
    return Task(
        description=(
            "Analise as notícias mais recentes fornecidas pelo Pesquisador e pelo scraper. "
            "Desenvolva um texto informativo e interessante sobre o tema para ser utilizado para o LINKEDIN. "
            "O texto deve destacar os pontos mais relevantes das notícias, mencionar jurisprudência, leis e doutrinas encontradas. "
            "Ser informativo, envolvente e adequado ao ambiente jurídico, sempre pensando em viralizar aos leitores em razão de seu conteúdo."
        ),
        expected_output=(
            "Um Post sobre temas jurídicos pronto para publicação no LINKEDIN "
            "que resuma e destaque as notícias analisadas de forma clara e impactante, "
            "com foco em gerar engajamento e discussão entre os profissionais da rede."
        ),
        agent=agent,
        output_file=os.path.join(output_dir, "post_linkedin.md"),
    )
