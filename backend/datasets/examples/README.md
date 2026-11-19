# Example dataset

`finds_en.csv` and `finds_tr.csv` are the same table in the two interface
languages: find lots from four trenches of a mound, each with a period, a find
type, a material, a count and a weight.

**The rows are invented.** They come from no excavation and must not be cited
or analysed as evidence. The mound does not exist. The table was written so
that the shape is familiar: periods appear in field order, not in
chronological order; the trenches reach different parts of the sequence;
obsidian thins out after the Chalcolithic; coins, glass and roof tiles begin
with the Hellenistic period; a few lots come from mixed fill.

`POST /api/datasets/example` copies one of the two files into the user's own
datasets, where it is parsed like any upload. The Turkish file uses semicolons
and decimal commas, as a spreadsheet saved in Turkey would.
