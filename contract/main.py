import near
from near_sdk_py import Contract, view, call, init, ONE_NEAR, Balance

FUNDED_ACCOUNTS_STORAGE_KEY = "funded_accounts"
FUNDING_AMOUNT = Balance(1 * ONE_NEAR)

class GreetingContract(Contract):
    @call
    def fund(self, target_account_id):
        if self.predecessor_account_id != self.current_account_id:
            raise Exception("UNAUTHORIZED")

        funded_accounts = self.storage.get(FUNDED_ACCOUNTS_STORAGE_KEY, [])
        if target_account_id in funded_accounts:
            raise Exception("Account is already funded")
        funded_accounts.append(target_account_id)
        self.storage[FUNDED_ACCOUNTS_STORAGE_KEY] = funded_accounts

        promise = near.promise_batch_create(target_account_id)
        near.promise_batch_action_transfer(promise, FUNDING_AMOUNT)
        near.promise_return(promise)

    @view
    def get_funded_accounts(self):
        return self.storage.get(FUNDED_ACCOUNTS_STORAGE_KEY, [])
