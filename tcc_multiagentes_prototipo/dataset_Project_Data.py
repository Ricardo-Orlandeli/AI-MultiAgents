import pandas as pd
import numpy as np
import random
import os
import json
from datetime import datetime, timedelta
from faker import Faker

# Configurar o Faker para português do Brasil
fake = Faker('pt_BR')
Faker.seed(42)  # Para reprodutibilidade
np.random.seed(42)
random.seed(42)

def gerar_dataset(num_projetos=1000, output_dir="../dataset"):
    """
    Generates a synthetic dataset for training AI agents.

    Args:
        num_projetos: Number of projects to generate
        output_dir: Output directory for the files
    """
    print(f"Generating dataset with {num_projetos} projects...")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate projects
    projetos = []
    for i in range(num_projetos):
        projeto_id = f"PROJ-{i+1:04d}"

        # Basic project data
        data_inicio = fake.date_between(start_date='-2y', end_date='-6m')
        duracao_planejada = random.randint(30, 365)  # Between 1 month and 1 year
        data_termino_planejada = data_inicio + timedelta(days=duracao_planejada)

        # Project status (in progress, completed, delayed, cancelled)
        status_opcoes = ['Em andamento', 'Concluído', 'Atrasado', 'Cancelado']
        status_pesos = [0.5, 0.2, 0.25, 0.05]  # More projects in progress and delayed
        status = random.choices(status_opcoes, weights=status_pesos, k=1)[0]

        # Budget and manager
        orcamento_inicial = random.randint(50000, 5000000)
        gerente = fake.name()

        # Completion percentage
        if status == 'Concluído':
            percentual_conclusao = 100.0
        elif status == 'Cancelado':
            percentual_conclusao = random.uniform(10.0, 90.0)
        else:
            # For projects in progress or delayed, the percentage depends on elapsed time
            dias_decorridos = (datetime.now().date() - data_inicio).days
            percentual_tempo = min(1.0, dias_decorridos / duracao_planejada)

            if status == 'Em andamento':
                # Projects in progress can be slightly ahead or behind schedule
                percentual_conclusao = percentual_tempo * random.uniform(0.8, 1.2)
            else:  # Delayed
                # Delayed projects have a completion percentage lower than elapsed time
                percentual_conclusao = percentual_tempo * random.uniform(0.5, 0.9)

            percentual_conclusao = min(99.9, max(1.0, percentual_conclusao * 100))

        # Actual/forecasted end date
        if status == 'Concluído':
            # Completed projects may have finished early, on time, or with a small delay
            variacao_dias = random.randint(-30, 30)
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)
        elif status == 'Cancelado':
            # Cancelled projects end early
            data_termino_real = data_inicio + timedelta(days=int(duracao_planejada * percentual_conclusao / 100))
        elif status == 'Atrasado':
            # Delayed projects have a forecasted end date after the planned date
            atraso_dias = random.randint(10, 180)  # Between 10 days and 6 months of delay
            data_termino_real = data_termino_planejada + timedelta(days=atraso_dias)
        else:  # Em andamento
            # Projects in progress can be on time or with a small delay/ahead
            variacao_dias = random.randint(-15, 30)
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)

        # Calculate current delay in days
        if datetime.now().date() > data_termino_planejada:
            atraso_atual = (datetime.now().date() - data_termino_planejada).days
        else:
            atraso_atual = 0

        # Generate earned value metrics
        percentual_tempo = min(1.0, (datetime.now().date() - data_inicio).days / duracao_planejada)
        pv = orcamento_inicial * percentual_tempo  # Planned Value

        # Earned Value (EV) based on completion percentage and budget
        ev = orcamento_inicial * (percentual_conclusao / 100)

        # Actual Cost (AC) with variation
        if status == 'Em andamento' or status == 'Concluído':
            ac_variacao = random.uniform(0.8, 1.2)  # Variation from -20% to +20%
        else:  # Delayed or Cancelled
            ac_variacao = random.uniform(1.0, 1.5)  # Variation from 0% to +50% (higher costs)

        ac = float(ev) * ac_variacao

        # Calculate SPI and CPI
        spi = ev / pv if pv > 0 else 1.0
        cpi = ev / ac if ac > 0 else 1.0

        # Adjust SPI and CPI for specific statuses
        if status == 'Atrasado':
            spi = min(spi, 0.9)  # Delayed projects have SPI < 0.9
        elif status == 'Em andamento':
            spi = random.uniform(0.85, 1.15)  # Projects in progress have SPI between 0.85 and 1.15
        elif status == 'Concluído':
            spi = random.uniform(0.95, 1.1)  # Completed projects have SPI between 0.95 and 1.1

        # Estimates
        etc = (float(orcamento_inicial) - float(ev)) / cpi if cpi > 0 and percentual_conclusao < 100 else 0  # Estimate to Complete
        eac = ac + etc  # Estimate at Completion
        vac = orcamento_inicial - eac  # Variance at Completion

        # Budget variance in percentage
        desvio_orcamento = ((ac / (float(orcamento_inicial) * percentual_tempo)) - 1) * 100 if percentual_tempo > 0 else 0

        # Generate cost categories
        categorias_custos = {
            "Pessoal": float(ac) * random.uniform(0.4, 0.6),
            "Equipamentos": float(ac) * random.uniform(0.1, 0.2),
            "Software": float(ac) * random.uniform(0.05, 0.15),
            "Serviços": float(ac) * random.uniform(0.1, 0.2),
            "Outros": float(ac) * random.uniform(0.05, 0.1)
        }
        # Adjust to ensure sum equals AC
        soma_categorias = sum(categorias_custos.values())
        fator_ajuste = float(ac) / float(soma_categorias)
        categorias_custos = {k: v * fator_ajuste for k, v in categorias_custos.items()}

        # Generate scope information
        mudanca_escopo = random.choices(['Sim', 'Não'], weights=[0.3, 0.7], k=1)[0]
        if mudanca_escopo == 'Sim':
            descricao_mudancas = random.choice([
                "Adição de novos requisitos de segurança",
                "Expansão do escopo para incluir funcionalidades adicionais",
                "Redução do escopo devido a restrições orçamentárias",
                "Alteração nas especificações técnicas",
                "Mudança na plataforma de implementação"
            ])
            impacto_cronograma = random.randint(5, 60)  # Between 5 and 60 days
            impacto_custo = float(orcamento_inicial) * random.uniform(0.05, 0.2)  # Between 5% and 20% of the budget
            # Generate change requests
            num_solicitacoes = random.randint(1, 5)
            solicitacoes_mudanca = []
            for j in range(num_solicitacoes):
                solicitacao = random.choice([
                    'Adição de funcionalidade de autenticação biométrica',
                    'Alteração na interface do usuário',
                    'Integração com sistema legado',
                    'Mudança no banco de dados',
                    'Adição de relatórios gerenciais',
                    'Implementação de módulo de exportação de dados',
                    'Alteração nos requisitos de desempenho',
                    'Mudança na arquitetura do sistema'
                ])
                solicitacoes_mudanca.append(f"SCM-{j+1:02d}: {solicitacao}")
        else:
            descricao_mudancas = "N/A"
            impacto_cronograma = 0
            impacto_custo = 0
            solicitacoes_mudanca = []

        # Generate requirements
        num_requisitos = random.randint(5, 15)
        requisitos = []
        for j in range(num_requisitos):
            requisitos.append(f"REQ-{j+1:02d}: {random.choice([
                'O sistema deve permitir autenticação de usuários',
                'O sistema deve processar transações em menos de 2 seconds',
                'O sistema deve ser compatível com navegadores modernos',
                'O sistema deve permitir exportação de dados em formato CSV',
                'O sistema deve implementar criptografia de dados sensíveis',
                'O sistema deve ter interface responsiva',
                'O sistema deve permitir integração com APIs externas',
                'O sistema deve ter backup automático diário',
                'O sistema deve ter controle de acesso baseado em perfis',
                'O sistema deve registrar logs de auditoria',
                'O sistema deve ter alta disponibilidade (99.9%)',
                'O sistema deve ser escalável para suportar até 10.000 usuários simultâneos',
                'O sistema deve ter documentação completa',
                'O sistema deve passar por testes de segurança',
                'O sistema deve ser compatível com dispositivos móveis'
            ])}")

        # Generate risks
        num_riscos = random.randint(3, 10)
        riscos = []
        for j in range(num_riscos):
            probabilidade = random.randint(1, 5)
            impacto = random.randint(1, 5)
            nivel = "Baixo" if probabilidade * impacto <= 6 else "Médio" if probabilidade * impacto <= 15 else "Alto"
            riscos.append({
                "id": f"R{j+1:02d}",
                "descricao": random.choice([
                    "Atraso na entrega de componentes críticos",
                    "Rotatividade de pessoal-chave",
                    "Mudanças regulatórias",
                    "Problemas de integração com sistemas legados",
                    "Falhas de segurança",
                    "Indisponibilidade de recursos especializados",
                    "Problemas de desempenho",
                    "Falhas em testes de aceitação",
                    "Resistência dos usuários à mudança",
                    "Problemas de compatibilidade",
                    "Falhas de infraestrutura",
                    "Dependências externas não cumpridas",
                    "Estimativas imprecisas",
                    "Requisitos mal definidos",
                    "Problemas de comunicação com stakeholders"
                ]),
                "probabilidade": probabilidade,
                "impacto": impacto,
                "nivel": nivel,
                "plano_mitigacao": random.choice([
                    "Implementar plano de contingência",
                    "Contratar pessoal adicional",
                    "Monitorar mudanças regulatórias",
                    "Realizar testes de integração antecipados",
                    "Fortalecer medidas de segurança",
                    "Buscar fornecedores alternativos",
                    "Otimizar código e infraestrutura",
                    "Realizar testes de aceitação com usuários-chave",
                    "Comunicar benefícios da mudança",
                    "Testar compatibilidade em diferentes ambientes",
                    "Implementar redundância de infraestrutura",
                    "Gerenciar dependências ativamente",
                    "Refinar estimativas com base em dados históricos",
                    "Melhorar a documentação de requisitos",
                    "Estabelecer canais de comunicação claros"
                ])
            })

        # ... (continue handling stakeholders, communication, quality metrics, resources, dependencies, lessons, risks_ocorridos, tasks, etc. as in your original code)

        # Compile project information
        projeto = {
            "id": projeto_id,
            "nome": fake.catch_phrase(),
            "data_inicio": data_inicio.strftime("%d/%m/%Y"),
            "data_termino_planejada": data_termino_planejada.strftime("%d/%m/%Y"),
            "data_termino_real": data_termino_real.strftime("%d/%m/%Y"),
            "duracao_planejada": duracao_planejada,
            "orcamento_inicial": orcamento_inicial,
            "gerente": gerente,
            "status": status,
            "percentual_conclusao": percentual_conclusao,
            "atraso_atual": atraso_atual,
            # ... etc., add all fields as in your original logic
        }

        projetos.append(projeto)

    # Save dataset in JSON format
    with open(os.path.join(output_dir, "projetos.json"), 'w', encoding='utf-8') as f:
        json.dump(projetos, f, ensure_ascii=False, indent=2)

    # Save dataset in CSV format (main data only)
    df_projetos = pd.DataFrame([{
        "id": p["id"],
        "nome": p["nome"],
        "data_inicio": p["data_inicio"],
        "data_termino_planejada": p["data_termino_planejada"],
        "data_termino_real": p["data_termino_real"],
        "orcamento_inicial": p["orcamento_inicial"],
        "gerente": p["gerente"],
        "status": p["status"],
        "percentual_conclusao": p["percentual_conclusao"],
        "spi": p.get("spi", None),
        "cpi": p.get("cpi", None),
        "mudanca_escopo": p.get("mudanca_escopo", None)
    } for p in projetos])

    df_projetos.to_csv(os.path.join(output_dir, "projetos.csv"), index=False)

    print(f"Dataset generated successfully! Files saved in {output_dir}")
    return projetos

if __name__ == "__main__":
    gerar_dataset(num_projetos=1000)
