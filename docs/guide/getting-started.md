# Getting started

Chart-er turns a table and a sentence into a chart. You upload a CSV or Excel file, choose the columns, say what you want to see, and a language model writes the chart. This page takes you from nothing to a first chart in about five minutes.

You need two things: an account on a Chart-er server, and access to a language model. The model is yours: Chart-er does not come with one and does not pay for one. If you only want to look around first, steps 1 and 2 need no model.

## 1. Create an account

Open the site and choose **Create an account**. Enter an email address and a password of at least eight characters. The name is optional and is only shown in the top bar.

The language switch (English / Türkçe) is in the top bar. Chart-er starts in your browser's language.

## 2. Add a dataset

On **Datasets**, either:

- press **Upload** and choose a `.csv`, `.tsv`, `.txt` or `.xlsx` file of up to 20 MB, or
- press **Try an example**. This adds a small table of finds (lot, trench, period, find type, material, count, weight). The rows are invented; it is there so you can try every step without a file of your own.

The dataset opens with status *Pending*, then *Done* a moment later. The page then shows how the file was read and one line per column: its type, how many cells are empty, how many different values it has, and a summary. If something looks wrong here (a number column read as text, column names that are really a title row), fix it before making charts: see [Datasets](datasets.md).

## 3. Connect a model

Open **Settings**. Enter:

- the **base URL** of an OpenAI-compatible service, for example `https://api.openai.com/v1` or `https://openrouter.ai/api/v1`,
- your **API key** for that service,
- then press **Load models** and pick one.

Press **Save**, then **Test connection**. A green *Connected* means you are ready. [Models](models.md) explains the choices, including a model that runs on your own computer so that nothing leaves it.

## 4. Make a chart

Open the dataset and scroll to **New chart**.

1. Pick the **X axis** and **Y axis** columns. With the example: X = `Period`, Y = `Count`.
2. Optionally pick a **Color** column to split the chart into groups, for example `Material`.
3. Under **What to show**, leave *Let the model decide* or say it yourself. For counts choose *Total*; for measurements such as lengths choose *Distribution* or *Average*.
4. **Describe the chart** in a sentence: `Total finds per period as bars`.
5. Press **Create chart**.

The chart page opens and waits for the model, usually a few seconds. Then the chart appears. With the example, the periods on the x axis run from oldest to newest, not alphabetically: Chart-er recognised the column as periods and ordered it itself.

## 5. Change it

Under **Revise**, write what should change (`make it horizontal`, `colour by material`, `show only Trench A`) and press **Create revision**. Every revision is kept; you can go back to any of them in the list on the side.

Under **Export** you can save the chart as PNG or SVG.

## Where next

- Your own file is not read the way you expected: [Datasets](datasets.md)
- The periods are in the wrong order: [Period columns](periods.md)
- The chart is not what you asked for: [Charts](charts.md)
- A red message: [Troubleshooting](troubleshooting.md)
