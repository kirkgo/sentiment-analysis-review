# Sentiment Analysis Review

## Introdução

Esta é uma solução que faz o scraping dos dados consolidados das ações da Bovespa (D-1), faz o ETL através do Glue e exibe os dados no Athena.

## Autor

- Kirk Patrick (MLET1 - Grupo 66)
- Você pode entrar em contato com o autor pelo LinkedIn: [https://www.linkedin.com/in/kirkgo/](https://www.linkedin.com/in/kirkgo/)

## Visão Geral

Este projeto consiste em duas aplicações:

- Sentiment Analysis
- Sentiment Dashboard

# 1. Sentiment Analysis

Esta API de Análise de Sentimentos é um backend em Python usando FastAPI. Ela permite a análise de sentimentos em textos, gerenciamento de avaliações e fornece estatísticas sobre os sentimentos analisados. A API é projetada para trabalhar com avaliações de produtos, com foco inicial em dados da Amazon.

Possui dois arquivos:

1. `train_sentiment_model.py`: Treina o modelo de machine learning para classificação de sentimentos.
2. `main.py`: Implementa os endpoints da API e a lógica de negócios.

## Instalação das Dependências

Antes de executar os scripts, é necessário instalar as dependências do projeto. Siga os passos abaixo para configurar o ambiente:

1. Certifique-se de ter o Python 3.9 ou superior instalado. Você pode verificar a versão do Python com o comando:

   ```bash
   python --version
   ```

2. Recomenda-se criar um ambiente virtual para isolar as dependências do projeto. Para criar e ativar um ambiente virtual, execute:

   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, use: venv\Scripts\activate
   ```

3. Com o ambiente virtual ativado, instale as dependências usando o pip. Crie um arquivo `requirements.txt` com o seguinte conteúdo:

   ```
   pandas
   numpy
   scikit-learn
   joblib
   seaborn
   matplotlib
   fastapi
   sqlalchemy
   pydantic
   uvicorn
   ```

4. Instale as dependências executando:

   ```bash
   pip install -r requirements.txt
   ```

5. Verifique se todas as dependências foram instaladas corretamente:
   ```bash
   pip list
   ```

Agora que as dependências estão instaladas, você pode prosseguir com a execução dos scripts.

## 1. Script de Treinamento do Modelo (train_sentiment_model.py)

### Objetivo

Treinar um modelo de análise de sentimentos usando avaliações da Amazon e salvar o modelo treinado para uso posterior.

### Principais Funcionalidades

- Carrega dados de avaliações da Amazon de um arquivo CSV.
- Pré-processa os dados, incluindo a classificação de sentimentos baseada na pontuação.
- Adiciona exemplos neutros para balancear o conjunto de dados.
- Utiliza TF-IDF para vetorização de texto.
- Treina um modelo de Regressão Logística para classificação de sentimentos.
- Avalia o modelo usando validação cruzada e métricas de classificação.
- Salva o modelo treinado, o vetorizador e o codificador de rótulos para uso futuro.

### Uso

Execute o script para treinar o modelo e salvá-lo:

```bash
python train_sentiment_model.py
```

## 2. API FastAPI (main.py)

### Objetivo

Implementar uma API RESTful para análise de sentimentos e gerenciamento de avaliações usando o modelo treinado.

### Principais Funcionalidades

- Análise de sentimentos de textos usando o modelo treinado.
- CRUD (Create, Read, Update, Delete) para avaliações.
- Carregamento de dados de avaliações de um arquivo CSV para o banco de dados.
- Cálculo e atualização de estatísticas de sentimentos.

### Rotas Principais

1. `/analyze-sentiment`: Analisa o sentimento de um texto fornecido.
2. `/load-data`: Carrega dados de avaliações do CSV para o banco de dados.
3. `/reviews`: Gerencia operações CRUD para avaliações.
4. `/update-stats`: Atualiza estatísticas de sentimentos.
5. `/sentiment-stats`: Retorna estatísticas de sentimentos.

### Configuração do Banco de Dados

- Utiliza SQLite como banco de dados (`amazon_reviews.db`).
- Define modelos para avaliações (`Review`) e estatísticas de sentimentos (`SentimentStats`).

### Uso

Para iniciar a API, execute:

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## Observações Importantes

- O modelo de análise de sentimentos é treinado com dados específicos da Amazon, o que pode influenciar sua performance em outros domínios.
- A API inclui middleware CORS configurado para permitir requisições de `http://localhost:3000`.
- As estatísticas de sentimentos são inicializadas na inicialização da aplicação.

# 2. Sentiment Dashboard

O Sentiment Dashboard é uma aplicação web desenvolvida com Next.js e React que consome a API de análise de sentimentos previamente documentada. Esta aplicação fornece uma interface gráfica para visualizar estatísticas de sentimentos e analisar novos textos em tempo real.

## Estrutura do Projeto

O projeto consiste em dois arquivos principais:

1. `package.json`: Define as dependências e scripts do projeto.
2. `index.tsx`: Contém o componente principal do dashboard.

## Dependências

As principais dependências do projeto incluem:

- Next.js (14.2.13)
- React (18)
- Recharts (2.12.7)
- Várias dependências UI como @radix-ui/react-slot, class-variance-authority, etc.

Para uma lista completa, consulte o arquivo `package.json`.

## Instalação e Configuração

Para configurar e executar o Sentiment Dashboard, siga estes passos:

1. Certifique-se de ter o Node.js instalado (versão 14 ou superior recomendada).

2. Clone o repositório do projeto (substitua `[URL_DO_REPOSITÓRIO]` pela URL real):

   ```bash
   git clone [URL_DO_REPOSITÓRIO]
   cd sentiment-dashboard
   ```

3. Instale as dependências:

   ```bash
   npm install
   ```

4. Inicie o servidor de desenvolvimento:

   ```bash
   npm run dev
   ```

5. Abra um navegador e acesse `http://localhost:3000` para ver o dashboard.

## Estrutura do Componente Principal (index.tsx)

O arquivo `index.tsx` contém o componente `SentimentDashboard`, que é responsável por toda a funcionalidade do dashboard. Aqui está uma visão geral de suas principais características:

### Estado

- `stats`: Armazena as estatísticas gerais de sentimentos.
- `text`: Armazena o texto inserido pelo usuário para análise.
- `sentiment`: Armazena o resultado da análise de sentimento.
- `error`: Gerencia mensagens de erro.
- `loading`: Indica quando uma análise está em andamento.

### Funções Principais

- `fetchStats()`: Busca as estatísticas de sentimentos da API.
- `updateLocalStats()`: Atualiza as estatísticas locais após uma nova análise.
- `updateServerStats()`: Envia atualizações de estatísticas para o servidor.
- `analyzeSentiment()`: Envia o texto para análise na API e atualiza o estado.

### Componentes UI

- Gráficos (PieChart e BarChart) para visualização de estatísticas.
- Formulário para inserção de texto e botão de análise.
- Cards para exibição de resultados e estatísticas.

## Fluxo de Uso

1. Ao carregar, o dashboard busca as estatísticas gerais de sentimentos.
2. O usuário pode inserir um texto na área de texto.
3. Ao clicar em "Analyze", o texto é enviado para a API.
4. O resultado da análise é exibido e as estatísticas são atualizadas localmente e no servidor.

## Personalização

- As cores dos sentimentos são definidas no objeto `SENTIMENT_COLORS`.
- O layout e estilos utilizam Tailwind CSS para fácil personalização.

## Observações Importantes

- O dashboard assume que a API está rodando em `http://localhost:8000`. Ajuste a URL se necessário.
- Tratamento de erros básico está implementado, mas pode ser expandido para casos de uso específicos.

## Considerações Finais

O projeto Sentiment Analysis Review, composto pela API backend em FastAPI e pelo Dashboard frontend em Next.js/React, oferece uma solução completa e integrada para a análise e visualização de sentimentos em avaliações de produtos.
