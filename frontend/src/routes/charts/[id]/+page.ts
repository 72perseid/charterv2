import { charts, datasets, revisions, type Revision, type Rows } from '$lib/api';
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, url }) => {
  const id = Number(params.id);
  if (!Number.isInteger(id)) error(404);
  const chart = await charts.get(id);

  // Show the requested revision, else the current one, else the newest.
  const wanted = Number(url.searchParams.get('revision'));
  const summary =
    chart.revisions.find((r) => r.id === wanted) ??
    chart.revisions.find((r) => r.id === chart.current_revision_id) ??
    chart.revisions[chart.revisions.length - 1];

  const [revision, dataset] = await Promise.all([
    summary ? revisions.get(summary.id) : Promise.resolve(null as Revision | null),
    datasets.get(chart.dataset_id)
  ]);
  const rows: Rows | null =
    revision?.status === 'done' ? await datasets.rows(chart.dataset_id, 100000) : null;
  return { chart, revision, dataset, rows };
};
