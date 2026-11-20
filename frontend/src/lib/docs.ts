// The documentation pages of the site are the Markdown files in docs/guide and
// docs/maintain, read at build time and rendered in the browser (ADR 0020).
// One source: what GitHub shows under docs/ is what the site shows under /docs.
import { Marked } from 'marked';
import type { Language } from '$lib/i18n';

const REPOSITORY = 'https://github.com/72perseid/charterv2/blob/main/';

export type SectionId = 'guide' | 'maintain';

// The order of the pages. A new file has to be listed here to appear.
export const sections: { id: SectionId; pages: string[] }[] = [
  {
    id: 'guide',
    pages: ['getting-started', 'datasets', 'periods', 'models', 'charts', 'reproducibility', 'troubleshooting']
  },
  { id: 'maintain', pages: ['docker', 'development', 'changing'] }
];

const english = import.meta.glob('../../../docs/{guide,maintain}/*.md', {
  query: '?raw',
  import: 'default',
  eager: true
}) as Record<string, string>;
// Translations sit in a tr/ folder beside the English pages. A page without one is shown in English.
const turkish = import.meta.glob('../../../docs/{guide,maintain}/tr/*.md', {
  query: '?raw',
  import: 'default',
  eager: true
}) as Record<string, string>;

export type Doc = { section: SectionId; page: string; title: string; text: string; translated: boolean };

export function exists(section: string, page: string): boolean {
  return sections.some((s) => s.id === section && s.pages.includes(page));
}

export function doc(section: SectionId, page: string, language: Language): Doc {
  const translation = language === 'tr' ? turkish[`../../../docs/${section}/tr/${page}.md`] : undefined;
  const text = translation ?? english[`../../../docs/${section}/${page}.md`] ?? '';
  return { section, page, title: title(text), text, translated: language === 'en' || translation !== undefined };
}

/** The first heading of a page is its title. */
export function title(text: string): string {
  return /^# +(.+)$/m.exec(text)?.[1].trim() ?? '';
}

/** The anchor GitHub gives a heading, so that a link works there and here. */
export function slug(heading: string): string {
  return heading
    .trim()
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\- _]/gu, '')
    .replace(/ /g, '-');
}

/**
 * Where a link written in a Markdown file leads on the site. `from` is the
 * file's directory in the repository, e.g. "docs/guide" or "docs/guide/tr".
 * Links between documentation pages become site routes; links to anything
 * else in the repository (README, SPEC, ADRs) go to GitHub.
 */
export function rewrite(href: string, from: string): string {
  if (/^([a-z][a-z0-9+.-]*:|#|\/)/i.test(href)) return href;
  const [path, anchor] = href.split('#');
  const parts = from.split('/');
  for (const step of path.split('/')) {
    if (step === '..') parts.pop();
    else if (step !== '.' && step !== '') parts.push(step);
  }
  const resolved = parts.join('/');
  const hash = anchor ? '#' + anchor : '';
  const page = /^docs\/(guide|maintain)\/(?:tr\/)?([a-z-]+)\.md$/.exec(resolved);
  if (page && exists(page[1], page[2])) return `/docs/${page[1]}/${page[2]}${hash}`;
  if (resolved === 'docs/README.md') return '/docs' + hash;
  return REPOSITORY + resolved + hash;
}

/** Markdown to HTML. The input is this repository's own files, never user content. */
export function render(text: string, from: string): string {
  const marked = new Marked({
    gfm: true,
    renderer: {
      heading({ tokens, depth, text: raw }) {
        const inner = this.parser.parseInline(tokens);
        return `<h${depth} id="${slug(raw)}">${inner}</h${depth}>\n`;
      },
      link({ href, tokens }) {
        const target = rewrite(href, from);
        const outside = /^https?:/.test(target) ? ' rel="noreferrer"' : '';
        return `<a href="${target.replace(/"/g, '&quot;')}"${outside}>${this.parser.parseInline(tokens)}</a>`;
      },
      // A wide table scrolls inside its own box instead of widening the page.
      table(token) {
        const cell = (c: (typeof token.header)[number], tag: string) =>
          `<${tag}>${this.parser.parseInline(c.tokens)}</${tag}>`;
        const head = token.header.map((c) => cell(c, 'th')).join('');
        const rows = token.rows.map((r) => `<tr>${r.map((c) => cell(c, 'td')).join('')}</tr>`).join('\n');
        return `<div class="table"><table><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div>\n`;
      }
    }
  });
  return marked.parse(text, { async: false });
}

/** The directory a page's Markdown lives in, for resolving its links. */
export function directory(d: Doc, language: Language): string {
  return `docs/${d.section}` + (language === 'tr' && d.translated ? '/tr' : '');
}
