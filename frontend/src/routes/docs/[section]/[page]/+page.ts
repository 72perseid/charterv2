import { error } from '@sveltejs/kit';
import { exists, type SectionId } from '$lib/docs';
import type { PageLoad } from './$types';

export const load: PageLoad = ({ params }) => {
  if (!exists(params.section, params.page)) error(404, 'Not found');
  return { section: params.section as SectionId, page: params.page };
};
