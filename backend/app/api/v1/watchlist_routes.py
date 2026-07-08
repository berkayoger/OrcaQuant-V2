from __future__ import annotations

from flask import Blueprint, g, request

from app.common.responses import error_response, ok
from app.core.security.auth_guard import require_auth
from app.extensions import db
from app.models.watchlist import Watchlist
from app.services.dashboard.market_cockpit_service import MarketCockpitService

watchlist_bp = Blueprint("watchlist", __name__)


def _normalize_symbols(symbols: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for symbol in symbols:
        clean = "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())
        if clean and clean not in seen:
            seen.add(clean)
            normalized.append(clean)
    return normalized[:25]


def _get_or_create_watchlist() -> Watchlist:
    watchlist = Watchlist.query.filter_by(user_id=g.current_user.id).order_by(Watchlist.created_at.asc()).first()
    if not watchlist:
        watchlist = Watchlist(user_id=g.current_user.id, data={"symbols": []})
        db.session.add(watchlist)
        db.session.commit()
    return watchlist


def _serialize(watchlist: Watchlist) -> dict:
    data = watchlist.data or {}
    return {
        "id": watchlist.id,
        "user_id": watchlist.user_id,
        "symbols": _normalize_symbols(data.get("symbols") or []),
        "created_at": watchlist.created_at.isoformat() if watchlist.created_at else None,
        "updated_at": watchlist.updated_at.isoformat() if watchlist.updated_at else None,
    }


@watchlist_bp.get("/")
@require_auth
def get_watchlist():
    return ok(_serialize(_get_or_create_watchlist()))


@watchlist_bp.put("/")
@require_auth
def replace_watchlist():
    payload = request.get_json(silent=True) or {}
    symbols = payload.get("symbols")
    if not isinstance(symbols, list):
        return error_response("validation_error", "symbols must be a list", 400)
    watchlist = _get_or_create_watchlist()
    watchlist.data = {"symbols": _normalize_symbols(symbols)}
    db.session.commit()
    return ok(_serialize(watchlist))


@watchlist_bp.post("/symbols")
@require_auth
def add_watchlist_symbol():
    payload = request.get_json(silent=True) or {}
    symbol = payload.get("symbol")
    if not symbol:
        return error_response("validation_error", "symbol is required", 400)
    watchlist = _get_or_create_watchlist()
    symbols = _normalize_symbols((watchlist.data or {}).get("symbols") or [])
    symbols = _normalize_symbols([*symbols, symbol])
    watchlist.data = {"symbols": symbols}
    db.session.commit()
    return ok(_serialize(watchlist))


@watchlist_bp.delete("/symbols/<symbol>")
@require_auth
def remove_watchlist_symbol(symbol: str):
    watchlist = _get_or_create_watchlist()
    symbols = [item for item in _normalize_symbols((watchlist.data or {}).get("symbols") or []) if item != symbol.upper().strip()]
    watchlist.data = {"symbols": symbols}
    db.session.commit()
    return ok(_serialize(watchlist))


@watchlist_bp.get("/cockpit")
@require_auth
def get_watchlist_cockpit():
    watchlist = _get_or_create_watchlist()
    symbols = _serialize(watchlist)["symbols"]
    cockpit = MarketCockpitService().build_cockpit(symbols=symbols or None, watchlist_symbols=symbols)
    return ok(cockpit)
