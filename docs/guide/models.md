# Models

Chart-er does not include a language model. You connect one under **Settings**, with your own account at a provider, or one running on your own computer. This is deliberate: you decide where the description of your data goes, and you pay for exactly what you use.

A chart costs very little. One request is about 1 000 to 3 000 tokens in and a few hundred out, a fraction of a cent on a small hosted model.

## Connecting a hosted model

1. Get an API key from a provider. This is separate from a chat subscription: a ChatGPT or Claude subscription does not include one.
2. In **Settings**, enter the **base URL**: the provider's address up to and including `/v1`.

   | Provider | Base URL |
   |---|---|
   | OpenAI | `https://api.openai.com/v1` |
   | OpenRouter (many models, one key) | `https://openrouter.ai/api/v1` |
   | Anthropic | `https://api.anthropic.com/v1` |

   Any service that speaks the OpenAI chat format works the same way.
3. Paste the **API key**. It is shown once and never again; afterwards the page only says which key is stored by its last characters.
4. Press **Load models** and choose one. If the provider does not publish a list, type the model's name.
5. **Save**, then **Test connection**. The test sends one tiny message and reports what came back.

## Which model

A small, inexpensive model is enough: writing a chart specification is not a hard task. What matters is that it answers with clean JSON and keeps to the column names it was given. The current small models of the large providers do. Reasoning models work too but are slower and cost more for no visible gain here.

## Temperature and prices

**Temperature** is 0 unless you change it. 0 gives the most repeatable result: the same request tends to produce the same chart. Some models refuse a temperature; Chart-er then leaves it out and notes that on the chart.

**Prices** are only used to show what each chart cost. They are filled in when the provider publishes them (OpenRouter does). Otherwise enter the input and output price per million tokens from the provider's price list, or leave them blank and the cost reads as unknown.

## A model on your own computer

With a local model server, nothing leaves your machine at all. [Ollama](https://ollama.com), LM Studio, llama.cpp and vLLM all work.

This needs Chart-er running on the same machine or network, with local endpoints allowed by whoever runs it. A public Chart-er server refuses addresses on private networks. Setting this up is described in the [README](../../README.md#running-with-a-local-model). Once it is:

- Base URL: `http://host.docker.internal:11434/v1` for Ollama when Chart-er runs in Docker.
- API key: leave blank.
- Model: load the list and pick one that fits your computer's memory. On a graphics card with 8 GB, a 7B model such as `qwen2.5:7b` answers in a few seconds.

Two things to know about local models:

- **The first request is slow.** The model has to be loaded into memory. If the connection test says the endpoint did not answer in time, run it again.
- **Check the context length.** Ollama reads only the first 4 096 tokens of a request unless told otherwise, and says nothing when it cuts one. The model then answers about columns it never saw, and Chart-er rejects the answer. For wide tables set `OLLAMA_CONTEXT_LENGTH=16384` where Ollama runs.

Small local models make more mistakes than hosted ones. Chart-er checks every answer, repairs what it safely can, asks once more when the answer is invalid, and tells you why when it gives up. The choices in the chart form (**What to show**, **Only rows where**) help most with small models, since they do not depend on how the model reads your sentence.

## Your key

The key is stored encrypted on the Chart-er server and is used only to call the endpoint you entered. Whoever operates the server holds the encryption key and could in principle decrypt yours. On a server you do not run yourself, use a key with a spending limit, and revoke it at the provider when you no longer need it.
