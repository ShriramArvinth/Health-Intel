# Health Intel Search (Talk To Your Records)

A retrieval‑augmented service that loads curated medical domain knowledge and prompt templates from Google Cloud Storage, caches them in-memory at startup, and serves downstream reasoning / chat / research workflows via LLM-backed pipelines.

## Key Capabilities
- Structured prompt + knowledge management (cloud → cached memory).
- Deterministic file naming & taxonomy by specialty / condition.
- Text ingestion + cleanup + consolidation (one normalized text artifact per slug).
- Retrieval Augmented Generation (RAG) experiments (semantic vs hierarchical chunking, query expansion).
- Cloud Run container deployment via GitHub Actions.
- Strong code quality: typed Python, small intent‑revealing functions, unit tests, static analysis.

## High-Level Architecture
1. GCS Bucket (content + prompts)
2. Startup Loader:
   - retrieve_and_cache_prompts()
   - retrieve_and_cache_knowledge()
3. Ingestion / normalization pipeline
4. Chunking + retrieval layer (pluggable strategies)
5. LLM orchestration (multiple provider API keys)
6. API / service interface (Cloud Run)

## Google Cloud Storage Layout (Example)
bucket/
  wld/
    knowledge.txt
    system_prompt.txt
    user_prompt.txt
  t1d/
    knowledge.txt
    system_prompt.txt
    user_prompt.txt
  ...additional specialties...

Naming rule: <slug>/<role>_prompt.txt and knowledge.txt

## Environment Variables (deployed)
- AI_CHAT_API_KEY
- DEEP_RESEARCH_API_KEY
- PERPLEXITY_API_KEY
- STORAGE_BUCKET_NAME (e.g. ai_chat_tes_resources)
- (Service account credentials injected via workflow secrets)

## Caching Strategy
On service start:
- Scan all slug directories
- Load knowledge + prompt files
- Build in-memory map: { slug: { knowledge, system_prompt, user_prompt } }
- Hot-reload (optional future enhancement) could watch GCS etags.

## Pipeline (Ingestion → Consolidation)
Inputs: list of slugs
Steps:
1. Fetch domain text (dx sources or internal corpora)
2. Clean / normalize (remove boilerplate, standardize citations)
3. Merge into single contextual document per slug
4. Store intermediate artifacts (optional) or keep ephemeral
5. Feed to chunker + embedding / graph modules

## RAG Experiment Tracks
Implemented / baseline:
- Semantic chunking (flat, embedding similarity)
In progress / planned:
- Hierarchical chunking (variable chunk sizes)
- Query expansion (intent-based enrichment)
- Graph RAG (entity/relation extraction + traversal)
- Model swap: replace PubMedBERT baseline with improved biomedical encoder

## Local Development
Prerequisites: Python 3.11+, gcloud CLI (for auth if pulling directly), Docker (optional)
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. export required environment variables (or use .env + loader)
4. Run tests: pytest
5. Start service: python -m app (or your entrypoint)

## Code Quality
- Type checking: mypy
- Linting: ruff / flake8 (choose one configured)
- Small, single-purpose functions
- Add unit tests for each new module (tests/ mirrors src/)

## Testing Strategy
- Unit: parsing, caching, chunking
- Integration: end-to-end ingestion + retrieval path
- (Planned) Golden outputs for deterministic prompt assembly

## Deployment (Dev)
Automated via .github/workflows/dev-deploy.yml:
- Trufflehog secret scan
- Build & push container to Artifact Registry
- Deploy to Cloud Run (service: Health-Intel-search-dev)
- Inject secrets + env vars

To trigger: push to main modifying app/, Dockerfile, requirements.txt, or workflow.

## Adding a New Specialty (Slug)
1. Create folder in bucket: <slug>/
2. Add knowledge.txt, system_prompt.txt, user_prompt.txt
3. Redeploy OR implement hot reload (if added later)
4. Confirm slug appears in cached registry at startup logs

## Future Enhancements
- Hot reload of GCS content
- Admin endpoint: /cache/refresh
- Embedding store abstraction (Postgres pgvector / Vertex Matching Engine)
- Graph-based retrieval module
- Evaluation harness (precision / recall on Q&A set)