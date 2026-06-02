# 🔍 Crime & Public Security Analytics Platform

A comprehensive **Big Data** platform for analyzing crime and public security data, built as a distributed, microservices-based architecture. The system implements a full data pipeline — from raw CSV ingestion through real-time Change Data Capture (CDC) streaming, into an OLAP data warehouse — culminating in machine learning-driven insights and an interactive web dashboard for decision support.

> **Course:** Big Data Analysis and Business Intelligence  
> **Institution:** Ho Chi Minh City University of Technology (HCMUT)

---

## 📑 Table of Contents

- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Data Pipeline Overview](#-data-pipeline-overview)
- [Project Structure](#-project-structure)
- [Database Design](#-database-design)
- [Services](#-services)
  - [Data Ingestion Service](#1-data-ingestion-service-services-ingestion)
  - [ETL Pipeline Service](#2-etl-pipeline-service-servicesetl-pipeline)
  - [Machine Learning Service](#3-machine-learning-service-servicesml-service)
  - [Web API Service](#4-web-api-service-servicesweb-api)
  - [Web Frontend Service](#5-web-frontend-service-servicesweb-frontend)
- [Infrastructure Components](#-infrastructure-components)
- [Shell Scripts](#-shell-scripts)
- [Environment Variables](#-environment-variables)
- [Getting Started](#-getting-started)
- [Port Reference](#-port-reference)
- [Java Dependencies (JARs)](#-java-dependencies-jars)

---

## 🏗 System Architecture

The system is designed as a distributed, microservices-based architecture. Data flows from an initial ingestion point through a processing pipeline and into a data warehouse, where it is then consumed by a machine learning service and a web frontend.

```
┌──────────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────────┐
│  Raw CSV     │────▶│  Preprocessing│────▶│ PostgreSQL│────▶│   Debezium   │
│  (crime data)│     │  (pandas)     │     │ (OLTP)    │     │   (CDC)      │
└──────────────┘     └──────────────┘     └───────────┘     └──────┬───────┘
                                                                    │
                                                                    ▼
┌──────────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────────┐
│  Web         │◀────│  Web API     │◀────│ ClickHouse│◀────│ Spark        │
│  Frontend    │     │  (FastAPI)   │     │ (OLAP DW) │     │ Streaming    │
│  (ReactJS)   │     │              │◀──┐ └───────────┘     └──────────────┘
└──────────────┘     └──────────────┘   │                         ▲
                                        │                         │
                                   ┌────┴──────┐          ┌──────┴───────┐
                                   │ ML Service│          │    Kafka     │
                                   │ (FastAPI) │          │   (Broker)   │
                                   └───────────┘          └──────────────┘
```

### Components

| Component | Technology | Role |
|---|---|---|
| **Data Preprocessing** | Python (pandas, psycopg2) | Reads raw CSV, cleans data, normalizes into relational tables, inserts into PostgreSQL |
| **Primary Data Store** | PostgreSQL | Stores normalized OLTP data (operational source-of-truth) |
| **CDC Connector** | Debezium 2.4 | Captures row-level changes from PostgreSQL via logical replication (`pgoutput`) |
| **Message Broker** | Apache Kafka (Confluent 7.5.0) | Streams CDC events as topics (one per table) |
| **Stream Processing** | Apache Spark 3.5.0 (Structured Streaming) | Consumes Kafka topics, transforms CDC events, loads into ClickHouse star schema |
| **Data Warehouse** | ClickHouse 23.8 | Columnar OLAP store for high-performance analytical queries |
| **ML Service** | FastAPI + scikit-learn / PyTorch / TensorFlow | Crime classification, clustering, and seasonal forecasting |
| **Web API** | FastAPI | Backend-for-Frontend querying ClickHouse and ML Service |
| **Web Frontend** | ReactJS | Interactive dashboards, charts, and maps |
| **Orchestration** | Docker Compose 3.8 | Multi-container orchestration for local development |

---

## 🛠 Technology Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.9 / 3.11 / 3.12, JavaScript (React), SQL |
| **Big Data** | Apache Spark 3.5.0 (PySpark), Kafka 7.5.0, Zookeeper |
| **Databases** | PostgreSQL (OLTP), ClickHouse 23.8 (OLAP) |
| **CDC** | Debezium 2.4 (PostgreSQL connector with `pgoutput` plugin) |
| **ML/AI** | scikit-learn, PyTorch, TensorFlow |
| **Web** | FastAPI (Python), ReactJS, D3.js/Chart.js |
| **Data Processing** | pandas, PySpark, clickhouse-connect |
| **Containerization** | Docker, Docker Compose |
| **Monitoring** | Kafka UI (Provectus), Spark Master Web UI |

---

## 🔄 Data Pipeline Overview

The platform implements **two ETL modes** — a batch pipeline and a real-time streaming pipeline:

### Mode 1: Batch ETL (`batch_etl.py`)

1. Reads raw CSV file (`data/raw/crime_data.csv`) using PySpark
2. Cleans and transforms data (date parsing, null handling, type casting)
3. Generates dimension tables (`dim_date`, `dim_time`, `dim_primary_type`, `dim_crime`, `dim_location`, `dim_patrol_unit`)
4. Builds the fact table (`fact_case`) by joining with all dimensions
5. Outputs processed CSV files to `data/processed/`

### Mode 2: Real-Time Streaming ETL (`preprocessing.py` → `etl.py`)

1. **Preprocessing** (`preprocessing.py`): Reads raw CSV, cleans data with pandas, inserts into **PostgreSQL** (normalized OLTP schema)
2. **Debezium CDC**: Captures inserts/updates/deletes from PostgreSQL and publishes them to **Kafka topics** (one per table)
3. **Spark Structured Streaming** (`etl.py`): Subscribes to 5 CDC topics, parses JSON events, maps data into star schema format, and writes to **ClickHouse**

```
CSV ──▶ pandas ──▶ PostgreSQL ──▶ Debezium CDC ──▶ Kafka Topics ──▶ Spark Streaming ──▶ ClickHouse
                                                                                         │
                                                                                    Star Schema
                                                                                   (OLAP Queries)
```

### Kafka Topics (CDC)

| Topic | Source Table | Target Table |
|---|---|---|
| `cdc.public.primary_type` | `primary_type` | `dim_primary_type` |
| `cdc.public.crime` | `crime` | `dim_crime` |
| `cdc.public.location` | `location` | `dim_location` |
| `cdc.public.patrol_unit` | `patrol_unit` | `dim_patrol_unit` |
| `cdc.public.case_report` | `case_report` | `fact_case` + `dim_date` + `dim_time` |

---

## 📁 Project Structure

```
Public-Safety-Crime-Analytics/
├── .dockerignore                   # Docker build exclusions
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── docker-compose.yml              # Multi-container orchestration (10 services)
├── Dockerfile                      # Spark cluster image (Python 3.11 on Spark 3.5.0)
├── requirements.txt                # Root-level Python dependencies
├── run_streaming.sh                # Script to submit Spark streaming job
├── running.sh                      # Script to initialize ClickHouse tables
├── stream_data.csv                 # Raw crime dataset (~38 MB)
│
├── data/
│   ├── raw/                        # Raw input CSV files
│   ├── processed/                  # Output from batch ETL (dimension & fact CSVs)
│   └── crime_analytics/            # ClickHouse local data files
│
├── docs/
│   ├── architecture.md             # System architecture documentation
│   ├── ADR/
│   │   └── adr_template.md         # Architecture Decision Record template
│   └── api/
│       └── openapi.md              # OpenAPI specifications for Web API & Ingestion API
│
├── infra/
│   ├── clickhouse/
│   │   └── init.sql                # ClickHouse DDL (star schema tables)
│   ├── debezium/
│   │   └── config.json             # Debezium PostgreSQL connector configuration
│   ├── postgresql/
│   │   └── init.sql                # PostgreSQL DDL (normalized OLTP schema with indexes)
│   ├── kafka/                      # Kafka configuration (placeholder)
│   ├── spark/                      # Spark configuration (placeholder)
│   └── zookeeper/                  # Zookeeper configuration (placeholder)
│
├── jars/                           # Spark Kafka connector JARs
│   ├── spark-sql-kafka-0-10_2.12-3.5.0.jar
│   ├── kafka-clients-3.5.0.jar
│   ├── commons-pool2-2.11.1.jar
│   └── spark-token-provider-kafka-0-10_2.12-3.5.0.jar
│
├── services/
│   ├── etl-pipeline/               # Spark ETL jobs
│   │   ├── Dockerfile
│   │   ├── jobs/
│   │   │   ├── etl.py              # Real-time CDC streaming ETL (Kafka → ClickHouse)
│   │   │   ├── batch_etl.py        # Batch ETL (CSV → star schema CSVs)
│   │   │   └── preprocessing.py    # Data preprocessing (CSV → PostgreSQL)
│   │   └── tests/
│   │
│   ├── ml-service/                 # Machine learning service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/                    # FastAPI application code
│   │   ├── models/                 # Saved model artifacts
│   │   ├── notebooks/              # Jupyter notebooks for experimentation
│   │   └── tests/
│   │
│   ├── web-api/                    # Backend-for-Frontend API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── internal/           # Internal business logic
│   │   │   └── routers/            # API route handlers
│   │   └── tests/
│   │
│   └── web-frontend/               # ReactJS dashboard
│       ├── Dockerfile              # Multi-stage build (build + serve)
│       ├── package.json
│       ├── public/                 # Static assets
│       └── src/
│           ├── components/         # Reusable UI components
│           ├── pages/              # Page views
│           └── services/           # API client services
│
├── services-ingestion/             # Data ingestion microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   └── preprocessing.py/      # Preprocessing scripts
│   └── tests/
│
└── testing.ipynb                   # Jupyter notebook for Kafka consumer testing
```

---

## 🗄 Database Design

The platform uses a **two-database architecture**:

### PostgreSQL — OLTP (Operational / Source)

Normalized relational schema for transactional writes. Debezium monitors these tables for CDC.

```sql
-- 5 tables with foreign key relationships and indexes

primary_type (id, name)
    ↑
crime (id, iucr, primary_type FK, description, fbi_code)
    ↑
location (id, location_description, block, location)

patrol_unit (id, beat, district, ward, community_area)

case_report (id, case_number, crime_id FK, location_id FK, patrol_unit_id FK, date, time, arrest, domestic)
```

**Indexes:** 14 indexes including composite indexes on `(date, crime_id)` and `(date, location_id)` for common query patterns.

### ClickHouse — OLAP (Analytical / Data Warehouse)

**Star schema** optimized for analytical queries using ClickHouse's `MergeTree` engine:

```
                        ┌─────────────────┐
                        │   dim_date      │
                        │─────────────────│
                        │ id (String PK)  │
                        │ date            │
                        │ month           │
                        │ quarter         │
                        │ year            │
                        │ day_of_week     │
                        │ is_weekend      │
                        └────────┬────────┘
                                 │
┌─────────────────┐    ┌────────┴────────┐    ┌─────────────────┐
│  dim_crime      │    │   fact_case     │    │  dim_location   │
│─────────────────│    │─────────────────│    │─────────────────│
│ id (Int32)      │◀───│ id (Int32)      │───▶│ id (Int32)      │
│ iucr            │    │ case_number     │    │ location_desc   │
│ primary_type    │    │ date_id ────────│──▶ │ block           │
│ description     │    │ time_id ────────│──┐ │ location        │
│ fbi_code        │    │ crime_id        │  │ └─────────────────┘
└────────┬────────┘    │ location_id     │  │
         │             │ patrol_unit_id  │  │ ┌─────────────────┐
┌────────┴────────┐    │ arrest          │  │ │  dim_time       │
│dim_primary_type │    │ domestic        │  │ │─────────────────│
│─────────────────│    └────────┬────────┘  └▶│ id (String PK)  │
│ id (Int32)      │             │              │ hour            │
│ name            │             │              │ minute          │
└─────────────────┘    ┌────────┴────────┐    │ second          │
                       │dim_patrol_unit  │    └─────────────────┘
                       │─────────────────│
                       │ id (Int32)      │
                       │ beat            │
                       │ district        │
                       │ ward            │
                       │ community_area  │
                       └─────────────────┘
```

**Tables Summary:**

| Table | Type | Engine | Description |
|---|---|---|---|
| `dim_date` | Dimension | MergeTree | Calendar dimension (2001–2025), keyed by `YYYYMMDD` |
| `dim_time` | Dimension | MergeTree | Time-of-day dimension (86,400 entries), keyed by `HHmmss` |
| `dim_primary_type` | Dimension | MergeTree | Crime categories (e.g., BATTERY, THEFT, ASSAULT) |
| `dim_crime` | Dimension | MergeTree | Crime details: IUCR code, description, FBI code |
| `dim_location` | Dimension | MergeTree | Location: description, block, coordinates |
| `dim_patrol_unit` | Dimension | MergeTree | Patrol jurisdiction: beat, district, ward, community area |
| `fact_case` | Fact | MergeTree | Central fact table referencing all dimensions |

---

## ⚙ Services

### 1. Data Ingestion Service (`services-ingestion/`)

**Purpose:** Provides an API endpoint for uploading raw CSV data into the system.

| Attribute | Detail |
|---|---|
| **Framework** | FastAPI + Uvicorn |
| **Language** | Python 3.9 |
| **Dependencies** | `fastapi`, `uvicorn`, `python-multipart`, `pandas`, `cassandra-driver` |
| **Port** | 8000 |

**API Endpoints:**
- `POST /upload/csv` — Accepts a `multipart/form-data` request with a CSV file, validates and cleans the data, then inserts it into the database.

---

### 2. ETL Pipeline Service (`services/etl-pipeline/`)

**Purpose:** Runs Extract-Transform-Load jobs to process data from source stores into the ClickHouse analytical warehouse.

| Attribute | Detail |
|---|---|
| **Framework** | Apache Spark 3.5.0, PySpark |
| **Language** | Python 3.11 |
| **Dependencies** | `clickhouse-connect`, `pyspark`, `kafka-python`, `pandas`, `psycopg2-binary` |

**Jobs:**

#### `preprocessing.py` — CSV to PostgreSQL
- Reads `stream_data.csv` (~38 MB) via pandas
- Samples 1% of data for testing (configurable)
- Parses datetime (`MM/dd/yyyy hh:mm:ss a` format)
- Converts booleans (arrest/domestic) to integers
- Fills null values with defaults
- Inserts into 5 PostgreSQL tables in order (respecting FK constraints)
- Batch inserts case reports in chunks of 5,000

#### `batch_etl.py` — CSV to Star Schema CSVs
- Full PySpark batch processing pipeline
- Generates all 6 dimension tables + 1 fact table
- Creates date dimension spanning 2001–2025 (9,131 entries)
- Creates time dimension covering all 86,400 seconds in a day
- Multi-table joins to build `fact_case` with all foreign keys
- Uses `broadcast()` hints for small dimension tables
- Outputs single CSV files via `coalesce(1)`

#### `etl.py` — Real-Time Streaming (Kafka → ClickHouse)
- Spark Structured Streaming with `foreachBatch` processing
- Subscribes to 5 Kafka CDC topics
- Parses Debezium JSON event format (`after` payload extraction)
- Maps CDC events to ClickHouse target tables
- Date conversion: handles both epoch-day integers and ISO strings
- Time conversion: handles both microsecond integers and `HH:MM:SS` strings
- Batched writes to ClickHouse with explicit column types
- Trigger interval: 5 seconds
- Spark config: 4g executor memory, 2g driver memory, 8 max cores

---

### 3. Machine Learning Service (`services/ml-service/`)

**Purpose:** Trains and serves ML models for crime analytics.

| Attribute | Detail |
|---|---|
| **Framework** | FastAPI + Uvicorn |
| **Language** | Python 3.9 |
| **Dependencies** | `fastapi`, `uvicorn`, `scikit-learn`, `pandas`, `torch`, `tensorflow`, `clickhouse-driver` |
| **Port** | 8000 |

**Planned Features:**
- `POST /predict/crime-type` — Crime type classification
- `GET /clusters/similar-areas` — Area clustering by crime patterns
- `GET /forecast/seasonal` — Seasonal crime forecasting

**Directory Structure:**
- `/src` — FastAPI application code
- `/models` — Saved/pre-trained model artifacts
- `/notebooks` — Jupyter notebooks for experimentation & analysis
- `/tests` — Unit and integration tests

---

### 4. Web API Service (`services/web-api/`)

**Purpose:** Backend-for-Frontend (BFF) that serves data to the dashboard.

| Attribute | Detail |
|---|---|
| **Framework** | FastAPI + Uvicorn |
| **Language** | Python 3.9 |
| **Dependencies** | `fastapi`, `uvicorn`, `requests`, `clickhouse-driver` |
| **Port** | 8000 |

**Planned API Endpoints:**
- `GET /api/dashboard/stats` — Aggregated crime statistics
- `GET /api/dashboard/hotspots` — Crime hotspot data
- `GET /api/crimes/by-area` — Crimes filtered by geographic area

**Directory Structure:**
- `/src/internal` — Internal business logic
- `/src/routers` — API route handlers
- `/tests` — Unit and integration tests

---

### 5. Web Frontend Service (`services/web-frontend/`)

**Purpose:** Interactive dashboard for crime data visualization and decision support.

| Attribute | Detail |
|---|---|
| **Framework** | ReactJS (Create React App) |
| **Version** | React 17.0.2 |
| **Build** | Multi-stage Docker build (Node 16 Alpine) |
| **Port** | 3000 |

**Features:**
- Interactive maps and charts for crime statistics
- Crime hotspot predictions visualization
- Data filtering and exploration tools

**Directory Structure:**
- `/src/components` — Reusable UI components
- `/src/pages` — Page views
- `/src/services` — API client services
- `/public` — Static assets (`index.html`, images)

---

## 🏢 Infrastructure Components

### Docker Compose Services

The `docker-compose.yml` defines **10 services**:

| Service | Image | Ports | Description |
|---|---|---|---|
| `clickhouse` | `clickhouse/clickhouse-server:23.8` | 8123 (HTTP), 9000 (Native) | OLAP data warehouse |
| `spark-master` | Custom (Dockerfile) | 8080 (UI), 7077 (Master), 4040 (App UI) | Spark cluster master |
| `spark-worker-1` | Custom (Dockerfile) | 8181 | Spark worker (2 cores, 4g RAM) |
| `spark-worker-2` | Custom (Dockerfile) | 8182 | Spark worker (2 cores, 4g RAM) |
| `spark-worker-3` | Custom (Dockerfile) | 8183 | Spark worker (2 cores, 4g RAM) |
| `zookeeper` | `confluentinc/cp-zookeeper:7.5.0` | 2181 | Kafka coordination service |
| `kafka` | `confluentinc/cp-kafka:7.5.0` | 9092 (Internal), 9094 (External) | Message broker |
| `debezium` | `debezium/connect:2.4` | 8083 | CDC connector for PostgreSQL |
| `kafka-ui` | `provectuslabs/kafka-ui:latest` | 9090 | Web UI for Kafka monitoring |

> **Note:** PostgreSQL runs on the **host machine** (accessed via `host.docker.internal`), not as a Docker container.

### Custom Spark Docker Image

The root `Dockerfile` builds a custom Spark image:
- Base: `apache/spark:3.5.0-python3`
- Compiles **Python 3.11.8 from source** (for ARM64 compatibility)
- Installs `clickhouse-connect` and `pyspark==3.5.0`
- Sets `SPARK_CLASSPATH` to load external JARs from `/opt/spark/jars-ext/`

### Debezium Configuration (`infra/debezium/config.json`)

```json
{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "database.hostname": "host.docker.internal",
  "database.dbname": "crime_data",
  "topic.prefix": "cdc",
  "plugin.name": "pgoutput",
  "table.include.list": "public.primary_type,public.crime,public.location,public.patrol_unit,public.case_report",
  "snapshot.mode": "initial"
}
```

- Monitors 5 PostgreSQL tables
- Uses `pgoutput` logical decoding plugin
- Publishes to topics with `cdc` prefix (e.g., `cdc.public.primary_type`)
- Initial snapshot mode captures existing data on first run

---

## 📜 Shell Scripts

### `running.sh` — ClickHouse Schema Initialization

Initializes the ClickHouse data warehouse by:
1. Creating the `crime_analytics` database
2. Dropping all existing tables (clean slate)
3. Creating 7 tables: `dim_primary_type`, `dim_crime`, `dim_location`, `dim_patrol_unit`, `dim_date`, `dim_time`, `fact_case`

**Usage:**
```bash
bash running.sh
```

### `run_streaming.sh` — Spark Streaming Job Submission

Starts the real-time CDC streaming pipeline:
1. Waits for the Spark cluster to be ready
2. Installs Python dependencies (`clickhouse-connect`, `kafka-python`) on all Spark containers
3. Creates checkpoint directories on the master node
4. Submits the Spark streaming job with Kafka connector JARs

**Usage:**
```bash
bash run_streaming.sh
```

**Spark Submit Configuration:**
- Executor memory: 3g
- Driver memory: 2g
- Executor cores: 2
- Max cores: 8

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# PostgreSQL (host machine)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your_password>
POSTGRES_DB=crime_data

# ClickHouse (Docker)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_NATIVE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_DB=crime_analytics

# Kafka
KAFKA_BROKER=kafka:9092
KAFKA_TOPIC_CRIME_DATA=crime.data.events

# Web API
API_PORT=8000
```

---

## 🚀 Getting Started

### Prerequisites

- **Docker** & **Docker Compose**
- **PostgreSQL** installed on the host machine (with logical replication enabled for Debezium)
- **Python 3.9+** (for running preprocessing scripts locally)
- **~16 GB RAM** recommended (Spark workers use 4g each)

### Step-by-Step Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Public-Safety-Crime-Analytics
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

3. **Prepare PostgreSQL:**
   ```bash
   # Create the database
   createdb crime_data

   # Initialize the schema
   psql -d crime_data -f infra/postgresql/init.sql

   # Enable logical replication (required for Debezium)
   # In postgresql.conf: wal_level = logical
   ```

4. **Place your raw data:**
   ```bash
   # Place the crime CSV dataset at:
   # data/raw/stream_data.csv  (for streaming pipeline)
   # data/raw/crime_data.csv   (for batch pipeline)
   ```

5. **Start the infrastructure services:**
   ```bash
   docker-compose up --build -d
   ```

6. **Initialize ClickHouse tables:**
   ```bash
   bash running.sh
   ```

7. **Run data preprocessing (load data into PostgreSQL):**
   ```bash
   python services/etl-pipeline/jobs/preprocessing.py
   ```

8. **Register the Debezium connector:**
   ```bash
   curl -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d @infra/debezium/config.json
   ```

9. **Start the Spark streaming ETL:**
   ```bash
   bash run_streaming.sh
   ```

### Monitoring

| Dashboard | URL |
|---|---|
| Spark Master UI | http://localhost:8080 |
| Spark Application UI | http://localhost:4040 |
| Kafka UI | http://localhost:9090 |
| ClickHouse HTTP | http://localhost:8123 |
| Debezium REST API | http://localhost:8083 |

---

## 🌐 Port Reference

| Port | Service | Protocol |
|---|---|---|
| 2181 | Zookeeper | TCP |
| 4040 | Spark Application UI | HTTP |
| 5432 | PostgreSQL (host) | TCP |
| 7077 | Spark Master | TCP |
| 8080 | Spark Master Web UI | HTTP |
| 8083 | Debezium Connect REST API | HTTP |
| 8123 | ClickHouse HTTP Interface | HTTP |
| 8181–8183 | Spark Worker Web UIs | HTTP |
| 9000 | ClickHouse Native Client | TCP |
| 9090 | Kafka UI | HTTP |
| 9092 | Kafka (Internal) | TCP |
| 9094 | Kafka (External/Host) | TCP |

---

## 📦 Java Dependencies (JARs)

Located in `/jars/`, these are required for Spark-Kafka integration:

| JAR | Version | Purpose |
|---|---|---|
| `spark-sql-kafka-0-10_2.12` | 3.5.0 | Spark Structured Streaming Kafka connector |
| `kafka-clients` | 3.5.0 | Apache Kafka Java client library |
| `commons-pool2` | 2.11.1 | Apache Commons connection pooling |
| `spark-token-provider-kafka-0-10_2.12` | 3.5.0 | Kafka authentication token provider |

---

## 📄 Documentation

Additional documentation can be found in the `/docs` directory:

- **[Architecture](docs/architecture.md)** — High-level system architecture and data flow
- **[OpenAPI Specs](docs/api/openapi.md)** — API specifications for Web API and Ingestion API
- **[ADR Template](docs/ADR/adr_template.md)** — Architecture Decision Record template for documenting design decisions

---

## 📊 Dataset

The project uses Chicago crime data (CSV format) containing fields such as:

| Field | Description |
|---|---|
| `ID` | Unique crime record identifier |
| `Case Number` | Chicago PD case number |
| `Date` | Date & time of occurrence (`MM/dd/yyyy hh:mm:ss a`) |
| `Block` | Street block address |
| `IUCR` | Illinois Uniform Crime Reporting code |
| `Primary Type` | Crime category (e.g., BATTERY, THEFT, ASSAULT) |
| `Description` | Detailed crime description |
| `Location Description` | Type of location (e.g., STREET, APARTMENT) |
| `Arrest` | Whether an arrest was made (boolean) |
| `Domestic` | Whether the incident was domestic-related (boolean) |
| `Beat` | Police beat number |
| `District` | Police district number |
| `Ward` | City ward number |
| `Community Area` | Community area number |
| `FBI Code` | FBI crime classification code |
| `Latitude` / `Longitude` | Geographic coordinates |
| `Location` | Combined lat/long string |
