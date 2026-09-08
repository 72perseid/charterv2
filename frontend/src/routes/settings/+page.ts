import { modelConfig } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  return { config: await modelConfig.get() };
};
