# Chart-er documentation

Three sets of pages, for three readers. The first two are also on the site itself under **Docs** (`/docs`), built from these same files, so there is one text to keep right.

## Using Chart-er

For the person with a spreadsheet. No programming is assumed. Also in Turkish: [Türkçe kullanım kılavuzu](guide/tr/getting-started.md).

1. [Getting started](guide/getting-started.md): an account, the example dataset, a first chart
2. [Datasets](guide/datasets.md): which files work, how they are read, what the model may see
3. [Period columns](guide/periods.md): charts in chronological order, and how to correct the order
4. [Models](guide/models.md): connecting a language model, hosted or on your own computer
5. [Charts](guide/charts.md): describing a chart, the choices beside the request, revisions, export
6. [Reproducibility](guide/reproducibility.md): what is recorded, the bundle, replaying a chart
7. [Troubleshooting](guide/troubleshooting.md): the messages you may see and what to do about each

## Running and changing Chart-er

For whoever installs their own copy or works on the code.

1. [Running it with Docker](maintain/docker.md): one compose file, on a laptop or a server; settings, updates, backups, what to check when something is wrong
2. [Development](maintain/development.md): running from source, tests, where things live
3. [Changing things](maintain/changing.md): a new prompt version, a string, an API field, a dependency, the PeriodO snapshot

## Why it is built this way

- [SPEC.md](../SPEC.md): the specification, with a reason for every decision
- [Architecture](architecture.md): the map of processes and request paths
- [Decision records](adr/README.md): one short page per decision
- [openapi.json](openapi.json): the API, generated from the code
