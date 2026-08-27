# Viva Demonstration Guide

## Opening

“My project is Smart Media Manager, an AI-powered event photo management system. It reduces manual event-photo work and helps participants find likely personal photographs from a private event gallery.”

## Demonstration Order

1. **Architecture health:** open `/api/health` and explain React, Flask, Celery/Redis, AI services, storage and database separation.
2. **Photographer login:** show role-protected access.
3. **Create event:** explain private access code, media retention and unclaimed vector retention.
4. **Batch upload:** upload a small controlled dataset.
5. **Asynchronous processing:** show that the upload is acknowledged before AI completion and explain the Redis queue and Celery worker.
6. **Pre-processing:** explain EXIF rotation, downscaling, compression, thumbnails, CLAHE and DeepFace alignment.
7. **AI outputs:** show blur score, duplicate flag, category and face-processing result. Explain that flags require review.
8. **Selfie search:** open the QR link, provide consent, upload one selfie and show event-restricted similarity matches.
9. **Privacy:** explain no selfie retention, private event access, expiring unclaimed embeddings and deletion requests.
10. **Limitations:** state that dynamic lighting, pose, blur and demographic variation can reduce recognition performance, so local precision/recall and false-match testing is required.

## Important Answer

“Smart Media Manager does not invent a new face-recognition algorithm. Its contribution is an integrated and evaluated event-photo workflow using established AI, cloud and web technologies.”
