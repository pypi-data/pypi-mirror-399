from typing import Dict, List, Optional, Union

from uzcloud_billing.choices import TransactionTypeChoice
from uzcloud_billing.signals import payment_completed_signal
from uzcloud_billing.utils import uzcloud_service


class BillingControllerMixin:
    def update_balance(self, balance: float):
        self.balance = balance
        self.save()

    def sync_balance(self):
        self.balance = uzcloud_service.get_balance(account_number=self.account_number)
        self.save()

    def make_charge(
        self,
        amount: float,
        reason: str,
        data: dict = {},
        retry_count: int = 3,
        sleep_time: float = 1.5,
    ):
        # sourcery skip: default-mutable-arg
        """
        Example Response :
        {
            "accountNumber": "AA-000657",
            "chargeAmount": 100,
            "balance": 159900,
            "invoiceId": "df71e40b-82cb-4015-92cd-1ea1eb4235fb",
            "createdAt": "2025-09-02T13:03:44.9902105+00:00"
        }
        """
        response: dict = uzcloud_service.make_invoice(
            account_number=self.account_number,
            amount=amount,
            reason=reason,
            retry_count=retry_count,
            sleep_time=sleep_time,
        )
        self.update_balance(balance=response["balance"])
        data.update(response)
        payment_completed_signal.send(sender=None, data=data)
        return response

    def refund_charge(self, amount: float, invoice_id: str, reason: str):
        return uzcloud_service.refund_invoice(
            account_number=self.account_number,
            invoice_id=invoice_id,
            amount=amount,
            reason=reason,
        )

    def get_payment_links(self, amount: Union[int, float]) -> Dict:
        return uzcloud_service.generate_payment_links(
            account_number=self.account_number, amount=amount
        )

    def get_payment_providers(self) -> List:
        return uzcloud_service.payment_providers()

    def get_transaction_history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        transaction_type: Optional[TransactionTypeChoice] = None,
    ) -> List[dict]:
        return uzcloud_service.transaction_history(
            account_number=self.account_number,
            start=start,
            end=end,
            transaction_type=transaction_type,
        )
