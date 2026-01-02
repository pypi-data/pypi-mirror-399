import pytest
from yabetoo import YabetooSDK
from models.payment import (
    CreateIntentRequest,
    ConfirmIntentRequest,
    PaymentMethodData,
    MomoData
)
from errors import YabetooError, ValidationError, APIError, NetworkError
from decimal import Decimal

@pytest.fixture
def sdk():
    return YabetooSDK("sk_test_example")

class TestPaymentEdgeCases:
    def test_zero_amount_payment(self, sdk, mocker):
        with pytest.raises(ValidationError) as exc_info:
            sdk.payments.create(CreateIntentRequest(
                amount=0,
                currency="xaf"
            ))
        assert "amount must be greater than 0" in str(exc_info.value)

    def test_extremely_large_amount(self, sdk, mocker):
        with pytest.raises(ValidationError) as exc_info:
            sdk.payments.create(CreateIntentRequest(
                amount=1000000000000,  # 1 trillion
                currency="xaf"
            ))
        assert "amount exceeds maximum allowed" in str(exc_info.value)

    def test_invalid_currency(self, sdk, mocker):
        with pytest.raises(ValidationError) as exc_info:
            sdk.payments.create(CreateIntentRequest(
                amount=1000,
                currency="invalid"
            ))
        assert "currency is not supported" in str(exc_info.value)

    def test_empty_description(self, sdk, mocker):
        # Should work with empty description
        mock_response = {"id": "pi_test", "amount": "1000", "currency": "xaf"}
        mocker.patch.object(sdk.payments._client, 'request', return_value=mock_response)
        
        result = sdk.payments.create(CreateIntentRequest(
            amount=1000,
            currency="xaf",
            description=""
        ))
        assert result.id == "pi_test"

    def test_special_characters_metadata(self, sdk, mocker):
        mock_response = {"id": "pi_test", "metadata": {"key": "value!@#$%^"}}
        mocker.patch.object(sdk.payments._client, 'request', return_value=mock_response)

        result = sdk.payments.create(CreateIntentRequest(
            amount=1000,
            currency="xaf",
            metadata={"key": "value!@#$%^"}
        ))
        assert result.metadata["key"] == "value!@#$%^"

class TestMomoEdgeCases:
    def test_invalid_phone_number_format(self, sdk, mocker):
        with pytest.raises(ValidationError) as exc_info:
            sdk.payments.confirm("pi_test", ConfirmIntentRequest(
                client_secret="cs_test",
                payment_method_data=PaymentMethodData(
                    type="momo",
                    momo=MomoData(
                        country="cg",
                        msisdn="invalid",
                        operator_name="mtn"
                    )
                )
            ))
        assert "invalid phone number format" in str(exc_info.value)

    def test_unsupported_operator(self, sdk, mocker):
        with pytest.raises(ValidationError) as exc_info:
            sdk.payments.confirm("pi_test", ConfirmIntentRequest(
                client_secret="cs_test",
                payment_method_data=PaymentMethodData(
                    type="momo",
                    momo=MomoData(
                        country="cg",
                        msisdn="+242123456789",
                        operator_name="unsupported"
                    )
                )
            ))
        assert "unsupported operator" in str(exc_info.value)

class TestNetworkEdgeCases:
    def test_timeout_handling(self, sdk, mocker):
        mocker.patch.object(sdk.payments._client, 'request', 
                          side_effect=NetworkError("Request timed out"))
        
        with pytest.raises(NetworkError) as exc_info:
            sdk.payments.retrieve("pi_test")
        assert "Request timed out" in str(exc_info.value)

    def test_retry_mechanism(self, sdk, mocker):
        # Mock network failure then success
        mock_calls = [
            NetworkError("Connection failed"),
            {"id": "pi_test", "status": "succeeded"}
        ]
        mock = mocker.patch.object(sdk.payments._client, 'request', 
                                 side_effect=mock_calls)
        
        result = sdk.payments.retrieve_with_retry("pi_test", max_retries=2)
        assert result.status == "succeeded"
        assert mock.call_count == 2

class TestAuthenticationEdgeCases:
    def test_invalid_api_key(self):
        with pytest.raises(ValidationError) as exc_info:
            YabetooSDK("")  # Empty API key
        assert "invalid API key" in str(exc_info.value)

    def test_malformed_api_key(self):
        with pytest.raises(ValidationError) as exc_info:
            YabetooSDK("invalid_key_format")
        assert "malformed API key" in str(exc_info.value)

class TestConcurrencyEdgeCases:
    def test_idempotency_key(self, sdk, mocker):
        # Same request with same idempotency key should return same result
        mock_response = {"id": "pi_test", "amount": "1000"}
        mock = mocker.patch.object(sdk.payments._client, 'request', 
                                 return_value=mock_response)

        request_data = CreateIntentRequest(
            amount=1000,
            currency="xaf"
        )

        result1 = sdk.payments.create(request_data, idempotency_key="key1")
        result2 = sdk.payments.create(request_data, idempotency_key="key1")

        assert result1.id == result2.id
        assert mock.call_count == 1  # Should only make one actual API call

class TestDataValidationEdgeCases:
    @pytest.mark.parametrize("invalid_amount", [
        -1000,  # Negative amount
        "1000",  # String instead of number
        None,   # None value
        Decimal("1000.50"),  # Decimal with cents
    ])
    def test_invalid_amount_types(self, sdk, invalid_amount):
        with pytest.raises(ValidationError):
            sdk.payments.create(CreateIntentRequest(
                amount=invalid_amount,
                currency="xaf"
            ))

    def test_null_values_in_metadata(self, sdk, mocker):
        mock_response = {"id": "pi_test", "metadata": {"key": None}}
        mocker.patch.object(sdk.payments._client, 'request', return_value=mock_response)

        result = sdk.payments.create(CreateIntentRequest(
            amount=1000,
            currency="xaf",
            metadata={"key": None}
        ))
        assert result.metadata["key"] is None