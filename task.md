# Plano de Desenvolvimento Backend - Desafio Bemagro

### Sprint 1: Fundação e Infraestrutura Base
**Objetivo:** Levantar a aplicação FastAPI vazia, configurar ambiente Docker.

* **Task 1.3: Setup Docker (Multi-stage)**
  * Atualizar `.gitignore` para incluir arquivos e pastas necessárias no contexto do python com fastAPI
  * implementar `Dockerfile.dev` com hot-reload ativado para desenvolvimento.
  * implementar `Dockerfile.prod` otimizado para produção.
  * implementar `docker-compose.yml` subindo 3 serviços: `api`, `db` (SQLite é serverless, mas para facilitar o docker-compose, criar o mapeamento de volume) e `redis`.

### Sprint 2: Camada de Dados e Modelagem
**Objetivo:** Configurar o banco de dados e os modelos de domínio para o histórico.

* **Task 2.1: Setup do Banco de Dados**
  * Instalar `sqlalchemy` e `alembic`.
  * Configurar a conexão assíncrona com SQLite no diretório `/infrastructure/database`.
* **Task 2.2: Entidades e Repositório**
  * Criar o modelo SQLAlchemy `SearchHistory` contendo: `id` (PK), `city_name` (String), `latitude` (Float), `longitude` (Float), `created_at` (DateTime padrão UTC).
  * Criar a interface do repositório (`/domain`) e a implementação concreta (`/infrastructure`) com os métodos `save_search_history` e `get_recent_history` ordenado por data decrescente.
* **Task 2.3: Migrations**
  * Inicializar o Alembic e gerar a primeira migração para a tabela de histórico.

### Sprint 3: Integração OpenWeatherMap (O Core do Desafio)
**Objetivo:** Conectar com a API externa garantindo as regras de negócio e tratamento de erros.

* **Task 3.1: Cliente HTTP**
  * Instalar `httpx`.
  * Criar a classe `OpenWeatherClient` na `/infrastructure/services`.
  * Implementar o método de busca passando a URL base `https://api.openweathermap.org/data/2.5/weather`.
  * Garantir o envio dos query parameters obrigatórios: `q={city}`, `appid={API_KEY}`, `units=metric` (para Celsius) e `lang=pt_br` (para descrição em português).
* **Task 3.2: Parseamento e DTOs**
  * Criar modelos Pydantic para mapear apenas o que importa da API:
    * Temperatura (`main.temp`)
    * Sensação térmica (`main.feels_like`)
    * Umidade (`main.humidity`)
    * Velocidade do vento (`wind.speed`)
    * Descrição do clima (`weather[0].description`)
    * Latitude e longitude (`coord.lat`, `coord.lon`).
* **Task 3.3: Tratamento de Erros**
  * Implementar try/catch para capturar status 404 (Cidade Inexistente) e 401 (Problema na API Key) e retornar exceções HTTP personalizadas.

### Sprint 4: Endpoints da Aplicação (Presentation)
**Objetivo:** Expor as rotas exigidas no desafio conectando aos serviços criados.

* **Task 4.1: Endpoint de Clima**
  * Criar a rota `GET /api/weather?city={nome_da_cidade}`.
  * Fluxo: Validar o input -> Chamar o `OpenWeatherClient` -> Salvar os dados (Cidade, Lat, Lon) de forma assíncrona usando o repositório de histórico -> Retornar o DTO final.
* **Task 4.2: Endpoint de Histórico**
  * Criar a rota `GET /api/history`.
  * Fluxo: Chamar o repositório e retornar a lista dos últimos registros contendo nome, data/hora, lat e lon.
* **Task 4.3: Healthcheck**
  * Criar a rota `GET /api/status`.
  * Validar: Status da aplicação, ping simples no SQLite e ping no Redis.

### Sprint 5: Diferenciais e Qualidade (Opcional)
**Objetivo:** Implementar o over-delivery planejado sem quebrar o que já funciona.

* **Task 5.1: Redis Cache**
  * Instalar `redis-py`.
  * Implementar um decorator ou middleware de cache na rota `/api/weather` tendo o nome da cidade (normalizado) como chave. Configurar TTL para 15 minutos.
* **Task 5.2: Rate Limiting**
  * Instalar `slowapi` ou equivalente.
  * Limitar a rota de weather a `10/minute` por IP para proteger a chave do OpenWeatherMap.
* **Task 5.3: Testes Automatizados**
  * Instalar `pytest` e `pytest-asyncio`.
  * Criar Testes Unitários: Mockar o cliente do OpenWeather e testar as respostas e os erros (cidade não encontrada).
  * Criar Testes E2E: Usar `TestClient` para bater nas rotas `/api/weather` e `/api/history` com um banco de dados de teste em memória.
  * *Opcional:* Script `locustfile.py` simples para demonstração de conceito de teste de carga.