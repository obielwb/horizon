# Horizon: Descoberta de Startups de IA para NVIDIA Inception

[![Licença: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-v0.186.1-green)](https://crewai.com/)

## Descrição

O **Horizon** é uma solução desenvolvida para o desafio do NVIDIA Inception, parte do Inteli Academy Challenge. Ele utiliza agentes de inteligência artificial (baseados em CrewAI) para automatizar a descoberta, análise e qualificação de startups de IA na América Latina. O foco é identificar startups apoiadas por top VCs (Venture Capitals), realizar análises de mercado, validar e pontuar as startups, analisar investimentos e enviar newsletters com insights estratégicos.

Essa ferramenta aborda o problema de fragmentação de dados no ecossistema de startups, ajudando a NVIDIA a mapear oportunidades promissoras e fortalecer o programa Inception. Inspirado no case da NVIDIA, o Horizon transforma dados dispersos em relatórios acionáveis, facilitando parcerias e networking.

## Funcionalidades Principais

- **Descoberta de Startups**: Busca startups de IA apoiadas por top VCs na América Latina usando ferramentas de busca web e scraping de sites.
- **Análise de Mercado**: Gera relatórios sobre o ecossistema de IA por país, incluindo cenário competitivo, oportunidades de crescimento, tendências e gaps de mercado.
- **Validação e Scoring**: Valida dados das startups e atribui scores baseados em inovação, potencial de mercado, alinhamento com tecnologias NVIDIA (ex.: GPUs/CUDA) e atratividade de investimento.
- **Análise de Funding e VCs**: Identifica investidores, rodadas de investimento, setores e qualidade dos VCs.
- **Envio de Newsletter**: Gera e envia relatórios consolidados via email (usando Resend API), com outputs em JSON (ex.: discovered_startups.json, market_analysis.json).
- **Armazenamento de Dados**: Usa banco de dados JSON persistente para evitar duplicatas e padronizar informações.

## Tecnologias Utilizadas

- **Framework Principal**: CrewAI para orquestração de agentes de IA.
- **Linguagem**: Python 3.10+.
- **Dependências** (de pyproject.toml):
  - crewai[tools] (>=0.186.1)
  - pandas (>=2.0.0)
  - beautifulsoup4 (>=4.12.0)
  - requests (>=2.31.0)
  - openpyxl (>=3.1.0)
- **Ferramentas Customizadas**: StartupDiscoveryTool, CompanyAnalysisTool, FundingResearchTool, LinkedInSearchTool, etc.
- **Integrações**: Busca em X (Twitter), web scraping, LinkedIn search, email via Resend.
- **Outputs**: Arquivos JSON e MD para relatórios (ex.: nvidia_inception_brazil_summary.md).

## Instalação

1. Clone o repositório:

   ```
   git clone https://github.com/seu-usuario/horizon.git
   cd horizon
   ```

2. Instale as dependências usando Poetry (recomendado) ou pip:

   ```
   poetry install
   ```

   Ou:

   ```
   pip install -r requirements.txt  # Crie um requirements.txt se necessário: poetry export -f requirements.txt --output requirements.txt
   ```

3. Configure variáveis de ambiente (crie um `.env` na raiz):
   ```
   RESEND_API_KEY=sua-chave-resend
   OPENAI_API_KEY=sua-chave-openai
   ```

## Uso

1. Execute o script principal para descobrir startups. Para mudar o país, altere no arquivo `main.py`

   ```
   crewai run
   ```

2. Outputs gerados:

   - `discovered_startups.json`: Lista de startups encontradas.
   - `market_analysis.json`: Análise de mercado.
   - `funding_analysis.json`: Detalhes de funding.

3. Para testar o envio de email:
   ```
   poetry run python src/horizon/utils/email_tester.py
   ```

## Configuração Avançada

- **Agentes e Tarefas**: Configurados em `src/horizon/config/agents.yaml` e `tasks.yaml`.
- **Banco de Dados**: Gerenciado por `src/horizon/utils/database.py` (JSON-based).
- **Ferramentas**: Definidas em `src/horizon/tools/startup_discovery_tools.py`.
- Personalize queries de busca ou prompts de agentes editando os YAMLs.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

- Desenvolvedor: Gabriel Willian Bartmanovicz (obielwb@gmail.com)
- LinkedIn: https://www.linkedin.com/in/gabriel-bartmanovicz/
- Para dúvidas sobre o desafio NVIDIA: ana.silva@sou.inteli.edu.br ou jonathan.alves@sou.inteli.edu.br

Desenvolvido como parte do Inteli Academy Challenge em parceria com NVIDIA.
