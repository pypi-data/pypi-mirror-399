import pytest
from yabetoo import YabetooSDK
from errors import RateLimitError
import time


@pytest.fixture
def sdk():
    return YabetooSDK("sk_test_example")


class TestRateLimiting:
    def test_rate_limit_handling(self, sdk, mocker):
        # Mock rate limit response
        mock_response = {
            "error": {
                "type": "rate_limit_error",
                "message": "Too many requests",
                "retry_after": 2
            }
        }
        mocker.patch.object(sdk.payments._client, 'request',
                            side_effect=RateLimitError("Too many requests", retry_after=2))

        start_time = time.time()

        with pytest.raises(RateLimitError) as exc_info:
            sdk.payments.retrieve("pi_test")

        assert "Too many requests" in str(exc_info.value)
        assert hasattr(exc_info.value, 'retry_after')
        assert exc_info.value.retry_after == 2

    def test_quota_exceeded(self, sdk, mocker):
        # Mock quota exceeded response
        mock_response = {
            "error": {
                "type": "quota_exceeded",
                "message": "Monthly API quota exceeded"
            }
        }
        mocker.patch.object(sdk.payments._client, 'request',
                            side_effect=APIError("Monthly API quota exceeded",
                                                 code="quota_exceeded"))

        with pytest.raises(APIError) as exc_info:
            sdk.payments.retrieve("pi_test")

        assert "Monthly API quota exceeded" in str(exc_info.value)
        assert exc_info.value.code == "quota_exceeded"

    def test_concurrent_requests(self, sdk, mocker):
        # Test handling of multiple concurrent requests
        from concurrent.futures import ThreadPoolExecutor
        import threading

        request_count = threading.Counter()

        def mock_request(*args, **kwargs):
            request_count.increment()
            if request_count.value > 5:
                raise RateLimitError("Too many concurrent requests")
            return {"id": "pi_test", "status": "succeeded"}

        mocker.patch.object(sdk.payments._client, 'request',
                            side_effect=mock_request)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(sdk.payments.retrieve, "pi_test")
                for _ in range(10)
            ]

            results = []
            errors = []
            for future in futures:
                try:
                    results.append(future.result())
                except RateLimitError:
                    errors.append("rate_limit")

        assert len(results) > 0  # Some requests should succeed
        assert len(errors) > 0   # Some should hit rate limit
