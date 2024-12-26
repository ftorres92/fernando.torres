import os
import streamlit as st
from dotenv import load_dotenv
from modules.pesquisador import create_pesquisador_agent, create_pesquisa_task
from modules.scraper import create_scraper_agent, create_scrap_task
from modules.linkedin import create_linkedin_agent, create_linkedin_task
from modules.instagram import create_instagram_agent, create_instagram_task
from crewai import Crew, Process
from utils.guardrails import validate_output_with_guardrails, filter_valid_links
from time import sleep
import sys


# Carregar variáveis de ambiente
load_dotenv()

# Constantes
output_dir = "Docscriados"
model_name = "gpt-4o-mini"
disallowed_domains = ["www.youtube.com", "www.jusbrasil.com", "gov.br", "www.mpf.mp.br"]  # Domínios proibidos

# Interface do Streamlit
st.title("Pesquisa Direito - JuristIA (Beta)")
st.subheader("Agentes de Inteligência Artificial Para Criação Automatizada de Conteúdo Jurídico.")
tema = st.text_input("Sobre qual tema gostaria de pesquisar?")

if "completed_tasks" not in st.session_state:
    st.session_state.completed_tasks = set()

# Botão para iniciar
if st.button("Iniciar Pesquisa e Criar Conteúdo"):
    if tema:
        status_placeholder = st.empty()  # Placeholder para mensagens temporárias
        try:
            with st.spinner("🤖 Os agentes estão trabalhando..."):
                # Criar Agentes
                pesquisador = create_pesquisador_agent(tema, model_name)
                scraper = create_scraper_agent(tema, model_name)
                linkedin = create_linkedin_agent(tema, model_name)
                instagram = create_instagram_agent(model_name)

                # Etapa 1: Pesquisador e Scraper
                raw_file = os.path.join(output_dir, "noticias_raw.md")
                filtered_file = os.path.join(output_dir, "noticias_filtradas.md")

                if "pesquisador_e_scraper" not in st.session_state.completed_tasks:
                    status_placeholder.info("🔍 Pesquisador iniciando a busca de links...")

                    # Criar tarefa do pesquisador
                    tarefa_pesquisa = create_pesquisa_task(tema, output_dir, pesquisador)

                    # Criar Crew para Pesquisador e Scraper
                    pesquisa_scrap_crew = Crew(
                        agents=[pesquisador, scraper],
                        tasks=[tarefa_pesquisa],
                        process=Process.sequential,
                    )

                    # Executar Pesquisador
                    pesquisa_scrap_crew.kickoff()

                    # Validar links extraídos
                    status_placeholder.info("✅ Validando os links extraídos pelo Pesquisador...")
                    validated_noticias = validate_output_with_guardrails(raw_file, "Pesquisador")
                    sleep(1)

                    if validated_noticias:
                        with st.expander("Notícias Encontradas"):
                            st.markdown(validated_noticias)

                        # Filtrar links proibidos
                        status_placeholder.info("🛠️ Filtrando links proibidos...")
                        filtered_links = filter_valid_links(validated_noticias.split('\n'), disallowed_domains)
                        if filtered_links:
                            with open(filtered_file, 'w') as f:
                                f.write('\n'.join(filtered_links))
                        else:
                            st.warning("⚠️ Nenhum link permitido foi encontrado após o filtro.")

                        # Adicionar tarefa do Scraper após validação
                        if filtered_links:
                            status_placeholder.info("🚀 Scraper iniciando o processamento dos links filtrados...")
                            tarefa_scrap = create_scrap_task(tema, output_dir, scraper, filtered_links, disallowed_domains)

                            pesquisa_scrap_crew.tasks.append(tarefa_scrap)

                            # Executar Scraper
                            pesquisa_scrap_crew.kickoff()

                            # Validar e exibir resultado do Scraper
                            validated_scrap = validate_output_with_guardrails(
                                os.path.join(output_dir, "scrap.md"), "Scraper"
                            )
                            if validated_scrap:
                                with st.expander(f"Conteúdo sobre o {tema}"):
                                    st.markdown(validated_scrap)

                    # Marcar Pesquisador e Scraper como concluídos
                    st.session_state.completed_tasks.add("pesquisador_e_scraper")

                # Etapa 2: Redes Sociais (LinkedIn e Instagram)
                if "redes_sociais" not in st.session_state.completed_tasks:
                    status_placeholder.info("📲 O terceiro Agente está preparando a postagem para Redes Sociais")
                    tarefa_linkedin = create_linkedin_task(tema, output_dir, linkedin)
                    tarefa_instagram = create_instagram_task(output_dir, instagram)

                    # Criar um novo Crew apenas para redes sociais
                    social_crew = Crew(
                        agents=[linkedin, instagram],
                        tasks=[tarefa_linkedin, tarefa_instagram],
                        process=Process.sequential,
                    )
                    social_crew.kickoff()  # Executar apenas tarefas das redes sociais

                    # Validar LinkedIn
                    validated_linkedin = validate_output_with_guardrails(
                        os.path.join(output_dir, "post_linkedin.md"), "LinkedIn"
                    )
                    if validated_linkedin:
                        with st.expander("Conteúdo para LinkedIn"):
                            st.markdown(validated_linkedin)

                    # Exibir conteúdo do Instagram
                    with st.expander("Conteúdo para Instagram"):
                        try:
                            with open(os.path.join(output_dir, 'post_instagram.md'), 'r') as f:
                                st.markdown(f.read())
                        except FileNotFoundError:
                            st.error("❌ Arquivo de Instagram não encontrado!")

                    # Marcar redes sociais como concluídas
                    st.session_state.completed_tasks.add("redes_sociais")

                status_placeholder.empty()  # Finalizar interface limpa

        except Exception as e:
            st.error(f"❌ Ocorreu um erro: {e}")

sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

# Agora tudo será exibido novamente no terminal
print("Saída restaurada para o terminal.")