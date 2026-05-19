from app.services.usage.usage_service import UsageService


def test_usage_payload_shape():
    status = UsageService()._build_status(3, 10)
    for k in ["used", "quota", "remaining", "percent", "warn75", "warn90", "exhausted"]:
        assert k in status
