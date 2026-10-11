import type { ProfileIn, ProfileOut } from "@codemind/shared";

import { api } from "@/lib/api";

export const fetchProfile = () => api.get<ProfileOut>("/api/v1/profile");
export const createProfile = (body: ProfileIn) => api.post<ProfileOut>("/api/v1/profile", body);
export const updateProfile = (body: ProfileIn) => api.put<ProfileOut>("/api/v1/profile", body);
