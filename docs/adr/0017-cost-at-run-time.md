# ADR 0017: Cost estimated from user-entered prices, fixed at run time

Date: 2026-09-08. Status: accepted.

Provider prices differ and change, so there is no built-in price table. Settings hold optional USD-per-million prices, prefilled when the provider's model list publishes them (OpenRouter does). Each revision stores the cost computed with the prices in force when it ran, and those prices in its request record, so later edits never rewrite history. Revisions that ran before any price was entered show an estimate at current prices, labelled and unstored.
