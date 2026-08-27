# Completion Changelog

## Frontend

- Connected landing page to real login, registration, dashboard and selfie-search routes.
- Added photographer dashboard with live API totals and processing status.
- Added event creation, access codes, QR access, retention settings and face-indexing control.
- Added batch upload, image preview, AI job polling and flagged-photo review.
- Added consent-based personalised selfie gallery and downloads.
- Added administrator monitoring and personal-data deletion request pages.
- Removed unsupported pricing and inflated performance claims.

## Backend

- Added local JWT authentication and optional Supabase Auth.
- Added event, image, processing, dashboard, administration and privacy APIs.
- Added image standardisation, compression, thumbnails and lighting normalisation.
- Added Celery/Redis processing architecture and non-blocking local thread fallback.
- Added blur analysis, perceptual duplicate comparison, multiple face embeddings and classification integration.
- Added local SQLite mode and Supabase PostgreSQL/pgvector mode.
- Added event-restricted HNSW cosine search.
- Added consent, access control, download audit, deletion requests and expiring unclaimed embeddings.
- Added automated tests, load-test file, evaluation script and Docker configuration.

## Security and Packaging

- Removed the original `.env`, compiled caches, `node_modules` and unnecessary large files.
- Added environment templates and expanded `.gitignore`.
- Added setup, viva, supervisor-feedback and honest project-status documentation.
