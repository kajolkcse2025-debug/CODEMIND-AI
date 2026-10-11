import { ApiClient } from "@/lib/api/client";
import { API_BASE_URL } from "@/lib/env";
import { firebaseAuth } from "@/lib/firebase";

/** The app-wide API client. Feature code imports ``api`` and never calls fetch directly. */
export const api = new ApiClient({
  baseUrl: API_BASE_URL,
  getToken: async (forceRefresh) => {
    const user = firebaseAuth?.currentUser;
    return user ? user.getIdToken(forceRefresh) : null;
  },
});

export { ApiClient } from "@/lib/api/client";
export { ApiError, describeError, fieldErrors, isApiError } from "@/lib/api/errors";
