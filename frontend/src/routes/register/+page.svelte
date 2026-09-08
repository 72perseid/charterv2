<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/api';
  import AuthForm from '$lib/components/AuthForm.svelte';
  import { t } from '$lib/i18n/en';
  import { session } from '$lib/session.svelte';

  async function submit(fields: { email: string; password: string; display_name: string }) {
    session.set(await auth.register(fields.email, fields.password, fields.display_name));
    await goto('/datasets');
  }
</script>

<svelte:head><title>{t.auth.register} · {t.appName}</title></svelte:head>

<AuthForm mode="register" onsubmit={submit} />
