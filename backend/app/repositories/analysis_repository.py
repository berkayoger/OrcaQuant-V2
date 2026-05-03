from __future__ import annotations

from app.extensions import db
from app.models.analysis_result import AnalysisResult


class AnalysisRepository:
    def create_analysis_result(self, asset_id: str, analysis_type: str, payload: dict) -> dict:
        row = AnalysisResult(asset_id=asset_id, analysis_type=analysis_type, payload_json=payload)
        db.session.add(row)
        db.session.commit()
        return self._to_dict(row)

    def get_latest_for_asset(self, asset_id: str, analysis_type: str = "technical") -> dict | None:
        row = (
            AnalysisResult.query.filter_by(asset_id=asset_id, analysis_type=analysis_type)
            .order_by(AnalysisResult.created_at.desc())
            .first()
        )
        return self._to_dict(row) if row else None

    def _to_dict(self, row: AnalysisResult) -> dict:
        return {
            "id": row.id,
            "asset_id": row.asset_id,
            "analysis_type": row.analysis_type,
            "payload_json": row.payload_json,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
