"""
Median Blockchain Python SDK

This SDK provides Python bindings for the Median blockchain APIs,
using mospy-wallet for proper Protobuf transaction signing.
"""

__version__ = "1.3.0"
__author__ = "Median Team"
__email__ = "contact@median.network"
__license__ = "Apache-2.0"

import json
import time
import requests
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from mospy import Account, Transaction
from mospy.clients import HTTPClient


class MedianSDKError(Exception):
    """SDK exception for Median-specific errors."""
    pass


@dataclass
class Coin:
    """Represents a coin amount with denomination"""
    denom: str
    amount: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "denom": self.denom,
            "amount": self.amount
        }


class MedianSDK:
    """
    Python SDK for interacting with the Median blockchain.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:1317",
        chain_id: str = "median",
        timeout: int = 30
    ):
        self.api_url = api_url.rstrip('/')
        self.chain_id = chain_id
        self.timeout = timeout
        self.session = requests.Session()
        self._client = HTTPClient(api=self.api_url) # Mospy client

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        raise_on_error: bool = True
    ) -> Dict[str, Any]:
        url = f"{self.api_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            if response.status_code >= 400 and raise_on_error:
                try:
                    err = response.json()
                except:
                    err = {"error": response.text}
                response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            if raise_on_error:
                raise
            return {"error": str(e)}

    # ==================== Account Management ====================

    def create_account(
        self,
        creator_address: str,
        new_account_address: str,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "creator": creator_address,
            "new_account_address": new_account_address
        }
        return self._broadcast_tx("/median.median.MsgCreateAccount", msg, creator_address, private_key, wait_confirm)

    def get_account(self, address: str) -> Dict[str, Any]:
        endpoint = f"/cosmos/auth/v1beta1/accounts/{address}"
        return self._make_request("GET", endpoint)

    def get_account_balance(self, address: str) -> List[Coin]:
        endpoint = f"/cosmos/bank/v1beta1/balances/{address}"
        response = self._make_request("GET", endpoint)
        balances = response.get("balances", [])
        return [Coin(denom=b["denom"], amount=b["amount"]) for b in balances]

    # ==================== Coin Management ====================

    def mint_coins(
        self,
        authority_address: str,
        recipient_address: str,
        amount: List[Coin],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "authority": authority_address,
            "recipient": recipient_address,
            "amount": [coin.to_dict() for coin in amount]
        }
        return self._broadcast_tx("/median.median.MsgMintCoins", msg, authority_address, private_key, wait_confirm)

    def burn_coins(
        self,
        authority_address: str,
        amount: List[Coin],
        from_address: str = "",
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "authority": authority_address,
            "from": from_address,
            "amount": [coin.to_dict() for coin in amount]
        }
        return self._broadcast_tx("/median.median.MsgBurnCoins", msg, authority_address, private_key, wait_confirm)

    # ==================== Task Management ====================

    def create_task(
        self,
        creator_address: str,
        task_id: str,
        description: str,
        input_data: str,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "creator": creator_address,
            "task_id": task_id,
            "description": description,
            "input_data": input_data
        }
        return self._broadcast_tx("/median.median.MsgCreateTask", msg, creator_address, private_key, wait_confirm)

    def commit_result(
        self,
        validator_address: str,
        task_id: str,
        result_hash: str,
        nonce: Optional[int] = None,
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        if nonce is None:
             nonce = 0

        msg = {
            "validator": validator_address,
            "task_id": task_id,
            "result_hash": result_hash,
            "nonce": str(nonce)
        }
        return self._broadcast_tx("/median.median.MsgCommitResult", msg, validator_address, private_key, wait_confirm)

    def reveal_result(
        self,
        validator_address: str,
        task_id: str,
        result: Union[int, float, str],
        nonce: Union[int, str],
        private_key: Optional[str] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        msg = {
            "validator": validator_address,
            "task_id": task_id,
            "result": str(result),
            "nonce": str(nonce)
        }
        return self._broadcast_tx("/median.median.MsgRevealResult", msg, validator_address, private_key, wait_confirm)

    # ==================== Query Methods ====================

    def get_task(self, task_id: str) -> Dict[str, Any]:
        endpoint = f"/median/median/task/{task_id}"
        return self._make_request("GET", endpoint)

    def get_consensus_result(self, task_id: str) -> Dict[str, Any]:
        endpoint = f"/median/median/consensus/{task_id}"
        return self._make_request("GET", endpoint)

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        endpoint = "/median/median/tasks"
        response = self._make_request("GET", endpoint, raise_on_error=False)
        return response.get("tasks", [])

    def list_commitments(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Query all commitments, optionally filter by task_id"""
        endpoint = "/median/median/commitment"
        response = self._make_request("GET", endpoint, raise_on_error=False)
        if task_id and "commitment" in response:
            response["commitment"] = [c for c in response.get("commitment", []) if c.get("task_id") == task_id]
        return response

    def list_reveals(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Query all reveals, optionally filter by task_id"""
        endpoint = "/median/median/reveal"
        response = self._make_request("GET", endpoint, raise_on_error=False)
        if task_id and "reveal" in response:
            response["reveal"] = [r for r in response.get("reveal", []) if r.get("task_id") == task_id]
        return response

    def list_consensus_results(self) -> Dict[str, Any]:
        """Query all consensus results"""
        endpoint = "/median/median/consensus_result"
        return self._make_request("GET", endpoint, raise_on_error=False)

    # ==================== Blockchain Info ====================

    def get_node_info(self) -> Dict[str, Any]:
        endpoint = "/cosmos/base/tendermint/v1beta1/node_info"
        return self._make_request("GET", endpoint)

    def get_current_height(self) -> int:
        """Query current block height"""
        endpoint = "/cosmos/base/tendermint/v1beta1/blocks/latest"
        result = self._make_request("GET", endpoint, raise_on_error=False)
        return int(result.get("block", {}).get("header", {}).get("height", "0"))

    def get_supply(self, denom: Optional[str] = None) -> Dict[str, Any]:
        if denom:
            endpoint = f"/cosmos/bank/v1beta1/supply/{denom}"
        else:
            endpoint = "/cosmos/bank/v1beta1/supply"
        return self._make_request("GET", endpoint)

    # ==================== Transaction Methods ====================

    def get_tx(self, tx_hash: str) -> Dict[str, Any]:
        """Query transaction by hash"""
        endpoint = f"/cosmos/tx/v1beta1/txs/{tx_hash}"
        return self._make_request("GET", endpoint, raise_on_error=False)

    def wait_for_tx(self, tx_hash: str, timeout: int = 30, interval: float = 1.0) -> Dict[str, Any]:
        """
        Wait for transaction to be included in a block.
        Returns transaction details when confirmed.

        Args:
            tx_hash: Transaction hash to wait for
            timeout: Maximum time to wait in seconds (default: 30)
            interval: Polling interval in seconds (default: 1.0)

        Returns:
            Transaction details

        Raises:
            MedianSDKError: If timeout is reached
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                tx = self.get_tx(tx_hash)
                tx_response = tx.get("tx_response", {})
                # If transaction is confirmed (has code field), return result
                if "code" in tx_response:
                    # Check for transaction errors
                    code = tx_response.get("code", 0)
                    if code != 0:
                        error_msg = f"Transaction failed (code={code}): {tx_response.get('raw_log', 'Unknown error')}"
                        raise MedianSDKError(error_msg)
                    return tx
            except MedianSDKError:
                raise
            except Exception:
                # Transaction might still be in mempool, continue waiting
                pass
            time.sleep(interval)
        raise MedianSDKError(f"Transaction confirmation timeout: {tx_hash}")

    # ==================== Utility Methods ====================

    def _check_tx_result(self, result: Dict[str, Any]) -> None:
        """
        Check transaction result, raise exception if failed.
        Provides helpful messages for sequence mismatch errors.
        """
        code = result.get("code", 0)
        if code != 0:
            codespace = result.get("codespace", "")
            raw_log = result.get("raw_log", "")
            error_msg = f"Transaction failed (code={code}, codespace={codespace}): {raw_log}"

            # Check for sequence error
            if "sequence" in raw_log.lower() or code == 32:
                error_msg += "\nHint: This may be an account sequence mismatch."
                error_msg += "\nPossible causes:"
                error_msg += "\n1. Previous transaction still in mempool"
                error_msg += "\n2. Account sequence number cache expired"
                error_msg += "\nSuggestion: Wait a few seconds and retry, or query latest account sequence"

            raise MedianSDKError(error_msg)

    def _broadcast_tx(
        self,
        msg_type: str,
        msg_content: Dict[str, Any],
        sender_address: str,
        private_key: Optional[Union[str, bytes]] = None,
        wait_confirm: bool = False
    ) -> Dict[str, Any]:
        """
        Broadcast a signed transaction using mospy.
        Optionally wait for transaction confirmation.
        """
        if not private_key:
            raise ValueError("Private key is required for signing transactions")

        # Handle private key conversion
        try:
            if isinstance(private_key, bytes):
                pk_bytes = private_key
            elif isinstance(private_key, str):
                # Remove 0x prefix if present
                clean_key = private_key.replace("0x", "")
                pk_bytes = bytes.fromhex(clean_key)
            else:
                raise ValueError(f"Unsupported private key type: {type(private_key)}")
        except Exception as e:
             raise ValueError(f"Invalid private key format: {e}")

        # Create account instance
        hrp = sender_address.split('1')[0]

        account = Account(
            private_key=pk_bytes,
            hrp=hrp,
            protobuf="cosmos"
        )

        # Sync account info (sequence, account number) from chain
        acc_info = self.get_account(sender_address)
        base_acc = acc_info.get("account", {})
        # Handle nesting
        if "base_vesting_account" in base_acc:
            base_acc = base_acc["base_vesting_account"]["base_account"]

        account_number = int(base_acc.get("account_number", 0))
        sequence = int(base_acc.get("sequence", 0))

        account.account_number = account_number
        account.next_sequence = sequence

        # Create Transaction
        tx = Transaction(
            account=account,
            chain_id=self.chain_id,
            gas=200000
        )

        # Add Message
        tx.add_msg(msg_type, msg_content)

        # Get transaction bytes
        tx_bytes_base64 = tx.get_tx_bytes_base64()

        payload = {
            "tx_bytes": tx_bytes_base64,
            "mode": "BROADCAST_MODE_SYNC"
        }

        endpoint = "/cosmos/tx/v1beta1/txs"
        result = self._make_request("POST", endpoint, data=payload)

        # Extract tx_hash from response
        tx_response = result.get("tx_response", {})
        tx_hash = tx_response.get("txhash", "")

        # Check for immediate failures
        self._check_tx_result(tx_response)

        # If wait_confirm is True, wait for transaction to be included
        if wait_confirm and tx_hash:
            try:
                confirmed_tx = self.wait_for_tx(tx_hash, timeout=30)
                confirmed_response = confirmed_tx.get("tx_response", {})
                self._check_tx_result(confirmed_response)
                return {"txhash": tx_hash, "confirmed": True, **confirmed_response}
            except MedianSDKError:
                # Return original result if wait fails
                return result

        return result


def create_sdk(
    api_url: str = "http://localhost:1317",
    chain_id: str = "median"
) -> MedianSDK:
    return MedianSDK(api_url=api_url, chain_id=chain_id)
