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
    columns: { name: 'Name', rows: 'Rows', columns: 'Columns', status: 'Status', created: 'Created' }
  },
  status: { pending: 'Pending', running: 'Running', done: 'Done', failed: 'Failed' },
  errors: {
    network: 'Could not reach the server.',
    unknown: 'Something went wrong.'
  }
} as const;
