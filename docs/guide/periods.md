# Period columns

A chart of finds per period is only readable when the periods run in time. A spreadsheet sorts `Early Bronze Age`, `Hellenistic`, `Late Bronze Age`, `Neolithic` alphabetically, which puts the Hellenistic period before the Late Bronze Age. Chart-er recognises a column of periods, gives it the type **period**, and orders every chart that uses it from oldest to newest.

You do not have to do anything for this. This page explains what Chart-er did, and how to correct it.

## What is recognised

- **Period names** in English, Turkish and German: `Late Bronze Age`, `Geç Tunç Çağı`, `Frühbronzezeit`, `Helenistik`.
- **Abbreviations and phases**: `EB II`, `LH IIIC`, `GTÇ`, `LN`.
- **Dates written in the cell**: `1500 BC`, `MÖ 1500`, `M.S. 200`, `9000 BP`, `1500-1200 BC`, `5th century BC`, `MÖ 5. yüzyıl`, `MÖ 3. binyıl`.
- **Ranges and alternatives**: `LN-FN`, `EM I-III`, `LH IIIB-C`, `Late Neolithic or LN`.

Values that say the date is not known (`Unknown`, `Mixed`, `Karışık`) are put at the end.

A column of plain years such as `-1500` is a number column and sorts correctly already.

## Where the dates come from

Period names are dated from [PeriodO](https://perio.do), a public gazetteer of period definitions taken from the published literature. Chart-er carries its own copy; perio.do is not contacted when you upload.

The same name means different years in different places: the Early Bronze Age of Anatolia is not that of Britain. Chart-er therefore reads the column as a whole, finds the region that most of its values have a definition for, and dates every value for that region.

On the dataset page, press **Order and sources** on a period column to see, for each value:

- the years it was given,
- how it was connected: found as written, after expanding an abbreviation, after translation, as a part of a period, from a date in the label, from your own data, or from your model,
- which published definition was used, with a link to its PeriodO record.

This is the place to check before you present a chart. A value marked **not placed, sorts last** was not understood.

## Correcting it

All of these are on the dataset page, under **Order and sources**. After any of them the dataset is read again, and charts made afterwards use the new order. An existing chart keeps the order it was made with until you revise it.

**Say what a value means.** Next to a value, under **Means**, type the usual name of the period or a date: `ECh` means `Early Chalcolithic`; `Evre 7` means `720-650 BC`. Press **Save meanings**. Use this for site shorthand that no gazetteer knows.

**Use the dates in your own table.** If the dataset has columns with the start and end year of each row, press **Dates from columns** and choose them. Every period is then placed by the earliest start and latest end among its rows. Tick *Years are counted BC* when `1500` in your table means 1500 BC. Your own dates come before PeriodO.

**Type the whole order.** At the bottom of the panel, *Or type the whole order by hand*: one value per line, oldest first. This is the direct way for the phases of a single site (`Phase 1`, `Phase 2a`), which have no dates anywhere.

**Ask your model.** *Ask the model about the unplaced values* sends the distinct values of this one column to the model in your Settings and asks which periods they are. This is the only button in Chart-er, apart from making a chart, that sends anything to the model, and it asks before it does. The answer is looked up in PeriodO like any other name; years suggested by the model alone are marked as an estimate.

**Switch it off, or on.** *Not periods* turns the column back into ordinary text. If Chart-er did not recognise a column that does hold periods, **Treat as periods** forces it.

## When a column is not recognised

Chart-er is cautious: it prefers leaving a column as text to inventing a chronology. A column becomes a period column only when most of its values can be dated and at least one of them beyond doubt. A header that says so (`Period`, `Phase`, `Dönem`) lowers the bar, since real period columns are full of local shorthand. A column with more than 200 different values is never treated as periods.

So if your column is not recognised: name the column `Period` or `Dönem`, or press **Treat as periods** and fill in the meanings of the values that were not placed.

## On the chart

The model is told only that the column is a period column. It is not sent the order. Chart-er puts the order into the chart after the model answers, and lists that under the chart's corrections. Ask for `newest first` in the request to reverse it.
