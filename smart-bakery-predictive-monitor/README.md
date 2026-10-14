# Smart Bakery Predictive Monitor

Projeto Integrador 4 — monitoramento preditivo de temperatura e umidade com dados IoT simulados.

## Tecnologias
- **FastAPI** para disponibilizar os dados por API
- **NumPy e Pandas** para gerar e tratar leituras simuladas
- **scikit-learn (Regressão Linear)** para estimar a tendência de temperatura
- **HTML, CSS, JavaScript e Chart.js** para visualizar histórico e previsões

## Como executar

Requer Python 3.10+.

1. Abra um terminal na pasta `backend`.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie a API:
   ```bash
   uvicorn app:app --reload
   ```
4. Abra `frontend/index.html` no navegador.

A API gera um conjunto inicial de 500 leituras simuladas ao iniciar. O botão **Gerar novas leituras** cria um novo conjunto. A documentação interativa da API fica em `http://127.0.0.1:8000/docs`.

## Endpoints
- `GET /health` — verifica se a API está ativa
- `GET /data` — retorna as 100 leituras mais recentes
- `GET /predict` — treina uma regressão linear com as 100 leituras mais recentes e prevê as próximas 10 leituras
- `POST /simulate` — gera um novo conjunto de dados

## Observação acadêmica
Os dados são sintéticos e servem para demonstrar o fluxo de coleta simulada, análise por aprendizagem de máquina e visualização. As previsões são demonstrações de tendência, não recomendações para operação real de uma padaria.
