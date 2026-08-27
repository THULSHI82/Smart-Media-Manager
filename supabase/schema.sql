-- Smart Media Manager: Supabase PostgreSQL + pgvector schema
-- Run this once in the Supabase SQL editor.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.users (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name text NOT NULL,
  email text NOT NULL UNIQUE,
  password_hash text,
  role text NOT NULL CHECK (role IN ('photographer', 'participant', 'administrator')),
  is_active smallint NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  photographer_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title text NOT NULL,
  description text,
  event_date date,
  location text,
  access_code text NOT NULL UNIQUE,
  is_public smallint NOT NULL DEFAULT 0,
  retention_days integer NOT NULL DEFAULT 90 CHECK (retention_days > 0),
  face_indexing_enabled smallint NOT NULL DEFAULT 1,
  unclaimed_embedding_days integer NOT NULL DEFAULT 30 CHECK (unclaimed_embedding_days > 0),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.categories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.images (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id uuid NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
  photographer_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  category_id uuid REFERENCES public.categories(id) ON DELETE SET NULL,
  original_filename text NOT NULL,
  storage_public_id text NOT NULL,
  image_url text NOT NULL,
  thumbnail_url text,
  width integer,
  height integer,
  file_size bigint,
  original_file_size bigint,
  preprocessing_ms double precision,
  storage_saving_percent double precision,
  processing_ms double precision,
  perceptual_hash text,
  blur_score double precision,
  is_blurry smallint NOT NULL DEFAULT 0,
  is_duplicate smallint NOT NULL DEFAULT 0,
  duplicate_of_id uuid REFERENCES public.images(id) ON DELETE SET NULL,
  classification_label text,
  classification_confidence double precision,
  processing_status text NOT NULL DEFAULT 'queued',
  processing_error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.face_embeddings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  image_id uuid NOT NULL REFERENCES public.images(id) ON DELETE CASCADE,
  event_id uuid NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
  face_index integer NOT NULL,
  model_name text NOT NULL,
  embedding_json text NOT NULL,
  embedding vector(512) NOT NULL,
  detector_confidence double precision,
  bounding_box_json text,
  is_claimed smallint NOT NULL DEFAULT 0,
  expires_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (image_id, face_index, model_name)
);

CREATE INDEX IF NOT EXISTS face_embeddings_event_idx ON public.face_embeddings(event_id);
CREATE INDEX IF NOT EXISTS face_embeddings_hnsw_cosine_idx
  ON public.face_embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS images_event_idx ON public.images(event_id);
CREATE INDEX IF NOT EXISTS images_processing_status_idx ON public.images(processing_status);

CREATE TABLE IF NOT EXISTS public.processing_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id uuid NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
  image_id uuid REFERENCES public.images(id) ON DELETE CASCADE,
  task_id text,
  job_type text NOT NULL,
  status text NOT NULL DEFAULT 'queued',
  progress integer NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  message text,
  error text,
  started_at timestamptz,
  completed_at timestamptz,
  duration_ms double precision,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Safe schema upgrades for databases created from earlier project versions.
ALTER TABLE public.images ADD COLUMN IF NOT EXISTS original_file_size bigint;
ALTER TABLE public.images ADD COLUMN IF NOT EXISTS preprocessing_ms double precision;
ALTER TABLE public.images ADD COLUMN IF NOT EXISTS storage_saving_percent double precision;
ALTER TABLE public.images ADD COLUMN IF NOT EXISTS processing_ms double precision;
ALTER TABLE public.processing_jobs ADD COLUMN IF NOT EXISTS duration_ms double precision;

CREATE TABLE IF NOT EXISTS public.download_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
  image_id uuid NOT NULL REFERENCES public.images(id) ON DELETE CASCADE,
  event_id uuid NOT NULL REFERENCES public.events(id) ON DELETE CASCADE,
  requester_ip text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.consents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id uuid REFERENCES public.events(id) ON DELETE CASCADE,
  user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
  consent_type text NOT NULL,
  consent_version text NOT NULL,
  accepted smallint NOT NULL,
  requester_ip text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.deletion_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
  email text NOT NULL,
  reason text,
  status text NOT NULL DEFAULT 'pending',
  created_at timestamptz NOT NULL DEFAULT now(),
  resolved_at timestamptz
);

CREATE TABLE IF NOT EXISTS public.activity_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text,
  details_json text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- HNSW cosine search restricted to one event. The Flask service applies access control
-- before calling this RPC with the service role key.
CREATE OR REPLACE FUNCTION public.match_event_faces(
  query_embedding vector(512),
  target_event_id uuid,
  match_threshold double precision DEFAULT 0.68,
  match_count integer DEFAULT 100
)
RETURNS TABLE (
  image_id uuid,
  image_url text,
  thumbnail_url text,
  filename text,
  category text,
  similarity double precision,
  confidence_percent double precision
)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT DISTINCT ON (i.id)
    i.id,
    i.image_url,
    i.thumbnail_url,
    i.original_filename,
    i.classification_label,
    1 - (f.embedding <=> query_embedding) AS similarity,
    round(((1 - (f.embedding <=> query_embedding)) * 100)::numeric, 2)::double precision
  FROM public.face_embeddings f
  JOIN public.images i ON i.id = f.image_id
  WHERE f.event_id = target_event_id
    AND i.processing_status = 'completed'
    AND i.is_blurry = 0
    AND i.is_duplicate = 0
    AND 1 - (f.embedding <=> query_embedding) >= match_threshold
  ORDER BY i.id, f.embedding <=> query_embedding
  LIMIT match_count;
$$;

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.face_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.download_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deletion_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_read_own ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY users_update_own ON public.users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY photographers_manage_own_events ON public.events FOR ALL USING (auth.uid() = photographer_id) WITH CHECK (auth.uid() = photographer_id);
CREATE POLICY photographers_manage_own_images ON public.images FOR ALL USING (auth.uid() = photographer_id) WITH CHECK (auth.uid() = photographer_id);
CREATE POLICY photographers_read_event_embeddings ON public.face_embeddings FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.events e WHERE e.id = face_embeddings.event_id AND e.photographer_id = auth.uid())
);
CREATE POLICY photographers_read_jobs ON public.processing_jobs FOR SELECT USING (
  EXISTS (SELECT 1 FROM public.events e WHERE e.id = processing_jobs.event_id AND e.photographer_id = auth.uid())
);

-- Removes temporary, unclaimed facial vectors after the event-configured retention period.
-- Schedule this function daily with Supabase Cron after reviewing the approved ethics policy.
CREATE OR REPLACE FUNCTION public.purge_expired_unclaimed_embeddings()
RETURNS integer
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $$
DECLARE deleted_count integer;
BEGIN
  DELETE FROM public.face_embeddings
  WHERE is_claimed = 0 AND expires_at IS NOT NULL AND expires_at < now();
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$;
