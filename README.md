# A Dual-Architecture NLP2SQL Agent System

![UI Query GPT Agent](figures/UI%20Query%20GPT%20Agent.png)

A dual-architecture AI system that allows you to chat with your CSV data using Natural Language to generate SQL queries and charts. This repository actively develops and compares two distinct architectural methodologies side-by-side.

## Features

- **Upload any CSV file (Baseline System)**: The application automatically infers the data schema and reads metadata.
- **Natural Language to SQL**: Converts your chat questions into optimized DuckDB queries.
- **Automated Data Visualization (Baseline System)**: Automatically writes Python code to generate and display plots inline using Matplotlib/Plotly.
- **Dual Architecture Deployment**: 
  - **Baseline System**: A 3-agent pipeline with **Semantic Layer** for rule-based query pre-analysis (Semantic -> Analyzer -> SQL -> Chart).
  - **Query GPT System**: An advanced 6-stage pipeline inspired by Uber's Query GPT (Enhance -> Intent -> Table -> Prune -> GenAI -> Execute) with Workspace Routing.
- **Benchmark Evaluation**: A dedicated evaluation suite testing both systems on 257 complex queries.

## System Architectures

### 1. Baseline System (3-Agent Pipeline + Semantic Layer)

```text
[User Chat]
      |
      v
+--------------+
|  Streamlit   |-------+
|     UI       |       | (Uploads CSV)
+--------------+       |
      |                v
      |         +--------------+
      |         | CSV Metadata |
      |         |  Extraction  |
      |         +--------------+
      |                |
      v                v
+-----------------------------+
|     Semantic Layer          | <-- (Rule-based, No LLM)
|  +------------------------+ |
|  | - Intent Detection     | |
|  | - Column Matching      | |
|  | - Aggregation Detection| |
|  | - Time Period Detection| |
|  | - Output Type Detection| |
|  +------------------------+ |
+-----------------------------+
      |
      | (SemanticResult: intent, columns, ops, ...)
      v
+--------------+ <-- (Schema + SemanticResult + User Query)
|   Analyzer   |
|    Agent     |
+--------------+
      |
      | (Generates Data Retrieval Plan)
      v
+--------------+
|     SQL      | --> [DuckDB Executes SQL]
|    Agent     | <-- [Returns Data subset]
+--------------+
      |
      | (Passes subset & checks if plot is needed)
      v
+--------------+
|    Chart     | --> [Generates Plotly/Matplotlib]
|    Agent     | --> [Saves to output/]
+--------------+
      |
      v
[Streamlit UI Displays Data/Chart]
```

1. **Semantic Layer (semantic/)**: A rule-based pre-processing module (no LLM calls) that analyzes the user's query before passing it to the LLM agents. It extracts structured metadata to reduce LLM workload and improve accuracy:
   - **Intent Detection**: Classifies query intent (aggregation, filter, comparison, ranking, trend, distribution) using keyword matching.
   - **Column Matching**: Fuzzy-matches terms in the query to CSV column names using 4 strategies: exact, normalized (diacritics-free), synonym-based (Vietnamese <-> English), and fuzzy (SequenceMatcher).
   - **Aggregation Detection**: Identifies SQL operations (SUM, AVG, COUNT, MAX, MIN) from Vietnamese/English keywords.
   - **Time Period Detection**: Extracts time granularity (day/month/quarter/year) and specific time filters.
   - **Output Type Detection**: Determines desired output format (chart, table, single value).
   - **GROUP BY / Sort Detection**: Identifies grouping and ordering hints.
2. **Analyzer Agent**: Interprets the user's intent using both the CSV schema and the SemanticResult from the Semantic Layer. The structured hints allow the LLM to validate and refine rather than analyze from scratch.
3. **SQL Agent**: Translates instructions into optimized SQL queries and safely executes them using the DuckDB engine. Uses double-quoted identifiers to support table/column names with special characters.
4. **Chart Agent (Optional)**: Triggered if visualization is requested, it writes and executes Python code (matplotlib/plotly) to render charts within Streamlit.

### 2. Query GPT System (Uber Inspired)

A newly introduced schema-driven architecture optimized for large sets of CSV files (68+ files) and context-window minimization through intelligent Workspace Routing.

```text
       [User Chat Query]
              |
              v
   +----------------------+    +-------------------------+
   | 1. Prompt Enhancer   |    | 0. Metadata Scanner     |
   | (Expands User Query) |    | (Builds schema &        |
   +----------------------+    |  workspaces.json)       |
              |                +-------------+-----------+
              v                              |
   +----------------------+                  |
   | 2. Intent Agent      |                  |
   | (Routes to Workspace)|                  |
   +----------------------+                  v
              |                +-------------------------+
              v                | User Select/Edit CSV    |
   +-----------------------------------------+-----------+
   | 3. Table Agent (Finds Best CSV in       |
   |    Matched Workspace)                   |
   +-----------------------------------------+
              |
              v (Matched CSV Schema + Enhanced Query)
   +--------------------------------------------------+
   | 4. Column Pruner (Removes Irrelevant Columns)    |
   +--------------------------------------------------+
              |
              v (Pruned Schema + Enhanced Query)
   +--------------------------------------------------+    +-----------------------+
   | 5. GenAI SQL Gateway (Generates DuckDB SQL)      |<---| SQL Samples RAG       |
   +--------------------------------------------------+    +----------+------------+
              |                                                       ^
              |                                            +----------+------------+
              |                                            | Ingest Data           |
              |                                            | (Vectorize samples)   |
              |                                            +-----------------------+
              v (Executable SQL)
   +--------------------------------------------------+
   | 6. SQL Executor (Runs DuckDB & Formats Markdown) |
   +--------------------------------------------------+
              |
              v
      [Streamlit UI Shows Markdown Data]
```

1. **Metadata Scanner (schema_builder.py & build_workspaces.py)**: Pre-scans the data-code/InfiAgent/da-dev-tables/ directory, builds a global schema_registry.json, and groups 68+ files into topic-based workspaces (Finance, Health, Sports, Transportation, General) via workspaces.json.
2. **Prompt Enhancer**: Intercepts short or vague queries and uses an LLM to expand them into clear, detailed questions to improve downstream accuracy.
3. **Intent Agent**: Classifies the semantic topic of the enhanced input and routes the query to the correct Workspace ID.
4. **Table Agent**: Uses the Workspace and Query to identify the single most relevant CSV file from that specific subset. (Includes UI for the user to manually select or edit the chosen CSV).
5. **Column Pruner Agent**: Selects ONLY the absolutely necessary columns required to answer the query, discarding the rest to dramatically save LLM token usage and prevent hallucinations.
6. **GenAI SQL Gateway**: A specialized pipeline that combines the pruned schema, retrieved SQL samples (via RAG), and the user query to generate highly accurate Few-Shot DuckDB SQL.
7. **SQL Executor**: A sandboxed wrapper that runs the query on DuckDB and streams results back to the user.
8. **SQL Sample RAG (sql_samples/)**: Uses Agno and ChromaDB to find relevant SQL examples similar to the user's question, enhancing generation accuracy.

## Benchmark Evaluation

A rigorous benchmark suite (benchmark/) evaluates both systems against a dataset of 257 complex tabular questions.

- **Baseline System Performance**: 90 / 257 correct (Accuracy: 35.02%)
- **Query GPT System Performance**: 85 / 257 correct (Accuracy: 33.07%)

*Note: The Query GPT architecture currently bypasses the Table Agent during automated evaluation (hardcoded to the correct table). The accuracy difference highlights optimization opportunities in the Column Pruning and GenAI SQL Generation steps.*

## Setup

1. **Prerequisites**: Ensure you have Python installed. We recommend using [uv](https://github.com/astral-sh/uv) to manage your environment.

2. **Initialize python environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and add your OpenAI API Key:
   Then, create the `.env` file and set your key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

This repository contains executable bash scripts for both distinct systems. Data resources (data-code/) are heavily shared between them.

### Running Baseline System
1. Start the Streamlit application:
   ```bash
   ./run_baseline.sh
   ```
2. Upload a CSV file through the sidebar on the left.
3. Chat with your data! 

### Running Query GPT System
Before launching the query GPT architecture, you **must** build the metadata schema registry and workspace mapping at least once:
```bash
python query_gpt_system/metadata/schema_builder.py
python query_gpt_system/metadata/build_workspaces.py
```
This deeply scans all the large CSVs inside data-code/InfiAgent/da-dev-tables/ and structures their formats for the Table Agent.

Next, you need to ingest the SQL samples into the vector database for the RAG system:
```bash
python query_gpt_system/sql_samples/ingest_samples.py
```

After the registry is successfully populated and the data is ingested:
```bash
./run_query_gpt.sh
```

### Running the Benchmarks
To run the automated evaluations and generate `results.json`:
```bash
python benchmark/run_eval_baseline.py
python benchmark/run_eval_query_gpt.py
```

### Example Prompts
- "What is the average age of passengers in each ticket class?"
- "Find the top 10 countries with the highest happiness score and plot them."
- "What is the correlation between the number of rooms and house prices?"

## Built With
- [Agno](https://agno.com/) - Multi-agent framework
- [Streamlit](https://streamlit.io/) - Interactive Web UI
- [DuckDB](https://duckdb.org/) - In-memory analytical SQL database
- [OpenAI](https://openai.com/) - Using the gpt-4o-mini language model
- [ChromaDB](https://www.trychroma.com/) - The open-source AI database
