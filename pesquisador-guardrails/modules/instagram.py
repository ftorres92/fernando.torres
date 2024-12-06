from crewai import Agent, Task
import os

def create_instagram_agent(model_name):
    return Agent(
        role="Criar conteúdo para Postagens para Instagram",
        goal="Com base no texto escrito pelo agente anterior e salvo em post_linkedin.md, escreva posts engajadores e virais para o Instagram do escritório de advocacia, destacando seus serviços e expertise jurídica.",
        backstory="Você é um especialista em criar conteúdo criativo e viral para redes sociais. Atualmente trabalha para um escritório de advocacia, criando posts que capturam a atenção e geram alto engajamento.",
        verbose=True,
        memory=True,
        llm=model_name,
    )

def create_instagram_task(output_dir, agent):
    return Task(
        description=(
            "Com base no conteúdo salvo em post_linkedin.md, crie um post para o Instagram que destaque uma área de atuação do escritório de advocacia, focando em atrair clientes potenciais e viralizar. "
            "O conteúdo deve ser informativo, engajador e incluir uma chamada para ação."
        ),
        expected_output="Um post de Instagram com até 1500 caracteres, devidamente humanizado para criar uma maior conexão emocional, e hashtags ajustadas para SEO.",
        agent=agent,
        output_file=os.path.join(output_dir, "post_instagram.md"),
    )
