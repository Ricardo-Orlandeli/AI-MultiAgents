{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1046{\fonttbl{\f0\fnil\fcharset0 Calibri;}}
{\*\generator Riched20 10.0.22621}\viewkind4\uc1 
\pard\sa200\sl276\slmult1\f0\fs22\lang22 import pandas as pd\par
import numpy as np\par
import random\par
import os\par
import json\par
from datetime import datetime, timedelta\par
from faker import Faker\par
\par
# Configurar o Faker para portugu\'eas do Brasil\par
fake = Faker('pt_BR')\par
Faker.seed(42)  # Para reprodutibilidade\par
np.random.seed(42)\par
random.seed(42)\par
\par
def gerar_dataset(num_projetos=1000, output_dir="../dataset"):\par
    """\par
    Generates a synthetic dataset for training AI agents.\par
\par
    Args:\par
        num_projetos: Number of projects to generate\par
        output_dir: Output directory for the files\par
    """\par
    print(f"Generating dataset with \{num_projetos\} projects...")\par
\par
    # Create output directory if it doesn't exist\par
    os.makedirs(output_dir, exist_ok=True)\par
\par
    # Generate projects\par
    projetos = []\par
    for i in range(num_projetos):\par
        projeto_id = f"PROJ-\{i+1:04d\}"\par
\par
        # Basic project data\par
        data_inicio = fake.date_between(start_date='-2y', end_date='-6m')\par
        duracao_planejada = random.randint(30, 365)  # Between 1 month and 1 year\par
        data_termino_planejada = data_inicio + timedelta(days=duracao_planejada)\par
\par
        # Project status (in progress, completed, delayed, cancelled)\par
        status_opcoes = ['Em andamento', 'Conclu\'eddo', 'Atrasado', 'Cancelado']\par
        status_pesos = [0.5, 0.2, 0.25, 0.05]  # More projects in progress and delayed\par
        status = random.choices(status_opcoes, weights=status_pesos, k=1)[0]\par
\par
        # Budget and manager\par
        orcamento_inicial = random.randint(50000, 5000000)\par
        gerente = fake.name()\par
\par
        # Completion percentage\par
        if status == 'Conclu\'eddo':\par
            percentual_conclusao = 100.0\par
        elif status == 'Cancelado':\par
            percentual_conclusao = random.uniform(10.0, 90.0)\par
        else:\par
            # For projects in progress or delayed, the percentage depends on elapsed time\par
            dias_decorridos = (datetime.now().date() - data_inicio).days\par
            percentual_tempo = min(1.0, dias_decorridos / duracao_planejada)\par
\par
            if status == 'Em andamento':\par
                # Projects in progress can be slightly ahead or behind schedule\par
                percentual_conclusao = percentual_tempo * random.uniform(0.8, 1.2)\par
            else:  # Delayed\par
                # Delayed projects have a completion percentage lower than elapsed time\par
                percentual_conclusao = percentual_tempo * random.uniform(0.5, 0.9)\par
\par
            percentual_conclusao = min(99.9, max(1.0, percentual_conclusao * 100))\par
\par
        # Actual/forecasted end date\par
        if status == 'Conclu\'eddo':\par
            # Completed projects may have finished early, on time, or with a small delay\par
            variacao_dias = random.randint(-30, 30)\par
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)\par
        elif status == 'Cancelado':\par
            # Cancelled projects end early\par
            data_termino_real = data_inicio + timedelta(days=int(duracao_planejada * percentual_conclusao / 100))\par
        elif status == 'Atrasado':\par
            # Delayed projects have a forecasted end date after the planned date\par
            atraso_dias = random.randint(10, 180)  # Between 10 days and 6 months of delay\par
            data_termino_real = data_termino_planejada + timedelta(days=atraso_dias)\par
        else:  # Em andamento\par
            # Projects in progress can be on time or with a small delay/ahead\par
            variacao_dias = random.randint(-15, 30)\par
            data_termino_real = data_termino_planejada + timedelta(days=variacao_dias)\par
\par
        # Calculate current delay in days\par
        if datetime.now().date() > data_termino_planejada:\par
            atraso_atual = (datetime.now().date() - data_termino_planejada).days\par
        else:\par
            atraso_atual = 0\par
\par
        # Generate earned value metrics\par
        pv = orcamento_inicial * (percentual_tempo if percentual_tempo <= 1.0 else 1.0)  # Planned Value\par
\par
        # Earned Value (EV) based on completion percentage and budget\par
        ev = orcamento_inicial * (percentual_conclusao / 100)\par
\par
        # Actual Cost (AC) with variation\par
        if status == 'Em andamento' or status == 'Conclu\'eddo':\par
            ac_variacao = random.uniform(0.8, 1.2)  # Variation from -20% to +20%\par
        else:  # Delayed or Cancelled\par
            ac_variacao = random.uniform(1.0, 1.5)  # Variation from 0% to +50% (higher costs)\par
\par
        ac = float(ev) * ac_variacao\par
\par
        # Calculate SPI and CPI\par
        spi = ev / pv if pv > 0 else 1.0\par
        cpi = ev / ac if ac > 0 else 1.0\par
\par
        # Adjust SPI and CPI for specific statuses\par
        if status == 'Atrasado':\par
            spi = min(spi, 0.9)  # Delayed projects have SPI < 0.9\par
        elif status == 'Em andamento':\par
            spi = random.uniform(0.85, 1.15)  # Projects in progress have SPI between 0.85 and 1.15\par
        elif status == 'Conclu\'eddo':\par
            spi = random.uniform(0.95, 1.1)  # Completed projects have SPI between 0.95 and 1.1\par
\par
        # Estimates\par
        etc = (float(orcamento_inicial) - float(ev)) / cpi if cpi > 0 and percentual_conclusao < 100 else 0  # Estimate to Complete\par
        eac = ac + etc  # Estimate at Completion\par
        vac = orcamento_inicial - eac  # Variance at Completion\par
\par
        # Budget variance in percentage\par
        desvio_orcamento = ((ac / (float(orcamento_inicial) * percentual_tempo)) - 1) * 100 if percentual_tempo > 0 else 0\par
\par
        # Generate cost categories\par
        categorias_custos = \{\par
            "Pessoal": float(ac) * random.uniform(0.4, 0.6),\par
            "Equipamentos": float(ac) * random.uniform(0.1, 0.2),\par
            "Software": float(ac) * random.uniform(0.05, 0.15),\par
            "Servi\'e7os": float(ac) * random.uniform(0.1, 0.2),\par
            "Outros": float(ac) * random.uniform(0.05, 0.1)\par
        \}\par
\par
        # Adjust to ensure sum equals AC\par
        soma_categorias = sum(categorias_custos.values())\par
        fator_ajuste = float(ac) / float(soma_categorias)\par
        categorias_custos = \{k: v * fator_ajuste for k, v in categorias_custos.items()\}\par
\par
        # Generate scope information\par
        mudanca_escopo = random.choices(['Sim', 'N\'e3o'], weights=[0.3, 0.7], k=1)[0]\par
\par
        if mudanca_escopo == 'Sim':\par
            descricao_mudancas = random.choice([\par
                "Adi\'e7\'e3o de novos requisitos de seguran\'e7a",\par
                "Expans\'e3o do escopo para incluir funcionalidades adicionais",\par
                "Redu\'e7\'e3o do escopo devido a restri\'e7\'f5es or\'e7ament\'e1rias",\par
                "Altera\'e7\'e3o nas especifica\'e7\'f5es t\'e9cnicas",\par
                "Mudan\'e7a na plataforma de implementa\'e7\'e3o"\par
            ])\par
\par
            impacto_cronograma = random.randint(5, 60)  # Between 5 and 60 days\par
            impacto_custo = float(orcamento_inicial) * random.uniform(0.05, 0.2)  # Between 5% and 20% of the budget\par
\par
            # Generate change requests\par
            num_solicitacoes = random.randint(1, 5)\par
            solicitacoes_mudanca = []\par
            # for j in range(num_solicitacoes):\par
            #     solicitacoes_mudanca.append(f"SCM-\{j+1:02d\}: \{random.choice([\par
            #         'Adi\'e7\'e3o de funcionalidade de autentica\'e7\'e3o biom\'e9trica',\par
            #         'Altera\'e7\'e3o na interface do usu\'e1rio',\par
            #         'Integra\'e7\'e3o com sistema legado',\par
            #         'Mudan\'e7a no banco de dados',\par
            #         'Adi\'e7\'e3o de relat\'f3rios gerenciais',\par
            #         'Implementa\'e7\'e3o de m\'f3dulo de exporta\'e7\'e3o de dados',\par
            #         'Altera\'e7\'e3o nos requisitos de desempenho',\par
            #         'Mudan\'e7a na arquitetura do sistema'])\})")\par
            \par
\par
            for j in range(num_solicitacoes):\par
              solicitacao = random.choice([\par
               'Adi\'e7\'e3o de funcionalidade de autentica\'e7\'e3o biom\'e9trica',\par
               'Altera\'e7\'e3o na interface do usu\'e1rio',\par
               'Integra\'e7\'e3o com sistema legado',\par
               'Mudan\'e7a no banco de dados',\par
               'Adi\'e7\'e3o de relat\'f3rios gerenciais',\par
               'Implementa\'e7\'e3o de m\'f3dulo de exporta\'e7\'e3o de dados',\par
               'Altera\'e7\'e3o nos requisitos de desempenho',\par
               'Mudan\'e7a na arquitetura do sistema'\par
              ])\par
              solicitacoes_mudanca.append(f"SCM-\{j+1:02d\}: \{solicitacao\}")\par
\par
\par
        else:\par
            descricao_mudancas = "N/A"\par
            impacto_cronograma = 0\par
            impacto_custo = 0\par
            solicitacoes_mudanca = []\par
\par
        # Generate requirements\par
        num_requisitos = random.randint(5, 15)\par
        requisitos = []\par
        for j in range(num_requisitos):\par
            requisitos.append(fREQ-\{j+1:02d\}: \{random.choice([\par
                'O sistema deve permitir autentica\'e7\'e3o de usu\'e1rios',\par
                'O sistema deve processar transa\'e7\'f5es em menos de 2 seconds',\par
                'O sistema deve ser compat\'edvel com navegadores modernos',\par
                'O sistema deve permitir exporta\'e7\'e3o de dados em formato CSV',\par
                'O sistema deve implementar criptografia de dados sens\'edveis',\par
                'O sistema deve ter interface responsiva',\par
                'O sistema deve permitir integra\'e7\'e3o com APIs externas',\par
                'O sistema deve ter backup autom\'e1tico di\'e1rio',\par
                'O sistema deve ter controle de acesso baseado em perfis',\par
                'O sistema deve registrar logs de auditoria',\par
                'O sistema deve ter alta disponibilidade (99.9%)',\par
                'O sistema deve ser escal\'e1vel para suportar at\'e9 10.000 usu\'e1rios simult\'e2neos',\par
                'O sistema deve ter documenta\'e7\'e3o completa',\par
                'O sistema deve passar por testes de seguran\'e7a',\par
                'O sistema deve ser compat\'edvel com dispositivos m\'f3veis'\par
            ])\})\par
\par
        # Generate risks\par
        num_riscos = random.randint(3, 10)\par
        riscos = []\par
        for j in range(num_riscos):\par
            probabilidade = random.randint(1, 5)\par
            impacto = random.randint(1, 5)\par
            nivel = "Baixo" if probabilidade * impacto <= 6 else "M\'e9dio" if probabilidade * impacto <= 15 else "Alto"\par
\par
            riscos.append(\{\par
                "id": f"R\{j+1:02d\}",\par
                "descricao": random.choice([\par
                    "Atraso na entrega de componentes cr\'edticos",\par
                    "Rotatividade de pessoal-chave",\par
                    "Mudan\'e7as regulat\'f3rias",\par
                    "Problemas de integra\'e7\'e3o com sistemas legados",\par
                    "Falhas de seguran\'e7a",\par
                    "Indisponibilidade de recursos especializados",\par
                    "Problemas de desempenho",\par
                    "Falhas em testes de aceita\'e7\'e3o",\par
                    "Resist\'eancia dos usu\'e1rios \'e0 mudan\'e7a",\par
                    "Problemas de compatibilidade",\par
                    "Falhas de infraestrutura",\par
                    "Depend\'eancias externas n\'e3o cumpridas",\par
                    "Estimativas imprecisas",\par
                    "Requisitos mal definidos",\par
                    "Problemas de comunica\'e7\'e3o com stakeholders"\par
                ]),\par
                "probabilidade": probabilidade,\par
                "impacto": impacto,\par
                "nivel": nivel,\par
                "plano_mitigacao": random.choice([\par
                    "Implementar plano de conting\'eancia",\par
                    "Contratar pessoal adicional",\par
                    "Monitorar mudan\'e7as regulat\'f3rias",\par
                    "Realizar testes de integra\'e7\'e3o antecipados",\par
                    "Fortalecer medidas de seguran\'e7a",\par
                    "Buscar fornecedores alternativos",\par
                    "Otimizar c\'f3digo e infraestrutura",\par
                    "Realizar testes de aceita\'e7\'e3o com usu\'e1rios-chave",\par
                    "Comunicar benef\'edcios da mudan\'e7a",\par
                    "Testar compatibilidade em diferentes ambientes",\par
                    "Implementar redund\'e2ncia de infraestrutura",\par
                    "Gerenciar depend\'eancias ativamente",\par
                    "Refinar estimativas com base em dados hist\'f3ricos",\par
                    "Melhorar a documenta\'e7\'e3o de requisitos",\par
                    "Estabelecer canais de comunica\'e7\'e3o claros"\par
                ])\par
            \})\par
\par
        # Generate stakeholders\par
        num_stakeholders = random.randint(3, 8)\par
        stakeholders = []\par
        for j in range(num_stakeholders):\par
            stakeholders.append(\{\par
                "nome": fake.name(),\par
                "papel": random.choice([\par
                    "Patrocinador",\par
                    "Gerente de \'c1rea",\par
                    "Usu\'e1rio Final",\par
                    "Equipe de Desenvolvimento",\par
                    "Fornecedor",\par
                    "Regulador",\par
                    "Consultor",\par
                    "Analista de Neg\'f3cios"\par
                ]),\par
                "interesse": random.choice([\par
                    "Alto",\par
                    "M\'e9dio",\par
                    "Baixo"\par
                ]),\par
                "influencia": random.choice([\par
                    "Alto",\par
                    "M\'e9dio",\par
                    "Baixo"\par
                ])\par
            \})\par
\par
        # Generate communication plan\par
        num_comunicacoes = random.randint(2, 5)\par
        plano_comunicacao = []\par
        for j in range(num_comunicacoes):\par
            plano_comunicacao.append(\{\par
                "tipo": random.choice([\par
                    "Reuni\'e3o de Status",\par
                    "Relat\'f3rio Semanal",\par
                    "Email",\par
                    "Apresenta\'e7\'e3o",\par
                    "Workshop"\par
                ]),\par
                "frequencia": random.choice([\par
                    "Di\'e1ria",\par
                    "Semanal",\par
                    "Quinzenal",\par
                    "Mensal"\par
                ]),\par
                "audiencia": random.choice([\par
                    "Equipe do Projeto",\par
                    "Stakeholders Chave",\par
                    "Ger\'eancia",\par
                    "Todos os Envolvidos"\par
                ]),\par
                "responsavel": fake.name()\par
            \})\par
\par
        # Generate quality metrics\par
        num_metricas_qualidade = random.randint(3, 7)\par
        metricas_qualidade = []\par
        for j in range(num_metricas_qualidade):\par
            metricas_qualidade.append(\{\par
                "metrica": random.choice([\par
                    "N\'famero de Defeitos por Itera\'e7\'e3o",\par
                    "Tempo M\'e9dio para Corre\'e7\'e3o de Defeitos",\par
                    "Satisfa\'e7\'e3o do Cliente",\par
                    "Cobertura de Testes",\par
                    "N\'famero de Bugs Cr\'edticos",\par
                    "Tempo de Resposta do Sistema",\par
                    "Disponibilidade do Sistema"\par
                ]),\par
                "valor_atual": round(random.uniform(0.5, 100.0), 2),\par
                "meta": round(random.uniform(1.0, 95.0), 2)\par
            \})\par
\par
        # Generate resource allocation\par
        num_recursos = random.randint(5, 15)\par
        alocacao_recursos = []\par
        for j in range(num_recursos):\par
            alocacao_recursos.append(\{\par
                "recurso": fake.name() if random.random() > 0.3 else fake.job(),\par
                "tipo": random.choice([\par
                    "Pessoa",\par
                    "Equipamento",\par
                    "Software"\par
                ]),\par
                "alocacao_percentual": random.randint(20, 100),\par
                "custo_hora": round(random.uniform(20.0, 200.0), 2)\par
            \})\par
\par
        # Generate dependencies\par
        num_dependencias = random.randint(0, 5)\par
        dependencias = []\par
        if num_dependencias > 0 and i > 0: # Avoid dependencies on the first project\par
            for j in range(num_dependencias):\par
                dependencia_id = f"PROJ-\{random.randint(1, i):04d\}"\par
                dependencias.append(\{\par
                    "projeto_dependente_id": projeto_id,\par
                    "projeto_dependencia_id": dependencia_id,\par
                    "tipo": random.choice([\par
                        "T\'e9rmino para In\'edcio",\par
                        "In\'edcio para In\'edcio",\par
                        "T\'e9rmino para T\'e9rmino"\par
                    ]),\par
                    "descricao": random.choice([\par
                        f"Requer a conclus\'e3o do projeto \{dependencia_id\}",\par
                        f"Requer o in\'edcio do projeto \{dependencia_id\}",\par
                        f"Requer a conclus\'e3o simult\'e2nea com o projeto \{dependencia_id\}"\par
                    ])\par
                \})\par
\par
        # Generate lessons learned\par
        num_licoes = random.randint(0, 3)\par
        licoes_aprendidas = []\par
        if num_licoes > 0:\par
            for j in range(num_licoes):\par
                licoes_aprendidas.append(\{\par
                    "licao": random.choice([\par
                        "A comunica\'e7\'e3o proativa com stakeholders \'e9 crucial.",\par
                        "A gest\'e3o de riscos deve ser cont\'ednua.",\par
                        "A defini\'e7\'e3o clara do escopo evita retrabalho.",\par
                        "A aloca\'e7\'e3o adequada de recursos impacta o cronograma.",\par
                        "Testes cont\'ednuos melhoram a qualidade.",\par
                        "A colabora\'e7\'e3o entre equipes \'e9 fundamental.",\par
                        "A documenta\'e7\'e3o detalhada facilita a manuten\'e7\'e3o.",\par
                        "A adapta\'e7\'e3o a mudan\'e7as \'e9 necess\'e1ria."\par
                    ]),\par
                    "categoria": random.choice([\par
                        "Processo",\par
                        "Pessoas",\par
                        "T\'e9cnico",\par
                        "Comunica\'e7\'e3o"\par
                    ])\par
                \})\par
\par
        # Generate occurred risks\par
        riscos_ocorridos = []\par
        if random.random() < 0.4:  # 40% chance of having occurred risks\par
            num_riscos_ocorridos = random.randint(1, min(3, len(riscos)))\par
            riscos_selecionados = random.sample(riscos, num_riscos_ocorridos)\par
\par
            for risco in riscos_selecionados:\par
                data_ocorrencia = fake.date_between(start_date=data_inicio, end_date=datetime.now().date())\par
\par
                riscos_ocorridos.append(\{\par
                    "id": risco["id"],\par
                    "data": data_ocorrencia.strftime("%d/%m/%Y"),\par
                    "impacto_real": random.choice([\par
                        "Atraso de 2 semanas no cronograma",\par
                        "Aumento de 10% nos custos",\par
                        "Redu\'e7\'e3o de funcionalidades",\par
                        "Problemas de qualidade",\par
                        "Insatisfa\'e7\'e3o dos stakeholders",\par
                        "Retrabalho significativo",\par
                        "Perda de dados",\par
                        "Indisponibilidade tempor\'e1ria",\par
                        "Falhas de seguran\'e7a",\par
                        "Perda de recursos-chave"\par
                    ]),\par
                    "acoes_tomadas": random.choice([\par
                        "Implementa\'e7\'e3o do plano de conting\'eancia",\par
                        "Realoca\'e7\'e3o de recursos",\par
                        "Ajuste no cronograma",\par
                        "Revis\'e3o do or\'e7amento",\par
                        "Contrata\'e7\'e3o de recursos adicionais",\par
                        "Implementa\'e7\'e3o de controles adicionais",\par
                        "Revis\'e3o de processos",\par
                        "Comunica\'e7\'e3o intensificada com stakeholders",\par
                        "Revis\'e3o de prioridades",\par
                        "Implementa\'e7\'e3o de solu\'e7\'f5es alternativas"\par
                    ])\par
                \})\par
\par
        # Generate critical and delayed tasks\par
        num_tarefas_criticas = random.randint(3, 8)\par
        tarefas_criticas = []\par
        for j in range(num_tarefas_criticas):\par
            tarefas_criticas.append(random.choice([\par
                "Desenvolvimento do m\'f3dulo de autentica\'e7\'e3o",\par
                "Integra\'e7\'e3o com sistema de pagamentos",\par
                "Implementa\'e7\'e3o do m\'f3dulo de relat\'f3rios",\par
                "Migra\'e7\'e3o de dados legados",\par
                "Testes de seguran\'e7a",\par
                "Implementa\'e7\'e3o da API REST",\par
                "Desenvolvimento da interface do usu\'e1rio",\par
                "Configura\'e7\'e3o da infraestrutura",\par
                "Implementa\'e7\'e3o do m\'f3dulo de notifica\'e7\'f5es",\par
                "Testes de aceita\'e7\'e3o do usu\'e1rio",\par
                "Implementa\'e7\'e3o do m\'f3dulo de an\'e1lise de dados",\par
                "Desenvolvimento do painel administrativo",\par
                "Implementa\'e7\'e3o do sistema de backup",\par
                "Configura\'e7\'e3o do ambiente de produ\'e7\'e3o",\par
                "Implementa\'e7\'e3o do m\'f3dulo de exporta\'e7\'e3o de dados"\par
            ]))\par
\par
        tarefas_atrasadas = []\par
        if status == 'Atrasado':\par
            num_tarefas_atrasadas = random.randint(1, min(3, len(tarefas_criticas)))\par
            tarefas_atrasadas = random.sample(tarefas_criticas, num_tarefas_atrasadas)\par
\par
        # Reason for delay\par
        if status == 'Atrasado':\par
            motivo_atraso = random.choice([\par
                "Atraso na entrega de componentes por fornecedores",\par
                "Problemas t\'e9cnicos inesperados",\par
                "Rotatividade de pessoal-chave",\par
                "Mudan\'e7as de requisitos n\'e3o planejadas",\par
                "Estimativas imprecisas",\par
                "Depend\'eancias externas n\'e3o cumpridas",\par
                "Problemas de integra\'e7\'e3o com sistemas legados",\par
                "Falhas em testes de aceita\'e7\'e3o",\par
                "Recursos insuficientes",\par
                "Problemas de comunica\'e7\'e3o"\par
            ])\par
        else:\par
            motivo_atraso = "N/A"\par
\par
        # Compile project information\par
        projeto = \{\par
            "id": projeto_id,\par
            "nome": fake.catch_phrase(),\par
            "data_inicio": data_inicio.strftime("%d/%m/%Y"),\par
            "data_termino_planejada": data_termino_planejada.strftime("%d/%m/%Y"),\par
            "data_termino_real": data_termino_real.strftime("%d/%m/%Y"),\par
            "duracao_planejada": duracao_planejada,\par
            "orcamento_inicial": orcamento_inicial,\par
            "gerente": gerente,\par
            "status": status,\par
            "percentual_conclusao": percentual_conclusao,\par
            "atraso_atual": atraso_atual,\par
            "motivo_atraso": motivo_atraso,\par
            "valor_planejado": pv,\par
            "valor_agregado": ev,\par
            "custo_real_atual": ac,\par
            "spi": spi,\par
            "cpi": cpi,\par
            "estimativa_custo_conclusao": etc,\par
            "estimativa_final_projeto": eac,\par
            "variacao_final_projeto": vac,\par
            "desvio_orcamento": desvio_orcamento,\par
            "categorias_custos": categorias_custos,\par
            "mudanca_escopo": mudanca_escopo,\par
            "descricao_mudancas": descricao_mudancas,\par
            "impacto_cronograma": impacto_cronograma,\par
            "impacto_custo": impacto_custo,\par
            "solicitacoes_mudanca": solicitacoes_mudanca,\par
            "requisitos": requisitos,\par
            "tarefas_criticas": tarefas_criticas,\par
            "tarefas_atrasadas": tarefas_atrasadas,\par
            "riscos": riscos,\par
            "riscos_ocorridos": riscos_ocorridos\par
        \}\par
\par
        projetos.append(projeto)\par
\par
    # Save dataset in JSON format\par
    with open(os.path.join(output_dir, "projetos.json"), 'w', encoding='utf-8') as f:\par
        json.dump(projetos, f, ensure_ascii=False, indent=2)\par
\par
    # Save dataset in CSV format (main data only)\par
    df_projetos = pd.DataFrame([\{\par
        "id": p["id"],\par
        "nome": p["nome"],\par
        "data_inicio": p["data_inicio"],\par
        "data_termino_planejada": p["data_termino_planejada"],\par
        "data_termino_real": p["data_termino_real"],\par
        "orcamento_inicial": p["orcamento_inicial"],\par
        "gerente": p["gerente"],\par
        "status": p["status"],\par
        "percentual_conclusao": p["percentual_conclusao"],\par
        "spi": p["spi"],\par
        "cpi": p["cpi"],\par
        "mudanca_escopo": p["mudanca_escopo"]\par
    \} for p in projetos])\par
\par
    df_projetos.to_csv(os.path.join(output_dir, "projetos.csv"), index=False)\par
\par
    # Generate status files for each project\par
    os.makedirs(os.path.join(output_dir, "status_files"), exist_ok=True)\par
\par
    for projeto in projetos:\par
        # Schedule status file\par
        with open(os.path.join(output_dir, "status_files", f"\{projeto['id']\}_cronograma.txt"), 'w', encoding='utf-8') as f:\par
            f.write(f"RELAT\'d3RIO DE STATUS DE CRONOGRAMA\\n")\par
            f.write(f"Projeto: \{projeto['nome']\} (\{projeto['id']\})\\n")\par
            f.write(f"Data: \{datetime.now().strftime('%d/%m/%Y')\}\\n")\par
            f.write(f"Gerente: \{projeto['gerente']\}\\n\\n")\par
\par
            f.write(f"Status atual: \{projeto['status']\}\\n")\par
            f.write(f"Percentual de conclus\'e3o: \{projeto['percentual_conclusao']:.1f\}%\\n")\par
            f.write(f"Data de in\'edcio: \{projeto['data_inicio']\}\\n")\par
            f.write(f"Data de t\'e9rmino planejada: \{projeto['data_termino_planejada']\}\\n")\par
            f.write(f"Data de t\'e9rmino real/prevista: \{projeto['data_termino_real']\}\\n")\par
            f.write(f"Atraso atual: \{projeto['atraso_atual']\} dias\\n")\par
            f.write(f"Motivo do atraso: \{projeto['motivo_atraso']\}\\n")\par
            f.write(f"\'cdndice de Desempenho de Cronograma (SPI): \{projeto['spi']:.2f\}\\n")\par
            f.write(f"Valor Planejado (PV): R$ \{projeto['valor_planejado']:.2f\}\\n")\par
            f.write(f"Valor Agregado (EV): R$ \{projeto['valor_agregado']:.2f\}\\n\\n")\par
\par
            f.write(f"Tarefas cr\'edticas:\\n")\par
            for tarefa in projeto['tarefas_criticas']:\par
                f.write(f"- \{tarefa\}\\n")\par
\par
            f.write(f"\\nTarefas atrasadas:\\n")\par
            for tarefa in projeto['tarefas_atrasadas']:\par
                f.write(f"- \{tarefa\}\\n")\par
\par
        # Cost status file\par
        with open(os.path.join(output_dir, "status_files", f"\{projeto['id']\}_custos.txt"), 'w', encoding='utf-8') as f:\par
            f.write(f"RELAT\'d3RIO DE STATUS DE CUSTOS\\n")\par
            f.write(f"Projeto: \{projeto['nome']\} (\{projeto['id']\})\\n")\par
            f.write(f"Data: \{datetime.now().strftime('%d/%m/%Y')\}\\n")\par
            f.write(f"Gerente: \{projeto['gerente']\}\\n\\n")\par
\par
            f.write(f"Or\'e7amento inicial: R$ \{projeto['orcamento_inicial']:.2f\}\\n")\par
            f.write(f"Custo real atual: R$ \{projeto['custo_real_atual']:.2f\}\\n")\par
            f.write(f"Desvio or\'e7ament\'e1rio: \{projeto['desvio_orcamento']:.2f\}%\\n")\par
            f.write(f"\'cdndice de Desempenho de Custo (CPI): \{projeto['cpi']:.2f\}\\n")\par
            f.write(f"Valor Agregado (EV): R$ \{projeto['valor_agregado']:.2f\}\\n")\par
            f.write(f"Estimativa para conclus\'e3o: R$ \{projeto['estimativa_custo_conclusao']:.2f\}\\n")\par
            f.write(f"Estimativa no t\'e9rmino (EAC): R$ \{projeto['estimativa_final_projeto']:.2f\}\\n")\par
            f.write(f"Varia\'e7\'e3o no t\'e9rmino (VAC): R$ \{projeto['variacao_final_projeto']:.2f\}\\n\\n")\par
\par
            f.write(f"Detalhamento por categoria:\\n")\par
            for categoria, valor in projeto['categorias_custos'].items():\par
                percentual = valor / float(projeto['custo_real_atual']) * 100\par
                f.write(f"- \{categoria\}: R$ \{valor:.2f\} (\{percentual:.1f\}%)\\n")\par
\par
        # Scope status file\par
        with open(os.path.join(output_dir, "status_files", f"\{projeto['id']\}_escopo.txt"), 'w', encoding='utf-8') as f:\par
            f.write(f"RELAT\'d3RIO DE STATUS DE ESCOPO\\n")\par
            f.write(f"Projeto: \{projeto['nome']\} (\{projeto['id']\})\\n")\par
            f.write(f"Data: \{datetime.now().strftime('%d/%m/%Y')\}\\n")\par
            f.write(f"Gerente: \{projeto['gerente']\}\\n\\n")\par
\par
            f.write(f"Escopo original: Sistema para \{projeto['nome'].lower()\}\\n")\par
            f.write(f"Houve mudan\'e7a de escopo: \{projeto['mudanca_escopo']\}\\n")\par
            f.write(f"Descri\'e7\'e3o das mudan\'e7as: \{projeto['descricao_mudancas']\}\\n")\par
            f.write(f"Impacto no cronograma: \{projeto['impacto_cronograma']\} dias\\n")\par
            f.write(f"Impacto no custo: R$ \{projeto['impacto_custo']:.2f\}\\n\\n")\par
\par
            f.write(f"Solicita\'e7\'f5es de mudan\'e7a:\\n")\par
            for solicitacao in projeto['solicitacoes_mudanca']:\par
                f.write(f"- \{solicitacao\}\\n")\par
\par
            f.write(f"\\nRequisitos atuais:\\n")\par
            for requisito in projeto['requisitos']:\par
                f.write(f"- \{requisito\}\\n")\par
\par
        # Risk status file\par
        with open(os.path.join(output_dir, "status_files", f"\{projeto['id']\}_riscos.txt"), 'w', encoding='utf-8') as f:\par
            f.write(f"RELAT\'d3RIO DE STATUS DE RISCOS\\n")\par
            f.write(f"Projeto: \{projeto['nome']\} (\{projeto['id']\})\\n")\par
            f.write(f"Data: \{datetime.now().strftime('%d/%m/%Y')\}\\n")\par
            f.write(f"Gerente: \{projeto['gerente']\}\\n\\n")\par
\par
            f.write(f"Riscos identificados:\\n")\par
            for risco in projeto['riscos']:\par
                f.write(f"- \{risco['id']\}: \{risco['descricao']\}\\n")\par
                f.write(f"  Probabilidade: \{risco['probabilidade']\}/5, Impacto: \{risco['impacto']\}/5, N\'edvel: \{risco['nivel']\}\\n")\par
                f.write(f"  Mitiga\'e7\'e3o: \{risco['plano_mitigacao']\}\\n\\n")\par
\par
            f.write(f"Riscos ocorridos:\\n")\par
            for risco in projeto['riscos_ocorridos']:\par
                f.write(f"- \{risco['id']\} (ocorrido em \{risco['data']\})\\n")\par
                f.write(f"  Impacto real: \{risco['impacto_real']\}\\n")\par
                f.write(f"  A\'e7\'f5es tomadas: \{risco['acoes_tomadas']\}\\n\\n")\par
\par
    print(f"Dataset generated successfully! Files saved in \{output_dir\}")\par
    return projetos\par
\par
if __name__ == "__main__":\par
    # Generate dataset with 1000 projects\par
    gerar_dataset(num_projetos=1000)\par
\par
# To generate a smaller dataset for testing:\par
# gerar_dataset(num_projetos=10, output_dir="../test_dataset")\par
\par
# To generate the full dataset:\par
# gerar_dataset(num_projetos=1000)\par
}
 