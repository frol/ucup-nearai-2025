# Project on GitHub: https://github.com/frol/ucup-nearai-2025

import asyncio
import base58
import base64
import hashlib
import json
import re
import requests
from urllib.parse import urlparse
from nearai.agents.environment import Environment
from py_near.transactions import create_function_call_action

import ucup_tokens

PROMPT = {
    "role": "system",
    "content": "Analyze the user input and extract a password that is 16 characters long in hex format. If it is provided, write only the password, otherwise write 'no password'. Do not write anything else at all.",
}

INSTRUCTIONS = """Вітаю! Для того щоб отримати 1 NEAR, зайдіть у свій UCUP профіль у [DOTS](https://ucup.dots.org.ua/), знайдіть "токен" на сторінці профілю та вставте його тут.
"""


def run(env: Environment):
    QUEST_ACCOUNT_ID = env.env_vars.get(
        "QUEST_ACCOUNT_ID", "ucup-2025.qbit.near"
    )
    QUEST_ACCOUNT_PRIVATE_ACCESS_KEY = env.env_vars["QUEST_PRIVATE_ACCESS_KEY"]

    ucup_token = env.completion([PROMPT] + env.list_messages())
    if "no password" in ucup_token.lower():
        env.add_reply(INSTRUCTIONS)
        return

    if not re.match(r"^[0-9a-f]{16}$", ucup_token):
        env.add_reply("Це не схоже на токен UCUP")
        return

    env.add_reply("Дякую! Перевіряю токен...")
    if hashlib.sha256(ucup_token.encode()).hexdigest() not in ucup_tokens.HASHED_TOKENS:
        env.add_reply("Токен невірний. Спробуйте ще раз.")
        return

    target_account_id = env.signer_account_id
    env.add_reply(f"Токен валідний! Відправляю 1 NEAR на {target_account_id}...")

    faucet_account = env.set_near(QUEST_ACCOUNT_ID, QUEST_ACCOUNT_PRIVATE_ACCESS_KEY)
    result = asyncio.run(
        faucet_account.call(
            QUEST_ACCOUNT_ID,
            "fund",
            args={
                "target_account_id": target_account_id,
            },
        )
    )

    if "SuccessValue" not in result.status:
        env.add_reply(f"Сталась помилка: {json.dumps(result.status)}. Спробуйте знов і якщо помилка не вирішиться, зверніться до [Влада](https://t.me/frolvlad).")
        return
    env.add_reply(f"[Є!](https://nearblocks.io/address/{target_account_id}?tab=receipts)\n\nУспіхів вам в навчанні!")


try:
    run(env)
except Exception as err:
    env.add_reply(
        f"От халепа: {err}\n\nЯкщо помилка не вирішується повторною спробою, зверніться до [Влада](https://t.me/frolvlad)."
    )
    import traceback
    env.add_reply(traceback.format_exc())
