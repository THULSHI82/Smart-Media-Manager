# Smart Media Manager

**AI-Powered Event Photo Management System**

Smart Media Manager is a React and Flask web application for event photographers and participants. A photographer creates an event, batch-uploads photographs and monitors a separate AI-processing pipeline. Participants open an authorised event, provide explicit biometric-processing consent, upload one selfie and receive likely matching photographs.

The project is structured to match the dissertation design:

- **Frontend:** React.js + Vite + Tailwind CSS
- **Backend:** Flask REST API + JWT role controls
- **Background processing:** Celery + Redis, with a local threaded fallback for simple demonstrations
- **Media storage:** Cloudinary, with local development storage fallback
- **Database:** Supabase PostgreSQL + pgvector, with SQLite fallback for immediate local demonstration
- **AI/image processing:** OpenCV, ImageHash, DeepFace and an optional TensorFlow classification model

## Implemented Functions

### Photographer

- Register and log in
- Create private or public events
- Generate event access codes and QR links
- Configure image and unclaimed face-vector retention periods
- Batch-upload JPEG, PNG and WebP photographs
- View upload acceptance separately from AI-processing status
- Review blur and duplicate flags rather than silently deleting files
- View category labels, processing progress and failures

### Participant

- Open an event using an event ID and access code
- Read and accept a biometric-processing consent notice
- Upload one selfie for event-scoped matching
- View similarity-ranked likely matches
- Download authorised photographs
- Submit a personal-data deletion request

### Administrator

- View user, event, image, download, failed-job and deletion-request totals
- Review recent system activity
- Resolve/reject deletion requests and purge expired unclaimed face vectors
- Manage event/processing records with administrator permissions

## Supervisor Feedback Addressed

1. **Scalable ingestion:** uploads are accepted first, then `processing_jobs` are dispatched to Celery through Redis. The Flask request does not need to remain open while face recognition finishes.
2. **Pre-processing:** EXIF orientation correction, downscaling, JPEG optimisation, thumbnail creation and CLAHE lighting normalisation are included. DeepFace face alignment is enabled.
3. **Real-world recognition limits:** similarity thresholds are configurable, results are presented as likely matches, and the code does not claim perfect biometric identification. Local precision, recall, false-match and false-rejection testing is still required.
4. **Vector search:** `supabase/schema.sql` contains a 512-dimensional pgvector field, an HNSW cosine index and an event-restricted matching function.
5. **Cloud cost boundaries:** optimised images and smaller thumbnails are uploaded instead of unrestricted raw files. Retention periods are stored per event.
6. **Privacy controls:** private event access codes, protected local media delivery, explicit consent, in-memory selfie processing, role checks, activity records, deletion requests and automatic expiry/purging of unclaimed face embeddings are included.

A detailed mapping is available in `docs/SUPERVISOR_FEEDBACK_IMPLEMENTATION.md`.

## Important Academic Boundary

The code provides the implementation and measurement tools, but it does **not** fabricate evaluation results. Accuracy, precision, recall, response time, SUS scores and load-test results must be collected using the final test dataset and reported in the dissertation with the sample size and test conditions.

## Quick Local Setup

Use **Python 3.11** for the AI dependency versions supplied here.

### 1. Frontend

```bash
cd Smart_Media_Manager_Completed
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

### 2. Backend core

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_demo.py
python app.py
```

The API runs on `http://localhost:5001`.

The demo seed creates:

- `photographer@example.com`
- `admin@example.com`
- Password: `Demo1234`

Change this password before any public demonstration.

### 3. Enable DeepFace and TensorFlow

```bash
pip install -r requirements-ai.txt
```

The first DeepFace use may need model files. Allow time for the model setup before a viva demonstration. For a custom event classifier, set:

```env
CLASSIFIER_BACKEND=tensorflow
CLASSIFICATION_MODEL_PATH=/absolute/path/to/model.keras
```

Without a supplied trained model, the application uses a clearly labelled heuristic category fallback so the rest of the workflow remains demonstrable.

## Celery and Redis

Start Redis:

```bash
docker compose up redis -d
```

Set in `backend/.env`:

```env
USE_CELERY=true
REDIS_URL=redis://localhost:6379/0
```

Run the API and worker in separate terminals:

```bash
python app.py
```

```bash
celery -A celery_app.celery worker --loglevel=info
```

For a simple local demonstration without Redis, keep `USE_CELERY=false`. The same processing pipeline runs through a local fallback, but the dissertation deployment architecture should use Celery and Redis.

## Cloudinary Configuration

Set:

```env
STORAGE_BACKEND=cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
```

Do not commit `.env`. The repository includes only `.env.example`.

## Supabase PostgreSQL and pgvector

1. Create a Supabase project.
2. Run `supabase/schema.sql` in the Supabase SQL editor.
3. Copy the project API values and PostgreSQL connection string into `backend/.env`.
4. Set:

```env
DATA_BACKEND=supabase
AUTH_BACKEND=supabase
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
SUPABASE_DB_URL=postgresql://...
```

The Flask API uses the database connection for structured records and the Supabase RPC for HNSW cosine vector matching. The service-role key must remain server-side only.

## Tests

```bash
cd backend
pytest -q
```

The included automated suite currently contains 15 tests covering health reporting, real login, role restrictions, private-event access, administrator event management, preprocessing, upload/processing, duplicate detection, protected local media, invalid uploads, privacy requests and the face-search availability boundary. Add project-specific labelled AI test data before reporting final accuracy.

## Security Checklist Before Submission

- Rotate every key that was previously stored in the original `.env` file.
- Keep `.env`, `node_modules`, `.venv`, model caches and uploaded user photos out of the submitted ZIP.
- Use HTTPS for deployed frontend/API traffic.
- Use private events by default.
- Review the Supabase RLS policies and service-role permissions.
- Run the expired-embedding cleanup task according to the approved ethics and retention policy.
- Do not describe similarity results as guaranteed identification.

## Main Project Structure

```text
src/
  components/          landing and application shell components
  pages/               login, dashboard, events, upload, selfie search, admin, privacy
  lib/                 API and navigation helpers
backend/
  routes/              Flask API routes
  services/            preprocessing, storage, blur, duplicate, face, classification, vector search
  tasks.py             complete image-processing pipeline
  celery_app.py        Celery/Redis worker entry point
  schema.sql           local SQLite demonstration schema
  tests/               automated tests
  scripts/             demo seed and retention cleanup
supabase/schema.sql     PostgreSQL, pgvector HNSW, RPC and RLS design
```

## Demonstration Flow

1. Log in as the photographer.
2. Create a private event and note its access code.
3. Upload a small prepared set containing clear, blurry and duplicate photographs.
4. Show the processing status changing, measured processing time/storage saving and review the AI flags.
5. Open the QR/selfie-search link.
6. Accept the privacy notice and submit a clear selfie.
7. Display likely matching photos and the similarity percentages.
8. Open the administrator dashboard and privacy page.

See `docs/VIVA_DEMO_GUIDE.md` for a speaking guide.
