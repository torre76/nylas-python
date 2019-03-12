from datetime import datetime
import pytest
from nylas.client.restful_models import Account, APIAccount, SingletonAccount


def test_create_account(api_client, monkeypatch):
    monkeypatch.setattr(api_client, "is_opensource_api", lambda: False)
    account = api_client.accounts.create()
    assert isinstance(account, Account)


def test_create_apiaccount(api_client, monkeypatch):
    monkeypatch.setattr(api_client, "is_opensource_api", lambda: True)
    account = api_client.accounts.create()
    assert isinstance(account, APIAccount)


def test_account_json(api_client, monkeypatch):
    monkeypatch.setattr(api_client, "is_opensource_api", lambda: False)
    account = api_client.accounts.create()
    result = account.as_json()
    assert isinstance(result, dict)


@pytest.mark.usefixtures("mock_ip_addresses")
def test_ip_addresses(api_client_with_app_id):
    result = api_client_with_app_id.ip_addresses()
    assert isinstance(result, dict)


@pytest.mark.usefixtures("mock_account")
def test_account_datetime(api_client):
    account = api_client.account
    assert account.linked_at == datetime(2017, 7, 24, 18, 18, 19)


@pytest.mark.usefixtures("mock_accounts", "mock_account_management")
def test_account_upgrade(api_client, app_id):
    api_client.app_id = app_id
    account = api_client.accounts.first()
    assert account.billing_state == "paid"
    account = account.downgrade()
    assert account.billing_state == "cancelled"
    account = account.upgrade()
    assert account.billing_state == "paid"


def test_account_delete(api_client, monkeypatch):
    monkeypatch.setattr(api_client, "is_opensource_api", lambda: False)
    account = api_client.accounts.create()
    with pytest.raises(NotImplementedError):
        account.delete()


@pytest.mark.usefixtures("mock_revoke_all_tokens", "mock_account")
def test_revoke_all_tokens(api_client_with_app_id):
    assert api_client_with_app_id.access_token is not None
    api_client_with_app_id.revoke_all_tokens()
    assert api_client_with_app_id.access_token is None


@pytest.mark.usefixtures("mock_revoke_all_tokens", "mock_account")
def test_revoke_all_tokens_with_keep_access_token(api_client_with_app_id, access_token):
    assert api_client_with_app_id.access_token == access_token
    api_client_with_app_id.revoke_all_tokens(keep_access_token=access_token)
    assert api_client_with_app_id.access_token == access_token


@pytest.mark.usefixtures("mock_accounts", "mock_account")
def test_account_access(api_client):
    account1 = api_client.account
    assert isinstance(account1, SingletonAccount)
    account2 = api_client.accounts[0]
    assert isinstance(account2, APIAccount)
    account3 = api_client.accounts.first()
    assert isinstance(account3, APIAccount)
    assert account1.as_json() == account2.as_json() == account3.as_json()
