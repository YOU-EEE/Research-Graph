"""Generate AI semantic data for knowledge graph enrichment."""
import sys
sys.path.insert(0, '.')

from database import SessionLocal
from services import ai_service

db = SessionLocal()

# Get all paper IDs
from models import Paper
papers = db.query(Paper).all()
paper_ids = [p.paper_id for p in papers]
print(f"Processing {len(paper_ids)} papers...")

# ── 1. Generate similarity for each paper ──
# _corpus() computes embeddings once and caches them
sim_count = 0
for pid in paper_ids:
    try:
        results = ai_service.generate_similarity(db, pid, mode="local", top_k=None)
        sim_count += len(results)
        print(f"  Paper {pid}: {len(results)} similar papers")
    except Exception as e:
        print(f"  Paper {pid} ERROR: {e}")

# ── 2. Generate relation suggestions for each paper ──
rel_count = 0
for pid in paper_ids:
    try:
        results = ai_service.generate_relation_suggestions(db, pid, mode="local")
        rel_count += len(results)
        print(f"  Paper {pid}: {len(results)} relation suggestions")
    except Exception as e:
        print(f"  Paper {pid} ERROR: {e}")

# ── 3. Auto-accept high-confidence relation suggestions ──
from models import AIRelationSuggestion
high_conf = (
    db.query(AIRelationSuggestion)
    .filter(AIRelationSuggestion.confidence >= 0.40)
    .all()
)
accepted_rel = 0
for sug in high_conf:
    try:
        ai_service.accept_relation_suggestion(db, sug.suggestion_id)
        accepted_rel += 1
    except Exception:
        db.rollback()
print(f"Auto-accepted {accepted_rel} high-confidence relations")

# ── 4. Generate clusters ──
try:
    clusters = ai_service.generate_clusters(db, project_id=None, num_clusters=5, mode="local")
    print(f"Generated {len(clusters)} clusters:")
    for c in clusters:
        print(f"  [{c['cluster_id']}] {c['label']}: {c['num_papers']} papers")
except Exception as e:
    print(f"Cluster ERROR: {e}")

# ── 5. Generate tag suggestions ──
tag_count = 0
for pid in paper_ids:
    try:
        results = ai_service.generate_tag_suggestions(db, pid, mode="local")
        tag_count += len(results)
        if results:
            print(f"  Paper {pid}: {len(results)} tag suggestions — {[r.tag_name for r in results[:5]]}")
    except Exception as e:
        print(f"  Paper {pid} ERROR: {e}")

print(f"\nTotal: {sim_count} similarities, {rel_count} relations, {accepted_rel} accepted, {tag_count} tag suggestions")
db.close()
