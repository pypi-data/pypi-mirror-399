-- Stage 2: Chunk-level hybrid scoring with HyDE
-- %(hyde_text)s = HyDE response text
-- %(hyde_vector)s = HyDE vector embedding (float4[] length 3072)
-- %(document_uuids)s = array of document UUIDs from stage 1
-- %(vector_weight)s = vector_weight (float8)
-- %(keyword_weight)s = keyword_weight (float8)

WITH params(hyde_text, hyde_vec, doc_uuids, w_sem, w_kw) AS (
  VALUES (%(hyde_text)s::text, (%(hyde_vector)s::float4[])::vector(3072), %(document_uuids)s::uuid[], %(vector_weight)s::float8, %(keyword_weight)s::float8)
),
-- Vector similarity between HyDE and document chunks
hyde_vector_scores AS (
  SELECT
    c.chunk_uuid,
    dc.content_chunk,
    dc.document_uuid,
    d.link,
    (1 - (c.embedding <-> p.hyde_vec))::float8 AS hyde_sem_score
  FROM prod.chunks_embeddings_3072 c
  JOIN prod.document_chunks dc USING (chunk_uuid)
  JOIN prod.documents d ON dc.document_uuid = d.document_uuid
  JOIN params p ON TRUE
  WHERE dc.document_uuid = ANY(p.doc_uuids)
),
-- Term-based search between HyDE text and document chunks
hyde_keyword_scores AS (
  SELECT
    c.chunk_uuid,
    dc.content_chunk,
    dc.document_uuid,
    d.link,
    pgroonga_score(dc.tableoid, dc.ctid)::float8 AS hyde_kw_score
  FROM prod.chunks_embeddings_3072 c
  JOIN prod.document_chunks dc USING (chunk_uuid)
  JOIN prod.documents d ON dc.document_uuid = d.document_uuid
  JOIN params p ON TRUE
  WHERE dc.document_uuid = ANY(p.doc_uuids)
    AND dc.content_chunk &@ p.hyde_text
),
-- Combine vector and keyword scores
combined_scores AS (
  SELECT 
    COALESCE(v.chunk_uuid, k.chunk_uuid) AS chunk_uuid,
    COALESCE(v.content_chunk, k.content_chunk) AS content_chunk,
    COALESCE(v.document_uuid, k.document_uuid) AS document_uuid,
    COALESCE(v.link, k.link) AS link,
    COALESCE(v.hyde_sem_score, 0.0) AS hyde_sem_score,
    COALESCE(k.hyde_kw_score, 0.0) AS hyde_kw_score
  FROM hyde_vector_scores v
  FULL OUTER JOIN hyde_keyword_scores k USING (chunk_uuid)
),
-- Normalize scores
normalized AS (
  SELECT 
    chunk_uuid,
    content_chunk,
    document_uuid,
    link,
    GREATEST(0.0, hyde_sem_score) AS hyde_sem_norm,
    CASE WHEN max_kw = 0 THEN 0 ELSE hyde_kw_score / max_kw END AS hyde_kw_norm
  FROM (
    SELECT 
      c.*,
      MAX(hyde_kw_score) OVER () AS max_kw
    FROM combined_scores c
  ) x
)
SELECT
  n.content_chunk,
  n.document_uuid,
  n.link,
  (p.w_sem * n.hyde_sem_norm + p.w_kw * n.hyde_kw_norm) AS hyde_combined_score
FROM normalized n
JOIN params p ON TRUE
ORDER BY (p.w_sem * n.hyde_sem_norm + p.w_kw * n.hyde_kw_norm) DESC
LIMIT %TOP_K%;
