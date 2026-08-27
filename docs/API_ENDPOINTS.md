# Main REST API Endpoints

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET | `/api/health` | Runtime, storage, queue and AI availability status | Public |
| POST | `/api/auth/register` | Register photographer/participant | Public |
| POST | `/api/auth/login` | Login and receive JWT | Public |
| GET | `/api/auth/me` | Current profile | Authenticated |
| POST | `/api/events` | Create event | Photographer/Admin |
| GET | `/api/events` | List owned/all events | Authenticated |
| GET | `/api/events/{id}` | Open event metadata | Public/code |
| PUT | `/api/events/{id}` | Edit manageable event | Photographer/Admin |
| DELETE | `/api/events/{id}` | Delete manageable event/media | Photographer/Admin |
| GET | `/api/events/{id}/qr` | Generate QR access data | Photographer/Admin |
| POST | `/api/photos/upload` | Batch upload, optimisation metrics and processing dispatch | Photographer/Admin |
| GET | `/api/photos/manage/{event}` | Review all event images/flags/metrics | Photographer/Admin |
| GET | `/api/photos/event/{event}` | Authorised gallery images | Public/code |
| GET | `/media/events/{event}/...` | Local image/thumbnail delivery | Public event or valid event code |
| GET | `/api/processing/events/{event}` | Event jobs, progress and average duration | Photographer/Admin |
| GET | `/api/processing/jobs/{job}` | Individual job status | Photographer/Admin |
| POST | `/api/face/search/{event}` | Consent-based event-scoped selfie vector search | Public/code |
| GET | `/api/photos/{id}/download` | Authorised download + audit | Public/code |
| GET | `/api/dashboard/summary` | Photographer metrics | Photographer/Admin |
| GET | `/api/admin/summary` | System monitoring | Administrator |
| GET | `/api/admin/deletion-requests` | Privacy request list | Administrator |
| PUT | `/api/admin/deletion-requests/{id}` | Resolve/reject privacy request | Administrator |
| POST | `/api/admin/privacy/purge-expired-embeddings` | Purge expired unclaimed face vectors | Administrator |
| POST | `/api/privacy/deletion-request` | Request personal-data deletion | Public |
| GET | `/api/privacy/policy` | Privacy policy summary | Public |
