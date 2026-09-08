# ADR 0001: pyarrow for the parsed-rows file

Date: 2026-09-08. Status: accepted.

SPEC §5 stores each dataset's canonical rows as `parsed.parquet`. pandas needs
an engine to read and write Parquet; the two options are pyarrow and
fastparquet. pyarrow is the pandas default, is what pandas 3 uses for its
string dtype, and reads back the exact dtypes we wrote (nullable integers,
booleans, timestamps), which the typed profile depends on.

Cost: about 40 MB in the image. Alternative rejected: storing parsed rows as
CSV, which would lose the types we just inferred and re-open the decimal and
date ambiguities on every read.
