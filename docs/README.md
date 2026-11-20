# Chart-er documentation

Three sets of pages, for three readers.

## Using Chart-er

For the person with a spreadsheet. No programming is assumed. The same content, shortened, is inside the app under **Help**, in English and Turkish.

1. [Getting started](guide/getting-started.md): an account, the example dataset, a first chart
2. [Datasets](guide/datasets.md): which files work, how they are read, what the model may see
3. [Period columns](guide/periods.md): charts in chronological order, and how to correct the order
4. [Models](guide/models.md): connecting a language model, hosted or on your own computer
5. [Charts](guide/charts.md): describing a chart, the choices beside the request, revisions, export
6. [Reproducibility](guide/reproducibility.md): what is recorded, the bundle, replaying a chart
7. [Troubleshooting](guide/troubleshooting.md): the messages you may see and what to do about each

## Maintaining Chart-er

For whoever runs the server or changes the code. Written so that the maintainer can hand the project over, or come back to it after a year.

1. [Development](maintain/development.md): running from source, tests, where things live
2. [Changing things](maintain/changing.md): a new prompt version, a string, an API field, a dependency, the PeriodO snapshot
3. [Deployment](maintain/deploy.md): the server, a deploy from start to finish, the domain
4. [Operations](maintain/operations.md): backups and restore, logs, accounts, what to check when something is wrong

## Why it is built this way

- [SPEC.md](../SPEC.md): the specification, with a reason for every decision
- [Architecture](architecture.md): the map of processes and request paths
- [Decision records](adr/README.md): one short page per decision
- [openapi.json](openapi.json): the API, generated from the code
