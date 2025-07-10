from crewai import Agent, Task, Crew, Process
import os
import json
from datetime import datetime

class ProjectManagementWorkflow:
    """
    Workflow para gerenciamento de projetos usando CrewAI.
    
    Este workflow coordena os agentes especializados em cronograma, custos, escopo e riscos
    para analisar arquivos de status de projetos e gerar recomendações.
    """
    
    def __init__(self, llm_api_key=None, process_type="sequential"):
        """
        Inicializa o workflow.
        
        Args:
            llm_api_key: Chave de API para o LLM (opcional)
            process_type: Tipo de processo (sequential ou hierarchical)
        """
        self.llm_api_key = llm_api_key
        self.process_type = process_type
        
        # Configurar diretórios
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.status_dir = os.path.join(self.base_dir, "..", "..", "dataset", "status_files")
        self.results_dir = os.path.join(self.base_dir, "..", "results")
        
        # Criar diretório de resultados se não existir
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Inicializar agentes e tarefas
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        
        # Criar crew
        self.crew = self._create_crew()
    
    def _create_agents(self):
        """
        Cria os agentes especializados.
        
        Returns:
            Dicionário com os agentes
        """
        # Agente de Cronograma
        schedule_agent = Agent(
            role="Especialista em Gerenciamento de Cronograma",
            goal="Analisar o status do cronograma do projeto e recomendar ações para manter o projeto no prazo",
            backstory="""Você é um especialista em gerenciamento de cronograma com vasta experiência em projetos complexos.
            Você é conhecido por sua capacidade de identificar problemas no cronograma e propor soluções eficazes.
            Você tem profundo conhecimento das melhores práticas do PMBOK para gerenciamento de cronograma.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Agente de Custos
        cost_agent = Agent(
            role="Especialista em Gerenciamento de Custos",
            goal="Analisar o status dos custos do projeto e recomendar ações para manter o projeto dentro do orçamento",
            backstory="""Você é um especialista em gerenciamento de custos com vasta experiência em controle orçamentário.
            Você é conhecido por sua capacidade de identificar desvios de custos e propor medidas de economia eficazes.
            Você tem profundo conhecimento das melhores práticas do PMBOK para gerenciamento de custos.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Agente de Escopo
        scope_agent = Agent(
            role="Especialista em Gerenciamento de Escopo",
            goal="Analisar o status do escopo do projeto e recomendar ações para controlar mudanças de escopo",
            backstory="""Você é um especialista em gerenciamento de escopo com vasta experiência em definição e controle de requisitos.
            Você é conhecido por sua capacidade de avaliar o impacto de mudanças de escopo e propor estratégias de mitigação.
            Você tem profundo conhecimento das melhores práticas do PMBOK para gerenciamento de escopo.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Agente de Riscos
        risk_agent = Agent(
            role="Especialista em Gerenciamento de Riscos",
            goal="Analisar o status dos riscos do projeto e recomendar ações para mitigar ameaças e explorar oportunidades",
            backstory="""Você é um especialista em gerenciamento de riscos com vasta experiência em identificação e análise de riscos.
            Você é conhecido por sua capacidade de desenvolver estratégias eficazes de resposta a riscos.
            Você tem profundo conhecimento das melhores práticas do PMBOK para gerenciamento de riscos.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Agente Gerente de Projeto (para modo hierárquico)
        project_manager_agent = Agent(
            role="Gerente de Projeto",
            goal="Coordenar a análise do status do projeto e consolidar as recomendações dos especialistas",
            backstory="""Você é um gerente de projeto experiente com certificação PMP.
            Você é conhecido por sua capacidade de liderar equipes multidisciplinares e tomar decisões baseadas em dados.
            Você tem profundo conhecimento de todas as áreas do PMBOK e sabe como integrar as diferentes perspectivas.""",
            verbose=True,
            allow_delegation=True
        )
        
        return {
            "schedule": schedule_agent,
            "cost": cost_agent,
            "scope": scope_agent,
            "risk": risk_agent,
            "project_manager": project_manager_agent
        }
    
    def _create_tasks(self):
        """
        Cria as tarefas para os agentes.
        
        Returns:
            Dicionário com as tarefas
        """
        # Tarefa para o Agente de Cronograma
        schedule_task = Task(
            description=f"""
            Analise o arquivo de status de cronograma do projeto e forneça recomendações.
            
            Passos:
            1. Leia o arquivo de status de cronograma localizado em {self.status_dir}/PROJ-0001_cronograma.txt
            2. Identifique o SPI (Índice de Desempenho de Cronograma) e avalie a saúde do cronograma
            3. Identifique as tarefas críticas e atrasadas
            4. Forneça recomendações específicas baseadas nas melhores práticas do PMBOK
            5. Priorize as recomendações com base no impacto e urgência
            
            Seu relatório deve incluir:
            - Resumo do status atual do cronograma
            - Avaliação da saúde do cronograma com base no SPI
            - Lista de recomendações priorizadas
            - Justificativa para cada recomendação
            """,
            agent=self.agents["schedule"],
            expected_output="""
            Um relatório detalhado com análise do status do cronograma e recomendações priorizadas.
            O relatório deve seguir o formato:
            
            # ANÁLISE DE CRONOGRAMA
            
            ## Status Atual
            [Resumo do status atual]
            
            ## Avaliação da Saúde
            [Avaliação baseada no SPI]
            
            ## Recomendações
            1. [Recomendação prioritária 1]
            2. [Recomendação prioritária 2]
            ...
            
            ## Justificativa
            [Justificativa para cada recomendação]
            """
        )
        
        # Tarefa para o Agente de Custos
        cost_task = Task(
            description=f"""
            Analise o arquivo de status de custos do projeto e forneça recomendações.
            
            Passos:
            1. Leia o arquivo de status de custos localizado em {self.status_dir}/PROJ-0001_custos.txt
            2. Identifique o CPI (Índice de Desempenho de Custo) e avalie a saúde dos custos
            3. Identifique as categorias de custo com maior desvio
            4. Forneça recomendações específicas baseadas nas melhores práticas do PMBOK
            5. Priorize as recomendações com base no impacto e urgência
            
            Seu relatório deve incluir:
            - Resumo do status atual dos custos
            - Avaliação da saúde dos custos com base no CPI
            - Lista de recomendações priorizadas
            - Justificativa para cada recomendação
            """,
            agent=self.agents["cost"],
            expected_output="""
            Um relatório detalhado com análise do status dos custos e recomendações priorizadas.
            O relatório deve seguir o formato:
            
            # ANÁLISE DE CUSTOS
            
            ## Status Atual
            [Resumo do status atual]
            
            ## Avaliação da Saúde
            [Avaliação baseada no CPI]
            
            ## Recomendações
            1. [Recomendação prioritária 1]
            2. [Recomendação prioritária 2]
            ...
            
            ## Justificativa
            [Justificativa para cada recomendação]
            """
        )
        
        # Tarefa para o Agente de Escopo
        scope_task = Task(
            description=f"""
            Analise o arquivo de status de escopo do projeto e forneça recomendações.
            
            Passos:
            1. Leia o arquivo de status de escopo localizado em {self.status_dir}/PROJ-0001_escopo.txt
            2. Identifique se houve mudanças de escopo e seu impacto
            3. Avalie as solicitações de mudança pendentes
            4. Forneça recomendações específicas baseadas nas melhores práticas do PMBOK
            5. Priorize as recomendações com base no impacto e urgência
            
            Seu relatório deve incluir:
            - Resumo do status atual do escopo
            - Avaliação do impacto das mudanças de escopo
            - Lista de recomendações priorizadas
            - Justificativa para cada recomendação
            """,
            agent=self.agents["scope"],
            expected_output="""
            Um relatório detalhado com análise do status do escopo e recomendações priorizadas.
            O relatório deve seguir o formato:
            
            # ANÁLISE DE ESCOPO
            
            ## Status Atual
            [Resumo do status atual]
            
            ## Avaliação de Impacto
            [Avaliação do impacto das mudanças]
            
            ## Recomendações
            1. [Recomendação prioritária 1]
            2. [Recomendação prioritária 2]
            ...
            
            ## Justificativa
            [Justificativa para cada recomendação]
            """
        )
        
        # Tarefa para o Agente de Riscos
        risk_task = Task(
            description=f"""
            Analise o arquivo de status de riscos do projeto e forneça recomendações.
            
            Passos:
            1. Leia o arquivo de status de riscos localizado em {self.status_dir}/PROJ-0001_riscos.txt
            2. Identifique os riscos de alto nível e riscos que já ocorreram
            3. Avalie a eficácia das respostas aos riscos ocorridos
            4. Forneça recomendações específicas baseadas nas melhores práticas do PMBOK
            5. Priorize as recomendações com base no impacto e urgência
            
            Seu relatório deve incluir:
            - Resumo do status atual dos riscos
            - Avaliação dos riscos de alto nível
            - Lista de recomendações priorizadas
            - Justificativa para cada recomendação
            """,
            agent=self.agents["risk"],
            expected_output="""
            Um relatório detalhado com análise do status dos riscos e recomendações priorizadas.
            O relatório deve seguir o formato:
            
            # ANÁLISE DE RISCOS
            
            ## Status Atual
            [Resumo do status atual]
            
            ## Avaliação de Riscos
            [Avaliação dos riscos de alto nível]
            
            ## Recomendações
            1. [Recomendação prioritária 1]
            2. [Recomendação prioritária 2]
            ...
            
            ## Justificativa
            [Justificativa para cada recomendação]
            """
        )
        
        # Tarefa para o Gerente de Projeto (para modo hierárquico)
        pm_task = Task(
            description=f"""
            Coordene a análise do status do projeto e consolide as recomendações dos especialistas.
            
            Passos:
            1. Delegue a análise do cronograma para o Especialista em Gerenciamento de Cronograma
            2. Delegue a análise dos custos para o Especialista em Gerenciamento de Custos
            3. Delegue a análise do escopo para o Especialista em Gerenciamento de Escopo
            4. Delegue a análise dos riscos para o Especialista em Gerenciamento de Riscos
            5. Consolide os resultados das análises
            6. Identifique interdependências entre as recomendações
            7. Priorize as recomendações com base no impacto global no projeto
            
            Seu relatório deve incluir:
            - Resumo executivo do status do projeto
            - Principais problemas identificados em cada área
            - Lista consolidada de recomendações priorizadas
            - Plano de ação integrado
            """,
            agent=self.agents["project_manager"],
            expected_output="""
            Um relatório executivo consolidado com análise integrada do status do projeto e plano de ação.
            O relatório deve seguir o formato:
            
            # RELATÓRIO EXECUTIVO DO PROJETO
            
            ## Resumo do Status
            [Resumo executivo do status do projeto]
            
            ## Principais Problemas
            [Lista dos principais problemas em cada área]
            
            ## Recomendações Priorizadas
            1. [Recomendação prioritária 1]
            2. [Recomendação prioritária 2]
            ...
            
            ## Plano de Ação Integrado
            [Plano de ação com responsáveis e prazos]
            """
        )
        
        return {
            "schedule": schedule_task,
            "cost": cost_task,
            "scope": scope_task,
            "risk": risk_task,
            "project_manager": pm_task
        }
    
    def _create_crew(self):
        """
        Cria a crew com os agentes e tarefas.
        
        Returns:
            Objeto Crew
        """
        if self.process_type == "hierarchical":
            # Modo hierárquico - o gerente de projeto coordena os especialistas
            crew = Crew(
                agents=[
                    self.agents["project_manager"],
                    self.agents["schedule"],
                    self.agents["cost"],
                    self.agents["scope"],
                    self.agents["risk"]
                ],
                tasks=[self.tasks["project_manager"]],
                process=Process.hierarchical,
                verbose=2
            )
        else:
            # Modo sequencial - os especialistas trabalham em sequência
            crew = Crew(
                agents=[
                    self.agents["schedule"],
                    self.agents["cost"],
                    self.agents["scope"],
                    self.agents["risk"]
                ],
                tasks=[
                    self.tasks["schedule"],
                    self.tasks["cost"],
                    self.tasks["scope"],
                    self.tasks["risk"]
                ],
                process=Process.sequential,
                verbose=2
            )
        
        return crew
    
    def run(self):
        """
        Executa o workflow.
        
        Returns:
            Resultados da execução
        """
        # Executar a crew
        results = self.crew.kickoff()
        
        # Salvar resultados
        self._save_results(results)
        
        return results
    
    def _save_results(self, results):
        """
        Salva os resultados da execução.
        
        Args:
            results: Resultados da execução
        """
        # Criar nome de arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{self.process_type}_{timestamp}.txt"
        filepath = os.path.join(self.results_dir, filename)
        
        # Salvar resultados
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(results, list):
                for i, result in enumerate(results):
                    f.write(f"=== RESULTADO {i+1} ===\n\n")
                    f.write(result)
                    f.write("\n\n")
            else:
                f.write(results)
        
        print(f"Resultados salvos em: {filepath}")

# Exemplo de uso
if __name__ == "__main__":
    import argparse
    
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Workflow de Gerenciamento de Projetos com CrewAI')
    parser.add_argument('--process', choices=['sequential', 'hierarchical'], default='sequential',
                        help='Tipo de processo (sequential ou hierarchical)')
    parser.add_argument('--api_key', type=str, help='Chave de API para o LLM')
    parser.add_argument('--mock', action='store_true', help='Usar modo de simulação (sem chamadas reais ao LLM)')
    
    args = parser.parse_args()
    
    # Criar e executar workflow
    workflow = ProjectManagementWorkflow(
        llm_api_key=args.api_key,
        process_type=args.process
    )
    
    if args.mock:
        print("Executando em modo de simulação...")
        # Simular resultados
        mock_results = [
            """
            # ANÁLISE DE CRONOGRAMA
            
            ## Status Atual
            O projeto está com SPI de 0.85, indicando um leve atraso no cronograma.
            
            ## Avaliação da Saúde
            O cronograma está em estado de ATENÇÃO devido ao SPI abaixo de 0.9.
            
            ## Recomendações
            1. Revisar o caminho crítico e identificar oportunidades de fast-tracking
            2. Implementar horas extras para recuperar o atraso
            3. Monitorar de perto as tarefas críticas
            
            ## Justificativa
            As recomendações visam recuperar o atraso sem impactar o escopo ou a qualidade.
            """,
            """
            # ANÁLISE DE CUSTOS
            
            ## Status Atual
            O projeto está com CPI de 0.92, indicando um leve desvio no orçamento.
            
            ## Avaliação da Saúde
            Os custos estão em estado de ATENÇÃO devido ao CPI abaixo de 0.95.
            
            ## Recomendações
            1. Revisar as categorias de custo com maior desvio
            2. Implementar medidas de economia sem impactar a qualidade
            3. Monitorar de perto todas as despesas futuras
            
            ## Justificativa
            As recomendações visam controlar os custos sem comprometer os objetivos do projeto.
            """,
            """
            # ANÁLISE DE ESCOPO
            
            ## Status Atual
            O projeto teve uma mudança de escopo que impacta o cronograma em 15 dias.
            
            ## Avaliação de Impacto
            O impacto da mudança de escopo é SIGNIFICATIVO e requer revisão da linha de base.
            
            ## Recomendações
            1. Documentar formalmente a mudança de escopo
            2. Revisar a linha de base do cronograma
            3. Avaliar o impacto nos custos e recursos
            
            ## Justificativa
            As recomendações visam garantir que a mudança de escopo seja gerenciada adequadamente.
            """,
            """
            # ANÁLISE DE RISCOS
            
            ## Status Atual
            O projeto tem 3 riscos de nível alto que requerem atenção imediata.
            
            ## Avaliação de Riscos
            Os riscos de alto nível representam uma AMEAÇA SIGNIFICATIVA para o sucesso do projeto.
            
            ## Recomendações
            1. Implementar planos de mitigação para os riscos de alto nível
            2. Revisar o registro de riscos semanalmente
            3. Desenvolver planos de contingência para os riscos críticos
            
            ## Justificativa
            As recomendações visam reduzir a exposição do projeto aos riscos identificados.
            """
        ]
        
        # Salvar resultados simulados
        workflow._save_results(mock_results)
        
        print("Simulação concluída!")
    else:
        # Executar workflow real
        results = workflow.run()
        
        print("Execução concluída!")
