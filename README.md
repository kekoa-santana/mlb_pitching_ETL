# MLB Pitching ETL Pipeline

A data engineering pipeline that extracts MLB pitch-by-pitch and game-level data from the MLB Stats API and Statcast, transforms it through a validated staging layer, and loads it into a PostgreSQL star-schema data warehouse for analytics.

## Table of Contents

- [Architecture](#architecture)
- [Data Flow](#data-flow)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Schema Validation](#schema-validation)
- [Configuration](#configuration)

## Architecture

The pipeline follows a three-layer architecture:

```
 MLB Stats API / PyBaseball
           |
   +-------v--------+
   | INGESTION LAYER |   Boxscores, Statcast pitches, team rosters
   +-------+---------+
           |
     Parquet files + Raw DB tables
           |
   +-------v--------+
   |  STAGING LAYER  |   Schema validation, type coercion, derived metrics
   +-------+---------+
           |
   +-------v----------+
   | PRODUCTION LAYER  |   Star schema: facts, dimensions, satellites
   +------------------+
```

**Key design decisions:**
- **Declarative schema specs** define structure, validation rules, and transformations for every table
- **Idempotent loads** via upsert (INSERT ... ON CONFLICT ... DO UPDATE) on all tables
- **Audit trail** with raw JSON payloads stored in landing tables
- **Builder pattern** for derived staging tables (at-bats aggregated from pitches)

## Data Flow

```
MLB Stats API & PyBaseball
         |
   Ingestion Layer
    |- fetch_and_load_boxscores()  --> raw.pitching_boxscores
    |- extract_and_save_statcast() --> data/*.parquet
    +- fetch_team_dim()            --> production.dim_team
         |
   Staging Layer (Transform & Load)
    |- parquet --> staging.statcast_pitches      (spec validation)
    |- parquet --> staging.statcast_batted_balls  (filtered to BIP only)
    |- build_at_bats() --> staging.statcast_at_bats (aggregated)
    +- raw.pitching_boxscores --> staging.pitching_boxscores
         |
   Production Layer (Star Schema)
    |- staging --> production.dim_game
    |- API     --> production.dim_player
    |- staging --> production.fact_pa
    |- staging --> production.fact_pitch
    |- staging --> production.sat_pitch_shape
    +- staging --> production.sat_batted_balls
```

## Project Structure

```
mlb_pitching_ETL/
+-- full_pipeline.py                  # Main orchestration entry point
+-- ingestion/
|   +-- ingest_boxscores.py           # Game boxscore extraction from Stats API
|   +-- ingest_statcast.py            # Pitch-by-pitch data via pybaseball
|   +-- ingest_team_dim.py            # Team dimension from Stats API
|   +-- ingest_dim_player.py          # Player dimension from Stats API
+-- transformation/
|   +-- staging/
|   |   +-- load_table.py             # Registry-based table loader
|   |   +-- transform_load_table.py   # Core transform & upsert engine
|   +-- builders/
|   |   +-- build_at_bats.py          # Aggregate pitches to at-bat level
|   |   +-- build_dim_game.py         # Derive game dimension from staging
|   +-- production/
|       +-- sql_registry.py           # Ordered SQL script execution
|       +-- sql/
|           +-- production_load_facts.sql   # Load fact_pa and fact_pitch
|           +-- load_pitch_shape.sql        # Load sat_pitch_shape
|           +-- load_batted_balls.sql       # Load sat_batted_balls
+-- schema/
|   +-- spec_engine.py                # Declarative schema validation engine
|   +-- staging/                      # Staging table specifications
|   +-- production/                   # Production table specifications
+-- utils/
|   +-- utils.py                      # Database connection helpers
|   +-- retry.py                      # HTTP retry with exponential backoff
|   +-- statcast_utils.py             # Pitch classification & flag helpers
|   +-- sql_runner.py                 # SQL file execution utilities
+-- alembic/                          # Database migration management
+-- docs/                             # Additional documentation
+-- data/                             # Parquet landing zone (gitignored)
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (default port: 5433)
- Database with `raw`, `staging`, and `production` schemas created

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd mlb_pitching_ETL
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your database credentials:
   ```
   DB_USER=<username>
   DB_PASSWORD=<password>
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=mlb_pitching
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

## Usage

### Full Pipeline

Run the complete ETL pipeline for a date range:

```bash
python full_pipeline.py --start-date 2025-03-18 --end-date 2025-11-01
```

### Skip Ingestion

If you already have parquet data files, skip the extraction phase:

```bash
python full_pipeline.py --skip-ingestion --parquet data/statcast_pitching.parquet
```

### Skip Production

Run only ingestion and staging without loading the production star schema:

```bash
python full_pipeline.py --start-date 2025-03-18 --end-date 2025-11-01 --skip-production
```

### Pipeline Phases

The pipeline executes three phases in order:

| Phase | What it does |
|-------|-------------|
| **Ingestion** | Fetches team rosters, game boxscores, and pitch-by-pitch Statcast data from MLB APIs. Saves raw data to landing tables and parquet files. |
| **Staging** | Applies schema validation, type coercion, bounds checking, and derived metric calculation. Loads validated data into staging tables via upsert. |
| **Production** | Builds the star schema: dimension tables, fact tables (fact_pa, fact_pitch), and satellite tables (sat_pitch_shape, sat_batted_balls) with derived analytics columns. |

## Database Schema

The production layer follows a star schema design:

### Dimensions

| Table | Primary Key | Description |
|-------|------------|-------------|
| `dim_game` | `game_pk` | Game metadata: date, type, home/away teams |
| `dim_player` | `player_id` | Player details: name, position, handedness, physical attributes |
| `dim_team` | `team_id` | All 30 MLB teams with venue and division info |

### Facts

| Table | Primary Key | Natural Key | Description |
|-------|------------|-------------|-------------|
| `fact_pa` | `pa_id` | (game_pk, game_counter) | Plate appearance outcomes, counts, and game context |
| `fact_pitch` | `pitch_id` | (game_pk, game_counter, pitch_number) | Individual pitch attributes, velocity, movement, and outcome flags |

### Satellites

| Table | Primary Key | Description |
|-------|------------|-------------|
| `sat_pitch_shape` | `pitch_id` (FK) | Release position, velocity vectors, acceleration components |
| `sat_batted_balls` | `pitch_id` (FK) | Launch speed/angle, hit coordinates, expected stats (xBA, xSLG, xwOBA), derived metrics (hard_hit, sweet_spot, spray_bucket) |

For full column-level documentation, see [docs/db_schema.md](docs/db_schema.md).

## Schema Validation

Every table passes through the spec engine (`schema/spec_engine.py`) which applies:

- **Column renaming** from source names to target names
- **Type coercion** (string to int, float, boolean, date)
- **Bounds validation** with configurable nullable ranges (e.g., pitch speed 20-108 mph, spin rate 500-3500 RPM)
- **Derived column calculation** via lambda functions (e.g., `is_whiff`, `pitch_result_type`, `rbi`)
- **Row filtering** to drop invalid records
- **Primary key uniqueness** enforcement with deduplication
- **Not-null constraint** checking

Each load produces a validation report with row counts, coercion results, and violation summaries.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DB_USER` | `kekoa` | PostgreSQL username |
| `DB_PASSWORD` | (required) | PostgreSQL password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5433` | Database port |
| `DB_NAME` | `mlb_pitching` | Database name |
| `DATABASE_URL` | (optional) | Full connection URL (overrides individual vars) |

### Data Sources

| Source | Library/API | Data |
|--------|-----------|------|
| MLB Stats API | `requests` | Team rosters, game schedules, boxscores, player info |
| Statcast | `pybaseball` | Pitch-by-pitch tracking data (velocity, spin, movement, location) |
