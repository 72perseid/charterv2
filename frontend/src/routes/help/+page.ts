// The short help page became the documentation (2026-11-20). Old links still land somewhere.
import { redirect } from '@sveltejs/kit';

export function load() {
  redirect(308, '/docs');
}
