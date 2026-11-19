# ADR 0019: What to show and which rows are chosen in the form, and enforced by the server

Date: 2026-11-20. Status: accepted.

A dataset of pig bone measurements by period showed three faults at once, with a 7B model on Ollama.

1. **The request did not fit and nobody noticed.** The profile made the request about 4 600 tokens; Ollama's default context is 4 096, and it read 2 050 of them without an error. The model answered with a generic chart over fields called `period` and `count`.
2. **Chart-er repaired that answer.** Unknown fields were replaced with the user's picks, so a chart of the *sum* of astragalus lengths came out marked `done`.
3. **The prompt had one idea of a category axis: sum it.** With the whole request read, "distribution" still gave bars.

**Decisions.**

- An answer whose x and y are both unknown fields, or that names no field of the dataset, is rejected. One unknown field is still repaired and recorded. A repair is for a slip; an answer about another dataset is a failure and has to look like one.
- The profile sent to the model drops what no chart uses: long text values and duplicate names, and is written one column per line. The same request is now about 2 900 tokens. Period sort lists are left out of the parent spec on a revision.
- Prompt `p2026-11-b`: amounts are summed, measurements and distributions are box plots, and a filter on a profile field is allowed when the chart is limited to part of the data.
- Two choices sit beside the request text: *what to show* (total, average, number of rows, distribution, points; default: let the model decide) and one *only rows where column = value*. The model is told, and afterwards the server makes the specification agree: it sets or removes the aggregate, sets the mark, and writes the filter. Each change is recorded as a correction. The filter value is checked against the data when the chart is requested.

**Why enforce and not only ask.** Deciding between a sum and a distribution from one sentence is the step small models fail at, and it is also the step where a wrong answer still draws a plausible chart. A choice the user made explicitly is not something to leave to that. It is not the silent repair of fault 2: the source is the user's own selection, not a guess, and it is written into the record.

**What this does not do.** The filter is one equality. Ranges, several conditions and "top ten" stay with the request text and the model. `auto` still depends on the model. The server cannot see how much of a request a model server actually read; the README says how to set Ollama's context, and the prompt token count on each revision shows it.
