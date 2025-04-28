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

PROMPT = {
    "role": "system",
    "content": "Analyze the user input and extract a list of certificate IDs, which are strings that start with L0, L1, L2, L3, D1, D2, D3, or T followed by a hyphen and three groups of numbers separated by hyphens. If they are provided, write only the certificate IDs separated by newlines, otherwise write 'no certificate IDs found'. Do not write anything else at all.",
}

INSTRUCTIONS = """Вітаю!

Для того щоб отримати вашу нагороду за успішне проходження сертификації Q-bit та перемогу UCUP-2025, зайдіть у свій UCUP профіль у [DOTS](https://ucup.dots.org.ua/), знайдіть отриману грамоту та введіть її номер (Certificate ID).

Доречі, ви можете отримати винагороду за кожну грамоту!
"""

def get_reward(cert):
    if cert.startswith("L0"):
        return 1
    elif cert.startswith("L1"):
        return 2
    elif cert.startswith("L2"):
        return 3
    elif cert.startswith("L3"):
        return 5
    elif cert.startswith("D1"):
        return 5
    elif cert.startswith("D2"):
        return 3
    elif cert.startswith("D3"):
        return 1
    elif cert.startswith("T"):
        return 100
    raise ValueError("Invalid certificate")

def run(env: Environment):
    QUEST_ACCOUNT_ID = env.env_vars.get(
        "QUEST_ACCOUNT_ID", "ucup-2025.qbit.near"
    )
    QUEST_ACCOUNT_PRIVATE_ACCESS_KEY = env.env_vars["QUEST_PRIVATE_ACCESS_KEY"]

    ucup_certificates = env.completion([PROMPT] + env.list_messages())
    ucup_certificates = [cert for cert in ucup_certificates.split() if re.match(r"^(L0|L1|L2|L3|D1|D2|D3|T)(-[0-9]{4,5}){3}$", cert)]
    if not ucup_certificates:
        env.add_reply(INSTRUCTIONS)
        return

    for cert in ucup_certificates:
        env.add_reply(f"Дякую! Перевіряю сертифікат {cert}...")
        if not requests.head(f"https://ucup.dots.org.ua/cat/cert/{cert}.pdf"):
            env.add_reply(f"Сертифікат {cert} не знайдено. Спробуйте ще раз.")
            continue

        reward = get_reward(cert)
        target_account_id = env.signer_account_id
        env.add_reply(f"Сертифікат {cert} знайдено! Відправляю {reward} NEAR на {target_account_id}...")

        hashed_cert = hashlib.sha256(cert.encode()).hexdigest()
        faucet_account = env.set_near(QUEST_ACCOUNT_ID, QUEST_ACCOUNT_PRIVATE_ACCESS_KEY)
        result = asyncio.run(
            faucet_account.call(
                QUEST_ACCOUNT_ID,
                "fund",
                args={
                    "target_account_id": target_account_id,
                    "hashed_token": hashed_cert,
                    "funding_amount": str(reward * 10**24),
                },
            )
        )

        if "SuccessValue" not in result.status:
            json_status = json.dumps(result.status)
            if "Account is already funded" in json_status:
                env.add_reply("NEAR винагороду за цей сертифікат вже отримано. Якщо ви вважаєте, що це помилка, зверніться [в підтримку](https://t.me/frolvlad).")
            else:
                env.add_reply(f"Сталась помилка: {json_status}. Спробуйте знов і якщо помилка не вирішиться, зверніться [в підтримку](https://t.me/frolvlad).")
        else:
            env.add_reply(f"[Вітаю з успішною участю в Кубку Університетів 2025!](https://nearblocks.io/address/{target_account_id}?tab=receipts)\n\nУспіхів вам в навчанні!")

    env.add_reply("Дізнавайтесь більше про [NEAR блокчейн](https://dev.near.org) та [NEAR AI](https://t.me/nearaialpha), та підписуйтесь на [щотижневі новини](https://dev.near.org/newsletter)")

try:
    run(env)
except Exception as err:
    env.add_reply(
        f"От халепа: {err}\n\nЯкщо помилка не вирішується повторною спробою, зверніться до [Влада](https://t.me/frolvlad)."
    )
    import traceback
    env.add_reply(traceback.format_exc())
