# UCUP-2025 - NEAR AI demo

Цей проект створено для демонстрації агента який видає 1 NEAR кожному учаснику UCUP-2025.

Проект має дві компоненти реалізовані на Python:

1. [NEAR AI](https://near.ai) агент (agent), який спілкується з користувачем і дізнається секретний токен відомий тільки учасникам UCUP-2025. З ним можна поспілкуватись [на NEAR AI Hub `frol.near/UCUP-agent`](https://app.near.ai/agents/frol.near/UCUP-agent)
2. [NEAR Protocol](https://dev.near.org) блокчейн контракт (contract), який впенюється щоб не було повторних списань токенів і надсилає 1 NEAR на вказаний акаунт (адресу). Його завантажено [на акаунт `ucup-2025.qbit.near`](https://nearblocks.io/address/ucup-2025.qbit.near).
