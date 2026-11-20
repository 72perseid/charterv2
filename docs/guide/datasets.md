# Datasets

A dataset is one table: the first row holds the column names, every other row is one record.

## Files that work

| | |
|---|---|
| Formats | `.csv`, `.tsv`, `.txt`, `.xlsx` |
| Not supported | `.xls` (old Excel). Open it in Excel or LibreOffice and save as `.xlsx`. |
| Size | up to 20 MB, 100 000 rows, 200 columns |
| Uploads | 20 per hour per account |

Your original file is kept unchanged and can be downloaded again from the dataset page (**Download original**).

## How a file is read

Chart-er works these out by itself and shows each one under **How it was read**:

- **Encoding.** UTF-8 is tried first, then Windows-1254 (the usual encoding of Turkish Excel exports), then Latin-1. If `ş`, `ğ` or `ı` look wrong in the table, save the file as UTF-8 and upload again.
- **Delimiter.** Comma, semicolon, tab or `|`, whichever fits the first lines.
- **Decimal mark.** A semicolon-separated file is assumed to use a decimal comma (`12,5`), as Turkish and German Excel write it. Otherwise Chart-er checks which mark makes the number columns readable. Grouped numbers such as `1.250,50` are understood.
- **Dates** are read day first: `03.04.2021` is 3 April.
- **Excel sheet.** The first sheet that is not empty. Choose another under **Sheet**.
- **Header row.** For Excel, the first row in which at least half the cells are filled, so a title above the table is skipped. If the column names are still wrong, set **Header row** yourself. It counts from zero: the first row of the sheet is 0.

Cells are trimmed, so `LN` and `LN ` are the same value.

## Column types

Every column gets one type. The type decides how the column can be charted.

| Type | Means | On a chart |
|---|---|---|
| integer, number | whole or decimal numbers | an axis with a scale; can be summed, averaged |
| date | calendar dates | a time axis |
| text | names, categories, codes | one bar, box or colour per value |
| boolean | yes / no | two groups |
| period | archaeological periods | groups in chronological order; see [Period columns](periods.md) |

A number column that came out as *text* almost always contains something that is not a number in a few cells: `?`, `ca. 12`, `12 cm`, `-`. Clean those cells in the file and upload again. Empty cells are fine.

## What the model sees

The model never receives your file. It receives a **profile**: a description of the columns. How much the profile says is set per dataset under **What the model sees**:

| Level | Sent to the model |
|---|---|
| **Minimal** | Column names, types, the number of rows, and how many cells are empty or distinct in each column. |
| **Statistics** (default) | Minimal, plus the smallest and largest value of number and date columns, their mean and median, and the five most frequent values of text columns. |
| **Sample** | Statistics, plus ten rows of the table. This is the only level at which raw rows leave the server. |

Two things are held back at every level: a text column in which every value is different (an identifier such as a find number) contributes no values, and text values longer than 40 characters (citations, notes, links) are left out.

The level in force is shown next to the request box each time you make a chart. *Statistics* is enough for almost every chart. *Minimal* is for data whose category names are themselves sensitive, such as unpublished site names. With *Minimal* the model cannot know which values a column holds, so use the **Only rows where** control in the form, not the sentence, to limit a chart to one value.

The chart itself is drawn in your browser from the rows held on the Chart-er server. The model writes the recipe and never sees the result.

## Deleting

**Delete dataset** removes the dataset, its file on the server, and every chart made from it. This cannot be undone.
