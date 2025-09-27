# MoMo SMS Processing Application

## Table of contents

* [Overview](#overview)
* [Features](#features)
* [Repository Structure](#repository-structure)
* [Architecture](#architecture)
* [Database](#database)
* [API Server](#api-server)
* [DSA Comparison](#data-structures-&-algorithms-(dsa)-comparison)
* [Development Workflow](#development-workflow)
* [Environment](#environment)
* [Team](#team)
* [Setup Instructions](#setup-instructions)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)

## Overview

This repository contains an enterprise-level full-stack application (coming soon) for processing Mobile Money (MoMo) SMS data.  
The system ingests SMS data in XML format, performs data cleaning and categorization, persists the results in a relational database, provides a REST API for transaction data, and offers a frontend dashboard for analytics and visualization.

## Features

* XML parsing using `xml.etree.ElementTree`  
* Data cleaning and normalization (dates, amounts, phone numbers)  
* Transaction categorization (payments, withdrawals, transfers, etc.)  
* Relational database persistence (MySQL by default, PostgreSQL supported)  
* REST API server in plain Python with Basic Authentication  
* Data Structures & Algorithms performance comparison (linear search vs dictionary lookup)  
* JSON exports for dashboard analytics  
* Frontend visualization (charts, tables, trends)  
* Modular ETL pipeline (`parse` → `clean` → `categorize` → `load` → `export`)  
* Unit tests for core ETL stages

## Repository Structure

```
MoMo_Enterprise/
├── README.md                    # Setup, run, overview 
├── CONTRIBUTING.md              # PRs, branching, and issues guide     
├── setup_project.sh             # Environment setup script
├── .gitignore                   # Files for Git to ignore    
├── .env                         # Environment configs, DB URLs/path to SQLite
├── requirements.txt             # Python dependencies
├── index.html                   # Static frontend dashboard entry
├── web/
│   ├── styles.css               # Dashboard styling   
│   ├── chart_handler.js         # Fetch + render charts/tables   
│   └── assets/
│       └── architecture.jpeg    # Architecture diagram
├── data/
│   ├── raw/                     
│   │   └── modified_sms_v2.xml  # Original XML (gitignored)
│   ├── processed/               # JSON exports
│   │   ├── dashboard.json
│   │   └── transactions.json        
│   ├── db/                      # DB files
│   └── logs/                    # ETL logs, dead letter files
│       ├── etl.log                
│       └── dead_letter/ 
├── etl/
│   ├── __init__.py
│   ├── config.py                # ETL config
│   ├── clean_normalize.py       # Cleaning and normalization
│   ├── categorize.py            # Categorization rules
│   ├── load_db.py               # DB creation/upsert
│   └── run.py                   # ETL pipeline runner
├── examples/
│   └── json_schemas.json        # JSON schema
├── api/                         
│   ├── __init__.py
│   ├── app.py                   # FastAPI app with /transactions, /analytics
│   ├── server.py                # REST API server
│   ├── db.py                    # Database helpers
│   └── schemas.py               # Pydantic models
├── dsa/
│   ├── parse_xml.py             # XML parser
│   └── compare_dsa_search.py    # DSA comparison
├── docs/
│   ├── erd_diagram.pdf          # ERD design rationale
│   └── api_docs.md              # API documentation
├── scripts/                     # Run, rebuild, serve app
│   ├── run_etl.sh                
│   ├── export_json.sh            
│   └── serve_frontend.sh         
└── tests/                       # Unit tests
     ├── test_parse_xml.py
     ├── test_clean_normalize.py
     └── test_categorize.py
```

## Architecture

The system follows a modular design:  
* Data ingestion from SMS XML loaded into ETL pipeline  
* Processing: parsing, cleaning, normalization, categorization  
* Persistence: relational database + caching layer  
* API: transaction data served securely via REST  
* DSA: search performance comparisons  
* Frontend: static dashboard consuming aggregated data  

View Architecture Diagram on [web](https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=MoMo%20SMS%20Enterprise%20Architecture.drawio) or from the file: web/assets/architecture.jpeg 

## Database

The project uses a relational database (MySQL default; PostgreSQL supported) to persist clean, categorized SMS transactions.  
* Normalized tables: `User`, `Transaction`, `TransactionParticipant`  
* ETL handles creation and upsert operations  
* REST API performs queries and updates efficiently  
* DB files in `data/db/`, ETL logs in `data/logs/`  
* Provides data integrity, fault tolerance, and scalability  

## API Server

* Located in `api/server.py`  
* Supports CRUD for transactions with Basic Auth protection 
* Returns JSON responses with proper HTTP status and error info

## Data Structures & Algorithms (DSA) Comparison

* Script at `dsa/compare_dsa_search.py` 
* Compares linear search vs dictionary lookup on transaction IDs  
* Outputs timing and reflection on efficiencies

## Development Workflow

Agile Scrum tracked on Jira:  
[View Scrum Board](https://alustudent-team1.atlassian.net/jira/software/projects/MSPE/boards/34?atlOrigin=eyJpIjoiYjg2ZjViOGNhM2FhNDUzNmFhZDg1MzA5OTdlOGU3ZmMiLCJwIjoiaiJ9)  
Columns: To Do, In Progress, Done

## Environment

This project was developed and tested on:  

<a href="https://ubuntu.com/" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=Ubuntu%2020.04%20LTS&color=E95420&logo=Ubuntu&logoColor=E95420&labelColor=2F333A" alt="Ubuntu 20.04 LTS"></a>  
<a href="https://www.gnu.org/software/bash/" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=GNU%20Bash&color=4EAA25&logo=GNU%20Bash&logoColor=4EAA25&labelColor=2F333A" alt="GNU Bash"></a>  
<a href="https://www.python.org" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=Python%203.8%2B&color=FFD43B&logo=Python&logoColor=3776AB&labelColor=2F333A" alt="Python 3.8+"></a>  
<a href="https://www.vim.org/" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=Vim&color=019733&logo=Vim&logoColor=019733&labelColor=2F333A" alt="Vim"></a>  
<a href="https://code.visualstudio.com/" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=Visual%20Studio%20Code&color=5C2D91&logo=Visual%20Studio%20Code&logoColor=5C2D91&labelColor=2F333A" alt="Visual Studio Code"></a>  
<a href="https://git-scm.com/" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=Git&color=F05032&logo=Git&logoColor=F05032&labelColor=2F333A" alt="Git"></a>  
<a href="https://github.com" target="_blank"><img height="20" src="https://img.shields.io/static/v1?label=&message=GitHub&color=181717&logo=GitHub&logoColor=f2f2f2&labelColor=2F333A" alt="GitHub"></a>

## Team

<details>
<summary>Monica Dhieu -- Backend & ETL Pipeline Lead</summary>
<ul>
<li><a href="https://github.com/m-dhieu">Github</a></li>
<li><a href="https://www.linkedin.com/in/monica-dhieu">LinkedIn</a></li>
<li><a href="mailto:m.dhieu@alustudent.com">e-mail</a></li>
</ul>
</details>

<details>
<summary>Janviere Munezero -- Database & API Integration</summary>
<ul>
<li><a href="https://github.com/Janviere-dev">Github</a></li>
<li><a href="https://www.linkedin.com/in/munezero-janviere-a5375b300">LinkedIn</a></li>
<li><a href="mailto:janviere.munezero@example.com">e-mail</a></li>
</ul>
</details>

<details>
<summary>Thierry Gabin -- Frontend & Data Visualization</summary>
<ul>
<li><a href="https://github.com/tgabin1">Github</a></li>
<li><a href="https://www.linkedin.com/in/#">LinkedIn</a></li>    
<li><a href="mailto:thierry.gabin@example.com">e-mail</a></li>
</ul>
</details>

<details>
<summary>Santhiana Kaze -- DevOps & Monitoring</summary>
<ul>
<li><a href="https://github.com/ksanthiana">Github</a></li>
<li><a href="https://www.linkedin.com/in/#">LinkedIn</a></li>    
<li><a href="mailto:santhiana.kaze@example.com">e-mail</a></li>
</ul>
</details>

## Setup Instructions

**Prerequisites:**  
* Python 3.8 or newer  
* Virtual environment (optional but encouraged)  
* Bash or compatible command-line  
* Git version control

**Setup:**  
* Clone the repo  
* Run `setup_project.sh` to install dependencies  
* Create `.env` for database connection strings if needed  

**Current Functionalities:**  
* Create database schemas with `database/database_setup.sql`
* Parse raw XML data with `dsa/parse_xml.py`  
* Load parsed transactions into JSON `data/processed/transactions.json`
* Load parsed transactions into MySQL DB  
* REST API on `api/server.py`  
* DSA performance test in `dsa/compare_dsa_search.py`

**Coming Soon:**  
* Frontend dashboard for detailed analytics  
* Automated ETL orchestration and monitoring  
* Enhanced API with analytics endpoints  

## Contributing

Consult `CONTRIBUTING.md` for guidelines on contributing.

## License

MIT License.

## Contact

Reach out to any listed team member for support, queries, or feedback.

---

*Monday: September 29, 2025*
