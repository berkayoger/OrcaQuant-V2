from app.extensions import db
from app.models.monte_carlo_result import MonteCarloResult


class MonteCarloRepository:
    def create_result(self, asset_id: str, payload: dict, analysis_id: str | None = None) -> dict:
        row = MonteCarloResult(asset_id=asset_id, analysis_id=analysis_id, payload_json=payload)
        db.session.add(row)
        db.session.commit()
        return self._to_dict(row)

    def get_latest_for_asset(self, asset_id: str) -> dict | None:
        row = MonteCarloResult.query.filter_by(asset_id=asset_id).order_by(MonteCarloResult.created_at.desc()).first()
        return self._to_dict(row) if row else None

    def _to_dict(self, row: MonteCarloResult) -> dict:
        return {"id": row.id, "asset_id": row.asset_id, "analysis_id": row.analysis_id, "payload_json": row.payload_json}
