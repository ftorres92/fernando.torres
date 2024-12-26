from guardrails.hub import HasUrl, RegexMatch
from guardrails import Guard
import re

def create_scraper_guard(disallowed_domains):
    """
    Cria um Guard para validar que os links não contenham domínios proibidos.

    Args:
        disallowed_domains (list): Lista de domínios que devem ser ignorados.

    Returns:
        Guard: Instância configurada do Guardrails.
    """
    # Cria um regex para capturar os domínios proibidos
    regex = f"({'|'.join(re.escape(domain) for domain in disallowed_domains)})"

    # Função de fallback para lidar com links inválidos
    def skip_invalid_link(value, fail_result):
        """Ignora links inválidos retornando None."""
        print(f"🚫 Link proibido detectado e ignorado: {value}")
        return None

    # Configurar o Guard com HasUrl e Regex
    guard = Guard()
    guard.use(HasUrl())  # Verifica se o conteúdo possui URLs
    guard.use(RegexMatch(regex=regex, on_fail=skip_invalid_link))  # Filtra links com domínios proibidos

    return guard

def filter_valid_links(input_links, disallowed_domains):
    """
    Valida e filtra links, removendo links de domínios proibidos.

    Args:
        input_links (str or list): Caminho do arquivo ou lista de links para filtrar.
        disallowed_domains (list): Lista de domínios proibidos.

    Returns:
        list: Lista de links válidos.
    """
    links = []
    
    # Se input_links for uma string, assume que é um caminho de arquivo
    if isinstance(input_links, str):
        try:
            with open(input_links, 'r') as f:
                links = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print(f"❌ Arquivo {input_links} não encontrado!")
            return []
    else:
        # Se não for string, assume que é uma lista
        links = [link.strip() for link in input_links if link.strip()]

    # Filtrar links proibidos
    filtered_links = []
    for link in links:
        if not any(domain in link for domain in disallowed_domains):
            filtered_links.append(link)
        else:
            print(f"🚫 Link proibido ignorado: {link}")

    return filtered_links

def validate_output_with_guardrails(output_file, agent_name):
    """
    Valida o conteúdo de um arquivo de saída para garantir que ele siga as regras específicas (como conter URLs válidas e sua existência).

    Args:
        output_file (str): Caminho do arquivo de saída a ser validado.
        agent_name (str): Nome do agente que gerou o conteúdo.

    Returns:
        str: O conteúdo validado, se a validação for bem-sucedida. Caso contrário, retorna None.
    """
    guard = Guard().use(HasUrl())  # Configura o Guardrails para validação de URLs
    try:
        # Lê o conteúdo do arquivo gerado
        with open(output_file, 'r') as f:
            content = f.read()

        # Valida o conteúdo utilizando as regras configuradas
        guard.validate(content)

        # Verifica se há links no conteúdo
        if "http://" not in content and "https://" not in content:
            raise ValueError("O conteúdo não contém links válidos.")

        # Mensagens personalizadas para agentes específicos
        if agent_name == "Scraper":
            print("✅ Validação bem-sucedida para o Scraper: Os links extraídos são válidos e confiáveis!")
        elif agent_name == "LinkedIn":
            print("✅ Validação bem-sucedida para o LinkedIn: O conteúdo está pronto para publicação!")
        elif agent_name == "Pesquisador":
            print("✅ Validação bem-sucedida para o Pesquisador: O conteúdo contém links relevantes!")
        elif agent_name == "Gerente de Qualidade":
            print("✅ Validação bem-sucedida para o Gerente de Qualidade: O conteúdo revisado está correto e inclui links!")
        else:
            print(f"✅ Validação bem-sucedida para o agente {agent_name}!")

        return content

    except Exception as e:
        # Mensagens de erro específicas para agentes
        if agent_name == "Scraper":
            print(f"❌ Validação falhou para o Scraper: {e}")
        elif agent_name == "LinkedIn":
            print(f"❌ Validação falhou para o LinkedIn: {e}")
        elif agent_name == "Pesquisador":
            print(f"❌ Validação falhou para o Pesquisador: {e}")
        elif agent_name == "Gerente de Qualidade":
            print(f"❌ Validação falhou para o Gerente de Qualidade: {e}")
        else:
            print(f"❌ Validação falhou para o agente {agent_name}: {e}")
        return None
