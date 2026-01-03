from http import HTTPStatus
from logos_sdk.services import get_headers, get_retry_session
from typing import Any, Generator, List
from dotenv import load_dotenv
import os


class MicrosoftAdvertisingMerchantCenterException(Exception):
    pass


class MicrosoftAdvertisingMerchantCenter:
    def __init__(self, url=None):
        load_dotenv()
        self.session = get_retry_session()
        self._URL = url or os.environ.get("MICROSOFT_ADVERTISING_MERCHANT_CENTER_PATH")
        self._GET_ACCESSIBLE_ACCOUNTS = self._URL + "/accessible-accounts"
        self._GET_ACCOUNT_ACCESSIBILITY = self._URL + "/get-account-accessibility"
        self._GET_PRODUCTS_STATUSES_SUMMARY = (
                self._URL + "/get-products-statuses-summary"
        )
        self._GET_PRODUCTS = self._URL + "/get-products"
        self._GET_STORES = self._URL + "/get-stores"
        self._GET_STORE = self._URL + "/get-store"

    def get_accessible_accounts(self, secret_id: str) -> List[dict]:
        """
        Gets accessible accounts
        :param secret_id: The ID of the secret in secret manager
        :return: List of dicts with account_id and name keys
        """
        body = {"secret_id": secret_id}
        header = get_headers(self._GET_ACCESSIBLE_ACCOUNTS)
        response = self.session.request(
            "post", url=self._GET_ACCESSIBLE_ACCOUNTS, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MicrosoftAdvertisingMerchantCenterException(response.content)

    def get_account_accessibility(
            self, secret_id: str, customer_id, customer_account_id, merchant_id: str
    ) -> bool:
        """
        Gets account accessibility
        :param secret_id: The ID of the secret in secret manager
        :param customer_id: The ID of the customer (parent ID) in Microsoft Advertising
        :param customer_account_id: The ID of the customer account in Microsoft Advertising
        :param merchant_id: The ID of the store in Microsoft Advertising
        :return: True if account has access
        """
        body = {
            "secret_id": secret_id,
            "customer_id": customer_id,
            "customer_account_id": customer_account_id,
            "merchant_id": merchant_id,
        }
        header = get_headers(self._GET_ACCOUNT_ACCESSIBILITY)
        response = self.session.request(
            "post", url=self._GET_ACCOUNT_ACCESSIBILITY, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MicrosoftAdvertisingMerchantCenterException(response.content)

    def get_products_statuses_summary(
            self, secret_id: str, customer_id, customer_account_id, merchant_id: str
    ) -> dict:
        """
        Gets products statuses summary
        :param secret_id: The ID of the secret in secret manager
        :param customer_id: The ID of the customer (parent ID) in Microsoft Advertising
        :param customer_account_id: The ID of the customer account in Microsoft Advertising
        :param merchant_id: The ID of the store in Microsoft Advertising
        :return: products statuses summary
        """
        body = {
            "secret_id": secret_id,
            "customer_id": customer_id,
            "customer_account_id": customer_account_id,
            "merchant_id": merchant_id,
        }
        header = get_headers(self._GET_PRODUCTS_STATUSES_SUMMARY)
        response = self.session.request(
            "post", url=self._GET_PRODUCTS_STATUSES_SUMMARY, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MicrosoftAdvertisingMerchantCenterException(response.content)

    def get_products(
            self,
            secret_id: str,
            customer_id,
            customer_account_id,
            merchant_id: str,
            page_size: int = 250,
    ) -> Generator[Any, Any, Any]:
        """
        Gets products
        :param secret_id: The ID of the secret in secret manager
        :param customer_id: The ID of the customer (parent ID) in Microsoft Advertising
        :param customer_account_id: The ID of the customer account in Microsoft Advertising
        :param merchant_id: The ID of the store in Microsoft Advertising
        :param page_size: page size
        :return: products
        """

        body = {
            "secret_id": secret_id,
            "customer_id": customer_id,
            "customer_account_id": customer_account_id,
            "merchant_id": merchant_id,
            "page_token": None,
            "page_size": page_size,
        }

        header = get_headers(self._GET_PRODUCTS)
        response = self.session.request(
            "post", url=self._GET_PRODUCTS, json=body, headers=header
        )

        if response.status_code != HTTPStatus.OK:
            raise MicrosoftAdvertisingMerchantCenterException(response.content)

        service_response = response.json()
        yield service_response["data"]["results"]

        while service_response["data"]["next_page_token"]:
            body["page_token"] = service_response["data"]["next_page_token"]
            response = self.session.request(
                "post",
                url=self._GET_PRODUCTS,
                json=body,
                headers=header,
            )

            if response.status_code != HTTPStatus.OK:
                raise MicrosoftAdvertisingMerchantCenterException(response.content)

            service_response = response.json()
            yield service_response["data"]["results"]

    def get_stores(self, secret_id: str, customer_id, customer_account_id) -> List[dict]:
        """
        Gets stores
        :param secret_id: The ID of the secret in secret manager
        :param customer_id: The ID of the customer (parent ID) in Microsoft Advertising
        :param customer_account_id: The ID of the customer account in Microsoft Advertising
        :return: stores
        """
        body = {
            "secret_id": secret_id,
            "customer_id": customer_id,
            "customer_account_id": customer_account_id,
        }
        header = get_headers(self._GET_STORES)
        response = self.session.request(
            "post", url=self._GET_STORES, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MicrosoftAdvertisingMerchantCenterException(response.content)

    def get_store(
            self, secret_id: str, customer_id, customer_account_id, merchant_id: str
    ) -> dict:
        """
        Gets store
        :param secret_id: The ID of the secret in secret manager
        :param customer_id: The ID of the customer (parent ID) in Microsoft Advertising
        :param customer_account_id: The ID of the customer account in Microsoft Advertising
        :param merchant_id: The ID of the store in Microsoft Advertising
        :return: store
        """
        body = {
            "secret_id": secret_id,
            "customer_id": customer_id,
            "customer_account_id": customer_account_id,
            "merchant_id": merchant_id,
        }
        header = get_headers(self._GET_STORE)
        response = self.session.request(
            "post", url=self._GET_STORE, json=body, headers=header
        )

        if response.status_code == HTTPStatus.OK:
            service_response = response.json()
            return service_response["data"]
        else:
            raise MicrosoftAdvertisingMerchantCenterException(response.content)
