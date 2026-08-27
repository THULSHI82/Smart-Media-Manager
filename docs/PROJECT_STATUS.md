# Project Status and Honest Boundaries

## Verified core implementation

The source includes a complete local demonstration path using React, Flask, SQLite, local media storage and a threaded background-processing fallback. The automated backend suite contains **15 tests** and covers health reporting, real login, role restrictions, event access, administrator event management, image preprocessing, upload/processing, duplicate detection, protected local media delivery, privacy requests and the face-AI availability boundary.

Implemented areas include:

- React landing page and application pages
- Local registration/login and optional Supabase Auth
- Photographer, participant and administrator roles
- Event creation, access codes, QR links and retention configuration
- Multi-image upload with measured preprocessing time and storage reduction
- EXIF correction, resizing, compression, thumbnails and CLAHE normalisation
- CLAHE-normalised AI copy used by face/classification processing
- Celery/Redis architecture with local threaded fallback
- Blur scoring and review flags
- Perceptual-hash duplicate flags
- Multi-face DeepFace embedding extraction when AI dependencies are installed
- Explicit 503 service response when face AI is unavailable instead of a false "no face" result
- Optional TensorFlow model loading plus a labelled heuristic fallback classifier
- SQLite demo database and Supabase PostgreSQL/pgvector deployment schema
- HNSW cosine vector search design
- Selfie-search consent, event scope and no selfie-file retention
- Private local media protected by the event access code
- Processing status, measured processing duration, activity records and downloads
- Deletion requests, administrator resolution and expired-vector purge
- Expanded automated tests and evaluation scaffolding

## Still requires external configuration or measured evidence

These are not fabricated or reported as complete results:

- Cloudinary credentials and deployed cloud-media security tests
- Supabase project values and execution of the SQL schema
- Redis service and Celery worker for true queue-based deployment
- DeepFace/TensorFlow installation and model cache on the demonstration Mac
- A trained event-category TensorFlow model if the dissertation claims trained classification
- A labelled event-photo test dataset
- Measured face precision/recall/false-match/false-rejection results
- Labelled blur/duplicate/classification accuracy results
- Load-test and usability results
- Final ethics-approved consent wording and participant sample

The local application remains fully usable for event creation, uploads, preprocessing, blur/duplicate analysis, gallery management, QR access, privacy controls and dashboards even when the optional DeepFace/TensorFlow/cloud services are not configured.
