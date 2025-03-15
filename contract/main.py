import near
from near_sdk_py import Contract, view, call, init, ONE_NEAR, Balance

FUNDED_TOKENS_STORAGE_KEY = "funded_tokens"
FUNDING_AMOUNT = Balance(1 * ONE_NEAR)

class GreetingContract(Contract):
    @call
    def fund(self, target_account_id: str, hashed_token: str):
        if self.predecessor_account_id != self.current_account_id:
            raise Exception("UNAUTHORIZED")

        funded_tokens = self.storage.get(FUNDED_TOKENS_STORAGE_KEY, [])
        if hashed_token in funded_tokens:
            raise Exception("Account is already funded")
        funded_tokens.append(hashed_token)
        self.storage[FUNDED_TOKENS_STORAGE_KEY] = funded_tokens

        promise = near.promise_batch_create(target_account_id)
        near.promise_batch_action_transfer(promise, FUNDING_AMOUNT)
        near.promise_return(promise)

    @view
    def get_funded_accounts(self):
        return self.storage.get(FUNDED_TOKENS_STORAGE_KEY, [])
