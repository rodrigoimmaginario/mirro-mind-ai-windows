"""Durable Explorer Story persistence operations."""

from __future__ import annotations

import json
from typing import Any

from memory.models import _now, _uuid
from memory.storage.base import ConnectionBacked


class ExplorerStoryStore(ConnectionBacked):
    """Storage operations for durable Exploratory Stories."""

    def get_active_explorer_story_record(self, journey: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """SELECT * FROM exploratory_stories
               WHERE journey = ? AND status = 'active'
               ORDER BY updated_at DESC
               LIMIT 1""",
            (journey,),
        ).fetchone()
        return dict(row) if row else None

    def list_explorer_story_records(self, journey: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT * FROM exploratory_stories
               WHERE journey = ?
               ORDER BY
                 CASE status
                   WHEN 'active' THEN 0
                   WHEN 'promoted' THEN 1
                   WHEN 'archived' THEN 2
                   ELSE 3
                 END,
                 updated_at DESC""",
            (journey,),
        ).fetchall()
        return [dict(row) for row in rows]

    def upsert_active_explorer_story_record(
        self,
        *,
        journey: str,
        title: str | None,
        current_story: str | None,
        narrative_summary: str | None,
        last_story_card: str | None,
        attractors: list[dict[str, Any]],
        experiment_proposal: dict[str, Any] | None,
        builder_handoff: dict[str, Any] | None,
        source_conversations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        now = _now()
        existing = self.get_active_explorer_story_record(journey)
        record_id = existing["id"] if existing else _uuid()
        created_at = existing["created_at"] if existing else now
        self.conn.execute(
            """INSERT INTO exploratory_stories
               (id, journey, title, status, current_story, narrative_summary,
                last_story_card, attractors_json, experiment_proposal_json,
                builder_handoff_json, source_conversations_json, created_at, updated_at)
               VALUES (?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 title = excluded.title,
                 current_story = excluded.current_story,
                 narrative_summary = excluded.narrative_summary,
                 last_story_card = excluded.last_story_card,
                 attractors_json = excluded.attractors_json,
                 experiment_proposal_json = excluded.experiment_proposal_json,
                 builder_handoff_json = excluded.builder_handoff_json,
                 source_conversations_json = excluded.source_conversations_json,
                 updated_at = excluded.updated_at""",
            (
                record_id,
                journey,
                title,
                current_story,
                narrative_summary,
                last_story_card,
                json.dumps(attractors, ensure_ascii=False),
                json.dumps(experiment_proposal, ensure_ascii=False)
                if experiment_proposal
                else None,
                json.dumps(builder_handoff, ensure_ascii=False) if builder_handoff else None,
                json.dumps(source_conversations or [], ensure_ascii=False),
                created_at,
                now,
            ),
        )
        self.conn.commit()
        record = self.get_active_explorer_story_record(journey)
        if record is None:  # defensive: should be impossible after insert/update
            raise RuntimeError("failed to persist active Exploratory Story")
        return record

    def archive_active_explorer_story_record(self, journey: str) -> dict[str, Any] | None:
        existing = self.get_active_explorer_story_record(journey)
        if not existing:
            return None
        now = _now()
        self.conn.execute(
            """UPDATE exploratory_stories
               SET status = 'archived', archived_at = ?, updated_at = ?
               WHERE id = ?""",
            (now, now, existing["id"]),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM exploratory_stories WHERE id = ?",
            (existing["id"],),
        ).fetchone()
        return dict(row) if row else None

    def mark_active_explorer_story_promoted(self, journey: str) -> dict[str, Any] | None:
        existing = self.get_active_explorer_story_record(journey)
        if not existing:
            return None
        now = _now()
        self.conn.execute(
            """UPDATE exploratory_stories
               SET status = 'promoted', promoted_at = ?, updated_at = ?
               WHERE id = ?""",
            (now, now, existing["id"]),
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM exploratory_stories WHERE id = ?",
            (existing["id"],),
        ).fetchone()
        return dict(row) if row else None
