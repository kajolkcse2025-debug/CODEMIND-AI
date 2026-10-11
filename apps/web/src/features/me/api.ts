import type { MeResponse } from "@codemind/shared";

import { api } from "@/lib/api";

export const fetchMe = () => api.get<MeResponse>("/api/v1/me");
