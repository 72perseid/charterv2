// Who is signed in, shared by every page. Svelte 5 runes, no store library.
import type { User } from '$lib/api';

let current = $state<User | null>(null);

export const session = {
  get user() {
    return current;
  },
  set(user: User | null) {
    current = user;
  }
};
