```
F:\HK251\bigdata\
├───.dockerignore
├───.env.example
├───.gitignore
├───docker-compose.yml
├───GEMINI.md
├───README.md
├───PROJECT_STRUCTURE.md
├───.gemini\
│   └───.env
├───data\
│   ├───processed\
│   │   └───README.md
│   └───raw\
│       └───README.md
├───docs\
│   ├───architecture.md
│   ├───ADR\
│   │   └───adr_template.md
│   └───api\
│       └───openapi.md
├───infra\
│   ├───cassandra\
│   │   └───init.cql
│   ├───clickhouse\
│   │   └───init.sql
│   ├───debezium\
│   │   └───config.json
│   ├───kafka\
│   │   └───README.md
│   ├───spark\
│   │   └───README.md
│   └───zookeeper\
│       └───README.md
├───services\
│   ├───etl-pipeline\
│   │   ├───Dockerfile
│   │   ├───README.md
│   │   ├───jobs\
│   │   │   └───README.md
│   │   │   └───requirements.txt
│   │   └───tests\
│   │       └───README.md
│   ├───ml-service\
│   │   ├───Dockerfile
│   │   ├───README.md
│   │   ├───requirements.txt
│   │   ├───models\
│   │   │   └───README.md
│   │   ├───notebooks\
│   │   │   └───README.md
│   │   ├───src\
│   │   │   └───README.md
│   │   └───tests\
│   │       └───README.md
│   ├───web-api\
│   │   ├───Dockerfile
│   │   ├───README.md
│   │   ├───requirements.txt
│   │   ├───src\
│   │   │   ├───README.md
│   │   │   ├───internal\
│   │   │   │   └───README.md
│   │   │   └───routers\
│   │   │       └───README.md
│   │   └───tests\
│   │       └───README.md
│   └───web-frontend\
│       ├───Dockerfile
│       ├───package.json
│       ├───README.md
│       ├───public\
│       │   └───README.md
│       └───src\
│           ├───README.md
│           ├───components\
│           │   └───README.md
│           ├───pages\
│           │   └───README.md
│           └───services\
│               └───README.md
└───services-ingestion\
    ├───Dockerfile
    ├───README.md
    ├───requirements.txt
    └───src\
        ├───README.md
        ├───api\
        │   └───README.md
        └───tests\
            └───README.md
```