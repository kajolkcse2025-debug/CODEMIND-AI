
import { api } from "@/lib/api";

export interface AiCoachRequest {
  message: string;
  conversation_id?: string;
}

export interface AiCoachResponse {
  conversation_id: string;
  reply: string;
  provider: string;
}

export function sendAiCoachMessage(
  request: AiCoachRequest,
): Promise<AiCoachResponse> {
  return api.post<AiCoachResponse>(
    "/api/v1/ai-coach/chat",
    request,
  );
}
