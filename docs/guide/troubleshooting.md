# Troubleshooting

Chart-er says why something failed. Find the message here; the wording on screen may continue with details.

## Uploading

| Message | What to do |
|---|---|
| *Old Excel (.xls) files are not supported.* | Open the file and save it as `.xlsx`. |
| *Unsupported file type.* | Export the table as `.csv` or `.xlsx`. |
| *The file has … rows; the limit is 100,000.* / *… columns; the limit is 200.* | Cut the table down to what the chart needs. |
| *The file is empty.* / *The file has a header but no data rows.* | The sheet or file holds no table. For Excel, check that the right sheet was read. |
| *Every sheet in the workbook is empty.* | Same; the workbook may hold only charts or pivot tables. |
| *Header row … is past the end of the sheet.* | The header row counts from 0. Enter a smaller number. |

**The table looks wrong after upload**

- *Everything is in one column.* The delimiter was not found. Save the file as `.xlsx`, or as CSV with commas or semicolons.
- *Turkish letters are garbled.* Save the file as UTF-8 and upload again.
- *A number column is "text".* Some cells are not numbers (`?`, `12 cm`, `ca. 5`). Clean them in the file.
- *Numbers are a thousand times too large or small.* The decimal mark was read the wrong way; the page shows which one was used. Write the numbers without thousands separators and upload again.
- *The column names are the first data row, or a title.* Set **Header row** on the dataset page.
- *Day and month are swapped.* Dates are read day first. Write them as `2021-04-03` in the file to be unambiguous.

## Connecting a model

| Message | What to do |
|---|---|
| *No model is configured. Add one under Settings.* | Fill in Settings first. |
| *Endpoint returned 401: check your API key.* | The key is wrong, revoked, or belongs to a different provider than the base URL. |
| *Endpoint returned 404: check the base URL and the model name.* | The base URL must end in `/v1` (for most providers), and the model name must be exactly as the provider writes it. |
| *Endpoint returned 429: rate limited or out of credit.* | Wait, or add credit at the provider. A new account often has none. |
| *The endpoint did not answer in time.* | Try again. A local model is loading on its first call. |
| *Could not resolve host …* / *Could not connect to the endpoint* | A typing mistake in the base URL, or the service is down. |
| *Base URL must use https://* | Plain `http://` is only allowed for local endpoints, on servers that permit them. |
| *Host … resolves to a private or local address, which this server does not call.* | This server does not allow local models. Run Chart-er yourself to use one ([Models](models.md#a-model-on-your-own-computer)). |
| *This endpoint does not list its models. Type the model name.* | Not an error. Type the name. |

## Making a chart

When a revision shows **Failed**, the reason is under it, and the **Request and response** tab shows what the model answered.

| Message | What it means and what to do |
|---|---|
| *The answer is not JSON.* / *The answer is not valid JSON* | The model wrote prose or broken JSON, twice. Try again; if it keeps happening, use a different model. |
| *The answer uses field names that are not in the profile* | The model invented column names. With a local model this is nearly always a cut-off request: see the context length under [Models](models.md#a-model-on-your-own-computer). Otherwise try again or use a stronger model. |
| *Not valid Vega-Lite v6 at …* | The model wrote a specification with a mistake at the place named. Rephrase the request more simply, or choose **What to show** in the form so less is left to the model. |
| *The model hit its output limit before writing an answer.* | A reasoning model used its whole allowance thinking. Use a model without reasoning, or a lower reasoning setting at the provider. |
| *No row has … = …* | The filter value does not occur in that column. Pick it from the list, and check spelling and capitals. |
| *… holds numbers; … is not one.* | The filter column is numeric; enter a number. |
| *… is a date column; filter on text or numbers.* | Filtering on dates is not available in the form. |

**The chart is drawn but is not what you wanted**

- *It adds up measurements.* Choose *Distribution* or *Average* under **What to show**.
- *It shows all the data, not the part you named.* Use **Only rows where**.
- *The periods are in the wrong order.* The order comes from the dataset, not the model: see [Period columns](periods.md#correcting-it). Revise the chart afterwards to pick up the new order.
- *The chart is empty.* Look at the **Data** tab and the **Specification** tab for a filter that matches nothing, then revise with `remove the filter`.
- *Too many bars or colours to read.* The column has too many different values. Filter to a subset, or chart a coarser column.
- *It changed something you did not ask for.* Read **Corrections** under the chart, then say what to keep in the next revision.

## Limits

*Upload limit reached. Try again in an hour.* / *Revision limit reached. Try again in an hour.* The limits are 20 uploads (the example counts as one) and 60 revisions per hour per account.

## Still stuck

Download the **reproducibility bundle** of the chart (it holds the request, the answer and the reason; not your rows and not your key) and send it to whoever runs your Chart-er server, or attach it to an issue at <https://github.com/72perseid/charterv2/issues>. Check first that the profile in it holds nothing you cannot share.
