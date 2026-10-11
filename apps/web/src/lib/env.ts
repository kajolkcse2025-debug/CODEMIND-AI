/** Typed access to build-time configuration. Everything here is PUBLIC (shipped to browsers). */
const env = import.meta.env;

function clean(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export const API_BASE_URL = (
  clean(env.VITE_API_BASE_URL) ?? (env.DEV ? "http://localhost:8000" : "")
).replace(/\/$/, "");

export const firebaseConfig = {
  apiKey: clean(env.VITE_FIREBASE_API_KEY),
  authDomain: clean(env.VITE_FIREBASE_AUTH_DOMAIN),
  projectId: clean(env.VITE_FIREBASE_PROJECT_ID),
  appId: clean(env.VITE_FIREBASE_APP_ID),
};

export const FIREBASE_AUTH_EMULATOR_URL = clean(env.VITE_FIREBASE_AUTH_EMULATOR_URL);

export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.authDomain &&
  firebaseConfig.projectId &&
  firebaseConfig.appId,
);
