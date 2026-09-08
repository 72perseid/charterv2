import { datasets, type Rows } from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  const id = Number(params.id);
  if (!Number.isInteger(id)) error(404);
  const dataset = await datasets.get(id);
  const rows: Rows | null = dataset.status === 'done' ? await datasets.rows(id, 100) : null;
  return { dataset, rows };
};
