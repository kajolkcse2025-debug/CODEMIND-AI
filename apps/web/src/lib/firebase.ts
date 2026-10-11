import { getApp, getApps, initializeApp, type FirebaseApp } from "firebase/app";
import { connectAuthEmulator, getAuth, type Auth } from "firebase/auth";

import { FIREBASE_AUTH_EMULATOR_URL, firebaseConfig, isFirebaseConfigured } from "@/lib/env";

export class FirebaseNotConfiguredError extends Error {
  constructor() {
    super(
      "Firebase is not configured. Copy .env.example to .env and fill in the VITE_FIREBASE_* values.",
    );
    this.name = "FirebaseNotConfiguredError";
  }
}

function createApp(): FirebaseApp {
  return getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
}

function createAuth(): Auth | null {
  if (!isFirebaseConfigured) return null;
  const instance = getAuth(createApp());
  if (FIREBASE_AUTH_EMULATOR_URL) {
    connectAuthEmulator(instance, FIREBASE_AUTH_EMULATOR_URL, { disableWarnings: true });
  }
  return instance;
}

/** ``null`` when Firebase is not configured, so the UI can explain instead of crashing. */
export const firebaseAuth: Auth | null = createAuth();

export function requireFirebaseAuth(): Auth {
  if (!firebaseAuth) throw new FirebaseNotConfiguredError();
  return firebaseAuth;
}
