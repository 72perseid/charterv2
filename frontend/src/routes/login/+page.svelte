<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/state';
  import { auth } from '$lib/api';
  import AuthForm from '$lib/components/AuthForm.svelte';
  import { t } from '$lib/i18n/en';
  import { session } from '$lib/session.svelte';

  async function submit({ email, password }: { email: string; password: string }) {
    session.set(await auth.login(email, password));
    const next = page.url.searchParams.get('next');
    await goto(next && next.startsWith('/') ? next : '/datasets');
  }
</script>

<svelte:head><title>{t.auth.signIn} · {t.appName}</title></svelte:head>

<AuthForm mode="login" onsubmit={submit} />
