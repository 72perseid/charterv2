// Every user-visible string lives here (SPEC §8). tr.ts is added in build step 6.
export const t = {
  appName: 'Chart-er',
  nav: { datasets: 'Datasets', charts: 'Charts', settings: 'Settings', signOut: 'Sign out' },
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
    source: 'Source code'
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
    empty: 'No datasets yet. Upload a CSV or Excel file to begin.',
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
  types: { integer: 'integer', number: 'number', date: 'date', boolean: 'boolean', string: 'text' },
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
      otherModel: 'Other (type a name)',
      apiKey: 'API key',
      apiKeyKeep: 'A key ending in {hint} is stored. Leave blank to keep it.',
      apiKeyNew: 'Pasted once, never shown again.',
      temperature: 'Temperature',
      temperatureHint: '0 gives the most repeatable charts.',
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
  status: { pending: 'Pending', running: 'Running', done: 'Done', failed: 'Failed' },
  errors: {
    network: 'Could not reach the server.',
    unknown: 'Something went wrong.'
  }
} as const;
