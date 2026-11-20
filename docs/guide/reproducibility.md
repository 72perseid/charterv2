# Reproducibility

A chart in a paper should be traceable to what produced it. With a language model in the middle that is not automatic: the same sentence can give a different chart tomorrow. Chart-er's answer is to record everything, so that the question "how was this figure made?" always has an exact answer.

## What is recorded

For every revision, whether it succeeded or failed:

- the messages sent to the model, word for word,
- the model's raw answer, before anything was done to it,
- the specification after checking, and the list of corrections,
- the model's name, the host of the endpoint, the temperature and the seed,
- the version of Chart-er's prompt and the version of Chart-er itself,
- tokens used, estimated cost, and how long it took.

All of it is on the chart page under **Request and response**.

## The bundle

**Export → Reproducibility bundle** downloads one JSON file with the chart, the dataset's profile, how the file was read, and every revision with the record above.

The bundle does not contain your rows and does not contain your API key. It does contain the dataset's whole profile, whatever level the model was allowed to see: column names, ranges, and the most frequent values of text columns. Check that before you publish it.

For a publication, the bundle together with the dataset is the complete provenance of a figure. A sentence for the methods section:

> The figure was generated with Chart-er (version `a3baa83`, prompt `p2026-11-b`) using the model `<model>` at temperature 0; the request, the model's response and the resulting Vega-Lite specification are in the supplementary file `charter-chart-12.json`.

The versions and the model name are in the bundle and on the chart page.

## Replaying a chart

Anyone with a bundle and a key can send the recorded request again and compare the answer. It needs a copy of Chart-er but no account and no database:

```sh
docker compose -f deploy/compose.yml run --rm -T api \
  python manage.py replay /tmp/charter-chart-12.json --revision 2 \
  --base-url https://api.openai.com/v1 --model gpt-4.1-mini --api-key sk-...
```

`--revision` defaults to the last one, `--model` to the model in the bundle, and `--out` writes the replayed specification to a file. The command sends the recorded messages with the recorded parameters, checks the answer the same way the server does, and reports whether the specification is identical or where it differs.

## What this does and does not promise

No provider guarantees the same answer twice, even at temperature 0 with a fixed seed, and models are withdrawn. A replay next year may differ or be impossible.

What is guaranteed is the record: the chart you published came from this specification, which is in the bundle and draws the same chart for ever, and the specification came from this request to this model. The specification is the reproducible object; the model call is its documented origin.
