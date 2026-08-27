# Supervisor Feedback Implementation Map

## 1. Scalable Media Processing Ingestion

**Feedback:** Large multi-image uploads should not block the primary Flask request.

**Implemented:**
- `backend/routes/photos.py` validates, optimises and records accepted images, then dispatches a processing job.
- `backend/tasks.py` contains the long-running blur, duplicate, face and classification pipeline.
- `backend/celery_app.py` supports Celery + Redis for queue-based deployment.
- Local demonstrations use a background thread; deterministic synchronous mode exists only for tests/benchmarks.
- `src/pages/UploadPage.jsx` polls and displays job progress separately from upload acknowledgement.

## 2. Image Pre-processing and Standardisation

**Feedback:** Raw files should not be passed directly into face/classification processing.

**Implemented:**
- EXIF orientation correction
- RGB conversion
- maximum-dimension downscaling
- JPEG optimisation
- thumbnail generation
- light contrast correction + CLAHE for the AI copy
- the normalised AI copy is now actually passed to face extraction and classification
- DeepFace alignment remains enabled when DeepFace is installed

The upload route records original size, optimised size, storage-saving percentage and preprocessing duration for measurable Chapter 6 evidence.

## 3. Real-World Face Recognition Boundaries

**Feedback:** Motion blur, low light, pose, occlusion and crowded scenes can increase false matches/rejections.

**Implemented safeguards/boundaries:**
- blur is measured before biometric interpretation
- detector confidence and face boxes can be stored with embeddings
- one event can store multiple faces per image
- cosine threshold is configurable
- participant results are presented as similarity matches, not guaranteed identity
- selfie search requires exactly one clear face
- if DeepFace is not installed/disabled, the API now returns an explicit service-unavailable response instead of incorrectly reporting "no face"

**Still requires measured research evidence:** precision, recall, false-match rate and false-rejection rate on a representative labelled event dataset.

## 4. Efficient Vector Search

`supabase/schema.sql` includes `vector(512)`, event indexing, an HNSW cosine index and an event-scoped matching RPC. The local SQLite path deliberately uses Python cosine comparison only for development-scale demonstrations.

## 5. Cloud Cost and Media Optimisation

Images are downscaled/compressed before storage, separate thumbnails are generated, retention periods are stored, and the application now records original/optimised byte counts, preprocessing time, processing time and percentage storage saving. Cloudinary account cost/egress figures still require the selected deployed account and cannot be fabricated.

## 6. Privacy, Security and Retention

Implemented controls now include:
- private events by default
- event-specific access codes
- local media delivery blocked without valid event access for private events
- JWT role checks and administrator permissions
- explicit biometric consent
- event-scoped vector matching
- no selfie file retention by the search endpoint
- unclaimed embedding expiry dates
- startup/admin purge of expired unclaimed vectors
- deletion requests with administrator resolution/rejection
- download/activity audit records
- secrets in environment variables and `.gitignore`
- Flask debug mode disabled by default
- generic client-facing unexpected-error responses

The exact consent wording, retention period and withdrawal process must still match approved university ethics documentation.
