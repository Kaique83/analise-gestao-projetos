# Projeto de Análise de Dados: Gestão de Projetos

Este repositório contém um projeto de análise de dados exploratória (EDA) realizado em um banco de dados de um sistema fictício de gestão de projetos. A análise foi desenvolvida utilizando Python em um ambiente Jupyter Notebook.

## Objetivo

O objetivo desta análise é extrair insights acionáveis sobre o portfólio de projetos, a distribuição da carga de trabalho entre a equipe e a eficiência operacional, respondendo a perguntas críticas de negócio através da visualização de dados.

## Ferramentas e Bibliotecas

* **Linguagem:** Python 3
* **Banco de Dados:** SQLite
* **Análise de Dados:** Pandas
* **Visualização:** Matplotlib, Seaborn
* **Ambiente:** Jupyter Notebook

## Como Executar a Análise

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Kaique83/A3UAM1-analise.git](https://github.com/Kaique83/A3UAM1-analise.git)
    cd A3UAM1-analise
    ```

2.  **Instale as dependências:**
    ```bash
    pip install pandas matplotlib seaborn jupyter
    ```

3.  **Popule o banco de dados (Opcional):**
    O repositório já contém um banco de dados (`gestao_projetos.db`) populado. Caso queira gerar novos dados, instale a biblioteca Faker (`pip install Faker`) e execute o script:
    ```bash
    python populate_db.py
    ```

4.  **Inicie o Jupyter Notebook:**
    ```bash
    python -m notebook
    ```

5.  No seu navegador, abra o arquivo `analise_projetos.ipynb` e execute as células.

## Principais Análises Realizadas

* Visão Geral do Status dos Projetos
* Análise de Carga de Trabalho Detalhada por Pessoa e Prioridade
* Distribuição de Projetos por Gerente
* Heatmap de Concentração de Tarefas por Status e Prioridade

---
*Esta análise foi realizada sobre os dados gerados pela aplicação de desktop para Gestão de Projetos, que pode ser encontrada [neste outro repositório](https://github.com/Kaique83/sistema-gestao-projetos).*