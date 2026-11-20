# Charts

A chart is made from one dataset, three column choices, two optional settings, and a sentence. The model turns those into a chart specification; Chart-er checks the specification and draws it.

## The form

Open a dataset and go to **New chart**.

| Field | What it does |
|---|---|
| **Title** | Optional. The name in your list of charts. |
| **X axis** | The column along the bottom: usually the groups (period, trench, species) or a date. |
| **Y axis** | The column that is measured or counted: a number. |
| **Color** | Optional. Splits each group by a second column, for example material within period. |
| **What to show** | How the Y values of one group become one mark. See below. |
| **Only rows where … equals …** | Optional. Limits the chart to the rows with one value in one column. |
| **Describe the chart** | Your request, up to 1 000 characters. |

The line under the request box says what the model will see of this dataset ([Datasets](datasets.md#what-the-model-sees)).

## What to show

This is the choice that most often goes wrong when left to a model, so you can make it yourself.

| Choice | The chart shows | Use it for |
|---|---|---|
| **Let the model decide** | whatever the model reads from your sentence | when you are not sure, or the sentence says it clearly |
| **Total (sum)** | the Y values of each group added up | amounts that add up: counts, weights, areas |
| **Average** | the mean of each group | a typical value per group |
| **Number of rows** | how many rows each group has | "how many finds per period", when each row is one find |
| **Distribution (box plot)** | median, quartiles and range of each group | measurements: lengths, widths, indices |
| **Every row as a point** | one point per row | small datasets, or to see the raw values |

**Do not add up measurements.** The total of forty bone lengths is a number that means nothing; it only shows which period has more bones. For a measurement choose *Distribution* or *Average*.

Whatever you choose here is applied to the chart by Chart-er itself, after the model has answered. If the model wrote something else, your choice wins and the difference is listed under the chart.

## Only rows where

Choose a column and type or pick a value: `Region` equals `Thessaly`. The chart then uses only those rows. For a period column every period is offered; for a text column, its most frequent values, but any value that occurs in the column can be typed. A value that no row has is refused straight away, so a typing mistake does not produce an empty chart.

This is one condition on one column. For anything more (two regions, a range of years) say it in the request; the model can write such filters, but whether it does depends on the model.

## Writing the request

Say what you want to see as you would to a colleague. Turkish works as well as English.

- `Total finds per period as bars`
- `Weight of pottery by trench, coloured by ware`
- `Dönemlere göre astragalus uzunluğu dağılımı`
- `Finds over time as a line, one line per material`
- `Horizontal bars, largest first`

What helps:

- **Name the kind of chart** when you care: bars, line, points, box plot.
- **Use the column names** as they appear in the dataset.
- **One chart per request.** Chart-er makes single charts; side-by-side panels and overlaid layers are not supported.
- **Leave out what the form already says.** If you chose *Distribution* and a filter, the sentence does not need to repeat them.

## The chart page

After **Create chart** the page waits (*Waiting for the model*, then *The model is writing the specification*) and then shows four tabs.

- **Chart**: the drawing.
- **Data**: the rows behind it.
- **Specification**: the Vega-Lite JSON, the complete recipe of the chart.
- **Request and response**: exactly what was sent to the model and exactly what it answered, with the model, the time taken, the tokens used and the estimated cost.

### Corrections

Under the chart you may see **Corrections applied to the model's answer**. Chart-er does not pass the model's answer through unchecked. It lists every change it made, for example:

- a period column was put in chronological order,
- a column name the model misspelled was replaced with the one you chose,
- the aggregate or the mark was changed to match **What to show**,
- your row filter was put in, or a filter that compared nothing was removed.

Read this list when a chart surprises you. It tells you whether the surprise came from the model or from a correction.

An answer that is not about your dataset at all (both axes use columns that do not exist) is rejected, not repaired. The revision then shows as *Failed* with the reason.

## Revisions

A chart is a series of revisions. Under **Revise**, change the columns, the choices or the sentence and press **Create revision**. The model also receives the previous specification, so `make the bars horizontal` or `use a log scale` changes only that.

- The list on the side shows every revision with its request and status. Click one to look at it.
- **Make this the current revision** sets which one the chart shows by default.
- A revision starts from the one you are looking at, so you can go back to revision 2 and branch from there.
- Nothing is overwritten. A failed revision stays in the list with its reason.

You can make 60 revisions per hour.

## Export

- **PNG** for slides and documents, **SVG** for print and for editing in a drawing program.
- **Spec JSON**: the Vega-Lite specification, to open in the [Vega editor](https://vega.github.io/editor/) or use in your own page. It contains no data; supply the rows under the name `main`.
- **Reproducibility bundle**: the full record of the chart. See [Reproducibility](reproducibility.md).

## What Chart-er does not do

- Several charts in one (panels, layers, a line over bars).
- Statistics beyond sum, mean, median and count: no tests, no regression lines.
- Changing your data. To recode or merge categories, edit the file and upload it again.
