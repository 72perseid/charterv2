import { describe, expect, it } from 'vitest';
import { doc, render, rewrite, sections, slug, title } from './docs';

describe('documentation pages', () => {
  it('has a file with a title for every listed page', () => {
    for (const section of sections) {
      for (const page of section.pages) {
        const d = doc(section.id, page, 'en');
        expect(d.title, `${section.id}/${page}`).not.toBe('');
      }
    }
  });

  it('shows a translation where one exists and English where none does', () => {
    for (const section of sections) {
      for (const page of section.pages) {
        const d = doc(section.id, page, 'tr');
        expect(d.title, `${section.id}/${page}`).not.toBe('');
        if (!d.translated) expect(d.text).toBe(doc(section.id, page, 'en').text);
      }
    }
  });

  it('makes the anchors GitHub makes', () => {
    expect(slug('What the model sees')).toBe('what-the-model-sees');
    expect(slug('A model on your own computer')).toBe('a-model-on-your-own-computer');
    expect(slug('Modelin gördüğü')).toBe('modelin-gördüğü');
    expect(slug('The prompt (and its snapshots)')).toBe('the-prompt-and-its-snapshots');
  });

  it('turns links between pages into routes and other repository links into GitHub links', () => {
    expect(rewrite('datasets.md', 'docs/guide')).toBe('/docs/guide/datasets');
    expect(rewrite('periods.md#correcting-it', 'docs/guide')).toBe('/docs/guide/periods#correcting-it');
    expect(rewrite('../maintain/docker.md', 'docs/guide')).toBe('/docs/maintain/docker');
    expect(rewrite('veri-setleri.md', 'docs/guide/tr')).toContain('github.com');
    expect(rewrite('datasets.md', 'docs/guide/tr')).toBe('/docs/guide/datasets');
    expect(rewrite('../../README.md#running-it', 'docs/maintain')).toBe(
      'https://github.com/72perseid/charterv2/blob/main/README.md#running-it'
    );
    expect(rewrite('../adr/README.md', 'docs/maintain')).toContain('/blob/main/docs/adr/README.md');
    expect(rewrite('https://perio.do', 'docs/guide')).toBe('https://perio.do');
    expect(rewrite('#restore', 'docs/maintain')).toBe('#restore');
  });

  it('leaves no link pointing at a Markdown file on the site', () => {
    for (const language of ['en', 'tr'] as const) {
      for (const section of sections) {
        for (const page of section.pages) {
          const d = doc(section.id, page, language);
          const from = `docs/${section.id}` + (language === 'tr' && d.translated ? '/tr' : '');
          const html = render(d.text, from);
          for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
            if (href.startsWith('/')) {
              const [, s, p] = /^\/docs(?:\/([a-z]+)\/([a-z-]+))?/.exec(href) ?? [];
              expect(href.startsWith('/docs'), href).toBe(true);
              if (s) expect(sections.find((x) => x.id === s)?.pages, href).toContain(p);
            }
          }
          expect(html).toContain(`<h1 id="${slug(title(d.text))}">`);
        }
      }
    }
  });

  it('renders tables and code', () => {
    const html = render('| a | b |\n|---|---|\n| `x` | [y](charts.md) |\n', 'docs/guide');
    expect(html).toContain('<div class="table"><table>');
    expect(html).toContain('<code>x</code>');
    expect(html).toContain('href="/docs/guide/charts"');
  });
});
