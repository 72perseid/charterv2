// Every user-visible string lives here (SPEC §8); tr.ts mirrors it. No i18n library.
// One section of the help page. Declared so that every section has the same shape in both languages.
export type HelpSection = { id: string; title: string; paragraphs: string[]; points: string[] };

export const en = {
  appName: 'Chart-er',
  nav: { datasets: 'Datasets', charts: 'Charts', settings: 'Settings', help: 'Help', signOut: 'Sign out' },
  language: { label: 'Language', en: 'English', tr: 'Türkçe' },
  landing: {
    title: 'Chart-er',
    lead: 'A table and a sentence in. A Vega-Lite chart, and the full record of how it was made, out.',
    what: [
      'Upload a CSV or Excel file. Chart-er profiles it: column names, inferred types, basic statistics.',
      'Pick the columns, describe the chart in plain language, and a language model of your choosing writes the Vega-Lite specification.',
      'Every revision is stored with the exact request that produced it, so any chart can be traced back to its inputs.'
    ],
    dataFlow:
      'Only the dataset profile leaves this server, and only to the model endpoint you configure with your own key. Raw rows are never sent unless you switch a dataset to sample mode.',
    signIn: 'Sign in',
    register: 'Create an account',
    source: 'Source code',
    help: 'How it works'
  },
  auth: {
    signIn: 'Sign in',
    register: 'Create an account',
    email: 'Email',
    password: 'Password',
    displayName: 'Name (optional)',
    noAccount: 'No account yet?',
    haveAccount: 'Already have an account?',
    working: 'Working…'
  },
  datasets: {
    title: 'Datasets',
    upload: 'Upload',
    empty: 'No datasets yet. Upload a CSV or Excel file to begin, or try the example.',
    example: 'Try an example',
    exampleTitle:
      'Adds a small table of finds by period to your datasets. The rows are invented. No model or key is needed to look at it.',
    exampleAdding: 'Adding…',
    columns: { name: 'Name', rows: 'Rows', columns: 'Columns', status: 'Status', created: 'Created' },
    uploadForm: {
      title: 'Upload a dataset',
      file: 'File (.csv, .tsv, .txt, or .xlsx, up to 20 MB)',
      name: 'Name',
      submit: 'Upload',
      cancel: 'Cancel',
      uploading: 'Uploading…'
    },
    detail: {
      parsing: 'Parsing the file. This page updates by itself.',
      failed: 'Parsing failed',
      file: 'File',
      download: 'Download original',
      delete: 'Delete dataset',
      confirmDelete: 'Delete for good?',
      newChart: 'New chart',
      profile: 'Columns',
      rows: 'First rows',
      rowsOf: 'of',
      parse: 'How it was read',
      encoding: 'Encoding',
      delimiter: 'Delimiter',
      decimal: 'Decimal mark',
      sheet: 'Sheet',
      headerRow: 'Header row',
      headerRowHint: 'Zero-based row number. Change it if the column names look wrong.',
      apply: 'Apply',
      profileColumns: {
        name: 'Column',
        original: 'Original name',
        type: 'Type',
        nulls: 'Empty',
        distinct: 'Distinct',
        summary: 'Summary'
      },
      period: {
        unplaced: 'not placed, sorts last',
        yours: 'your order',
        edit: 'Order and sources',
        treat: 'Treat as periods',
        dates: 'Dates from columns',
        datesTitle: 'Date the values of',
        datesHint:
          'Pick the columns of this dataset that hold the start and end year of each row. Every value is placed by the earliest start and the latest end among its rows, and these dates come before PeriodO. Values whose rows have no dates are still looked up in PeriodO.',
        datesStart: 'Start year column',
        datesEnd: 'End year column',
        datesNone: '(none)',
        datesBc: 'Years are counted BC (1500 means 1500 BC)',
        datesSave: 'Use these dates',
        datesRemove: 'Remove the link',
        datedBy: 'Dated by',
        varies: 'the dates differ between rows; the widest span is used',
        placedBy: 'How each value was placed',
        datedFor: 'Dated for',
        snapshot: 'PeriodO snapshot',
        bc: 'BC',
        ad: 'AD',
        via: {
          periodo: 'PeriodO',
          abbreviation: 'PeriodO, abbreviation expanded',
          translation: 'PeriodO, translated',
          derived: 'part of a PeriodO period',
          year: 'date in the label',
          model: 'your model',
          user: 'your meaning',
          data: 'dates in this dataset'
        },
        means: 'Means',
        meansPlaceholder: 'e.g. Late Neolithic, or 5300-4500 BC',
        meansHint:
          'Say what a value means: a period name as it is usually written, or a date. It is looked up in PeriodO like any other label and overrules what was found.',
        notRead: 'could not be read',
        notPlaced: 'not placed',
        saveMappings: 'Save meanings',
        typeOrder: 'Or type the whole order by hand',
        modelEstimate: 'estimate, no PeriodO definition',
        ask: 'Ask the model about the unplaced values',
        askConfirm: 'Send this column\'s values to your model?',
        askHint:
          'Sends the distinct values of this one column to the model endpoint in Settings. Nothing is sent unless you press this.',
        askFailed: 'The model could not be asked',
        editorLabel: 'Chronological order of',
        editorHint: 'One value per line, oldest first. Values you leave out sort last.',
        save: 'Save order',
        detect: 'Detect again',
        notPeriod: 'Not periods',
        cancel: 'Close'
      }
    },
    privacy: {
      label: 'What the model sees',
      levels: {
        minimal: 'Minimal',
        statistics: 'Statistics',
        sample: 'Sample'
      },
      describe: {
        minimal: 'Column names, types, row count, empty and distinct counts.',
        statistics: 'Minimal, plus numeric and date ranges and the top categorical values.',
        sample: 'Statistics, plus ten rows chosen with a fixed seed. Raw values leave the server.'
      }
    }
  },
  types: {
    integer: 'integer',
    number: 'number',
    date: 'date',
    boolean: 'boolean',
    string: 'text',
    period: 'period'
  },
  charts: {
    title: 'Charts',
    empty: 'No charts yet. Open a dataset and describe the chart you want.',
    columns: { title: 'Title', dataset: 'Dataset', status: 'Status', revisions: 'Revisions', updated: 'Updated' },
    form: {
      title: 'New chart',
      chartTitle: 'Title (optional)',
      x: 'X axis',
      y: 'Y axis',
      color: 'Color (optional)',
      none: '— none —',
      show: 'What to show',
      shows: {
        auto: 'Let the model decide',
        total: 'Total (sum)',
        average: 'Average',
        count: 'Number of rows',
        distribution: 'Distribution (box plot)',
        points: 'Every row as a point'
      },
      showHint:
        'Whatever you choose here is applied to the chart itself, whatever the model answers. Measurements such as lengths are a distribution or an average, not a total.',
      filterField: 'Only rows where (optional)',
      filterAll: '— all rows —',
      filterValue: 'equals',
      prompt: 'Describe the chart',
      promptHint: 'For example: total finds per area as bars, or weight over time as a line.',
      privacyNote: 'The model will see: {level}.',
      create: 'Create chart',
      creating: 'Creating…'
    },
    page: {
      dataset: 'Dataset',
      revision: 'Revision',
      waiting: 'Waiting for the model.',
      running: 'The model is writing the specification.',
      failed: 'Generation failed',
      tabs: { chart: 'Chart', data: 'Data', spec: 'Specification', request: 'Request and response' },
      revisions: 'Revisions',
      current: 'current',
      makeCurrent: 'Make this the current revision',
      revise: {
        title: 'Revise',
        lead: 'Starts from revision {n}. Change the fields or the request and the model sees the previous specification too.',
        prompt: 'What should change?',
        submit: 'Create revision',
        creating: 'Creating…'
      },
      export: {
        title: 'Export',
        png: 'PNG',
        svg: 'SVG',
        json: 'Spec JSON',
        bundle: 'Reproducibility bundle',
        bundleHint: 'One JSON file with the dataset profile, how it was read, and every revision with its request and response.'
      },
      dataRows: '{shown} of {total} rows',
      corrections: 'Corrections applied to the model\'s answer',
      adjustments: 'Parameters adjusted for this endpoint',
      record: {
        model: 'Model',
        endpoint: 'Endpoint',
        temperature: 'Temperature',
        seed: 'Seed',
        promptVersion: 'Prompt version',
        appVersion: 'App version',
        duration: 'Duration',
        tokens: 'Tokens',
        tokensDetail: '{prompt} in, {completion} out{reasoning}',
        reasoning: ' (of which {n} reasoning)',
        cost: 'Estimated cost',
        costAtCurrent: 'at current prices; this chart ran before prices were entered',
        costUnknown: 'enter prices under Settings',
        attempt: 'Attempt'
      },
      messages: 'Messages sent',
      response: 'Raw response',
      delete: 'Delete chart',
      confirmDelete: 'Delete for good?'
    }
  },
  settings: {
    title: 'Settings',
    model: {
      title: 'Model',
      lead: 'Chart-er sends the dataset profile to an OpenAI-compatible chat endpoint that you choose and pay for. The key is stored encrypted on this server; the operator holds the encryption key.',
      baseUrl: 'Base URL',
      baseUrlHint: 'The address up to and including /v1. For example https://api.openai.com/v1, https://openrouter.ai/api/v1, or https://api.anthropic.com/v1.',
      model: 'Model',
      modelHint: 'Pick from the list the provider returns, or type a name.',
      loadModels: 'Load models',
      loadingModels: 'Loading…',
      modelsLoaded: '{n} models from this endpoint.',
      modelsNeedKey: 'Enter the base URL and an API key to load the model list.',
      modelsNeedUrl: 'Enter the base URL to load the model list.',
      otherModel: 'Other (type a name)',
      apiKey: 'API key',
      apiKeyKeep: 'A key ending in {hint} is stored. Leave blank to keep it.',
      apiKeyNew: 'Pasted once, never shown again.',
      apiKeyOptional: 'Pasted once, never shown again. Leave blank for a local model that checks no key, such as Ollama.',
      temperature: 'Temperature',
      temperatureHint: '0 gives the most repeatable charts.',
      prices: 'Prices (USD per million tokens)',
      inputPrice: 'Input',
      outputPrice: 'Output',
      pricesHint: 'Only used to estimate what each chart cost. Leave blank if you do not know them.',
      pricesFromProvider: 'Filled in from the provider\'s published prices for this model.',
      save: 'Save',
      saved: 'Saved.',
      test: 'Test connection',
      testing: 'Testing…',
      connected: 'Connected',
      notConnected: 'Not connected',
      unsaved: 'Save the configuration, then test it.'
    },
    account: {
      title: 'Account',
      email: 'Email',
      name: 'Name',
      signOut: 'Sign out'
    }
  },
  help: {
    title: 'Help',
    lead: 'How to get from a spreadsheet to a chart, and what Chart-er does on the way.',
    contents: 'On this page',
    sections: [
      {
        id: 'start',
        title: 'In five steps',
        paragraphs: [],
        points: [
          'Datasets: upload a CSV or Excel file, or press "Try an example" to get a small invented table of finds.',
          'Look at the column table. Check that numbers are numbers and that the column names are right.',
          'Settings: enter the address and key of a language model, load the model list, save, and test the connection.',
          'Open the dataset, choose the X and Y columns, say what you want to see, and create the chart.',
          'Revise it with a sentence ("make it horizontal") until it is right, then export PNG or SVG.'
        ]
      },
      {
        id: 'files',
        title: 'Your file',
        paragraphs: [
          'One table per file: column names in the first row, one record per row. CSV, TSV and xlsx work, up to 20 MB, 100 000 rows and 200 columns. Save old .xls files as .xlsx first.',
          'Chart-er works out the encoding, the delimiter, the decimal mark, the sheet and the header row, and shows each under "How it was read". Semicolon files with decimal commas, as Turkish Excel writes them, are read correctly. Dates are read day first.'
        ],
        points: [
          'A number column shown as "text" has cells that are not numbers ("?", "12 cm"). Clean them in the file and upload again.',
          'Column names that are really a title or a data row: change "Header row" on the dataset page. It counts from 0.',
          'Garbled Turkish letters: save the file as UTF-8.'
        ]
      },
      {
        id: 'periods',
        title: 'Period columns',
        paragraphs: [
          'A column of archaeological periods ("Late Bronze Age", "Helenistik", "EB II", "MÖ 5. yüzyıl", "1500 BC") gets the type "period", and every chart that uses it runs from oldest to newest, not alphabetically. Names are dated from PeriodO, a gazetteer of published period definitions, for the region your column points to.',
          'Press "Order and sources" on the column to see the years each value was given and which publication they come from. Check this before you present a chart. There you can also correct it:'
        ],
        points: [
          'Say what a value means: "ECh" means "Early Chalcolithic", "Evre 7" means "720-650 BC".',
          '"Dates from columns": use the start and end year columns of your own table.',
          'Type the whole order by hand, one value per line. Best for the phases of one site.',
          'Ask your model about the values that could not be placed. Only this button sends the column\'s values to the model, and it asks first.',
          '"Not periods" switches it off; "Treat as periods" switches it on for a column that was not recognised.'
        ]
      },
      {
        id: 'model',
        title: 'The model',
        paragraphs: [
          'Chart-er has no language model of its own. You connect one under Settings with your own key and pay your provider for what you use: a fraction of a cent per chart on a small model. A chat subscription does not include an API key; you get one from the provider\'s developer pages.',
          'The base URL is the provider\'s address up to and including /v1, for example https://api.openai.com/v1 or https://openrouter.ai/api/v1. A small, inexpensive model is enough. Leave the temperature at 0 for the most repeatable charts.',
          'Your key is stored encrypted and used only to call the address you entered. Whoever runs this server could decrypt it, so use a key with a spending limit.'
        ],
        points: []
      },
      {
        id: 'chart',
        title: 'Describing a chart',
        paragraphs: [
          'Pick the columns, then say what you want as you would to a colleague, in English or Turkish: "Total finds per period as bars", "Weight by trench, coloured by ware". Name the kind of chart when you care about it. One chart per request: panels and layered charts are not supported.',
          'Two choices can be made in the form so that they do not depend on how the model reads your sentence. Chart-er applies them to the chart itself, whatever the model answers.'
        ],
        points: [
          '"What to show". Total: for amounts that add up, such as counts and weights. Average: a typical value per group. Number of rows: how many records each group has. Distribution: a box plot, for measurements such as lengths. Every row as a point: the raw values.',
          'Do not add up measurements. The total of forty bone lengths means nothing; choose Distribution or Average.',
          '"Only rows where … equals …" limits the chart to one value of one column, for example Region equals Thessaly. A value that no row has is refused at once.'
        ]
      },
      {
        id: 'result',
        title: 'Reading the result',
        paragraphs: [
          'The chart page has four tabs: the chart, the rows behind it, the Vega-Lite specification, and the exact request and response with the model, the tokens and the estimated cost.',
          'Chart-er checks the model\'s answer and lists every change it made under "Corrections applied to the model\'s answer": a period column put in order, a misspelled column name replaced, the aggregate changed to your choice. When a chart surprises you, read that list first. An answer that is not about your columns at all is rejected with a reason, not repaired.'
        ],
        points: []
      },
      {
        id: 'revise',
        title: 'Revisions and export',
        paragraphs: [
          'Every change is a new revision; nothing is overwritten. The model also sees the previous specification, so "use a log scale" changes only that. Click a revision in the list to look at it, start a new one from it, or make it the current one.',
          'Export PNG for slides, SVG for print, or the specification as JSON. The reproducibility bundle is one file with the dataset profile and every revision\'s request, response and specification. It holds neither your rows nor your key, and it is what to keep beside a published figure.'
        ],
        points: []
      },
      {
        id: 'privacy',
        title: 'What leaves this server',
        paragraphs: [
          'The model never receives your file. It receives a profile of the dataset, and only at the address you entered in Settings. You set how much the profile says, per dataset, under "What the model sees":'
        ],
        points: [
          'Minimal: column names, types, the number of rows, empty and distinct counts.',
          'Statistics (the default): also the ranges of number and date columns and the five most frequent values of text columns.',
          'Sample: also ten rows of the table. This is the only level at which raw rows are sent.',
          'Identifier columns contribute no values, and text values longer than 40 characters are left out, at every level.'
        ]
      },
      {
        id: 'problems',
        title: 'When something fails',
        paragraphs: ['A failed revision says why, and its "Request and response" tab shows what the model answered.'],
        points: [
          '"Endpoint returned 401": the key is wrong or belongs to another provider. "404": check the base URL (it usually ends in /v1) and the model name. "429": rate limited, or the account has no credit.',
          '"The endpoint did not answer in time": try again. A model on your own computer is still loading on its first call.',
          '"The answer is not JSON" or "Not valid Vega-Lite": the model made a mistake twice. Try again, simplify the request, choose "What to show" in the form, or use another model.',
          '"The answer uses field names that are not in the profile": the model invented columns. With a local model the request was probably cut off; raise its context length (for Ollama, OLLAMA_CONTEXT_LENGTH=16384).',
          'The chart adds up measurements: choose Distribution or Average. It shows all the data: use "Only rows where". The periods are out of order: correct them on the dataset page, then revise the chart.',
          'Limits: 20 uploads and 60 revisions per hour.'
        ]
      }
    ] as HelpSection[]
  },
  status: { pending: 'Pending', running: 'Running', done: 'Done', failed: 'Failed' },
  errors: {
    network: 'Could not reach the server.',
    unknown: 'Something went wrong.'
  }
};

export type Strings = typeof en;
