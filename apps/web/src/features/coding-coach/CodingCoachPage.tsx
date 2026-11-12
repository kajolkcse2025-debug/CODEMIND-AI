
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { sendAiCoachMessage } from "@/lib/api/aiCoach";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export function CodingCoachPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I'm your CodeMind AI Mentor. 👋\n\nI'm here to help you improve your coding skills, understand DSA, debug errors, prepare for interviews, and build your confidence.\n\nTell me what you're currently learning or struggling with. We'll work through it step by step.",
    },
  ]);

  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const message = input.trim();
    if (!message || loading) return;

    setInput("");
    setError(null);

    setMessages((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
      },
    ]);

    setLoading(true);

    try {
      const response = await sendAiCoachMessage({
        message,
        ...(conversationId
          ? { conversation_id: conversationId }
          : {}),
      });

      setConversationId(response.conversation_id);

      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.reply,
        },
      ]);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Couldn't reach your AI Mentor. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 p-4 sm:p-6">
      <header className="space-y-2">
        <p className="text-sm font-semibold tracking-wider text-primary">
          CODEMIND AI
        </p>
        <h1 className="text-3xl font-bold tracking-tight">
          Your AI Mentor
        </h1>
        <p className="text-muted-foreground">
          Your personal coding companion. Learn, improve, and prepare for
          your dream tech career.
        </p>
      </header>

      <section className="flex min-h-[65vh] flex-col overflow-hidden rounded-2xl border bg-card shadow-sm">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <div>
            <h2 className="font-semibold">CodeMind Mentor</h2>
            <p className="text-xs text-muted-foreground">
              AI-powered coding guidance
            </p>
          </div>

          <span className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="h-2 w-2 rounded-full bg-green-500" />
            Mentor ready
          </span>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto p-4 sm:p-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm leading-7 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}
              >
                {message.role === "assistant" && (
                  <p className="mb-2 text-xs font-semibold text-primary">
                    CODEMIND AI MENTOR
                  </p>
                )}

                {message.role === "assistant" ? (
                  <div className="break-words [&_h1]:mb-2 [&_h1]:mt-4 [&_h1]:text-xl [&_h1]:font-bold [&_h2]:mb-2 [&_h2]:mt-4 [&_h2]:text-lg [&_h2]:font-bold [&_h3]:mb-1 [&_h3]:mt-3 [&_h3]:font-semibold [&_p]:mb-3 [&_p:last-child]:mb-0 [&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-6 [&_li]:mb-1 [&_strong]:font-bold [&_a]:text-primary [&_a]:underline [&_blockquote]:border-l-2 [&_blockquote]:border-primary [&_blockquote]:pl-3 [&_blockquote]:italic [&_pre]:my-3 [&_pre]:overflow-x-auto [&_pre]:rounded-lg [&_pre]:bg-background [&_pre]:p-3 [&_code]:rounded [&_code]:bg-background [&_code]:px-1 [&_code]:py-0.5 [&_pre_code]:bg-transparent [&_pre_code]:p-0">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      skipHtml
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap break-words">
                    {message.content}
                  </p>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-muted px-4 py-3 text-sm text-muted-foreground">
                Your mentor is thinking...
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {error && (
          <p className="px-5 pb-2 text-sm text-destructive" role="alert">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} className="border-t p-4 sm:p-5">
          <div className="flex items-end gap-3">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  event.currentTarget.form?.requestSubmit();
                }
              }}
              placeholder="Ask your AI Mentor anything about coding, DSA, interviews..."
              rows={2}
              disabled={loading}
              className="min-h-12 flex-1 resize-none rounded-xl border bg-background px-4 py-3 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-60"
            />

            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>

          <p className="mt-2 text-xs text-muted-foreground">
            Press Enter to send · Shift + Enter for a new line
          </p>
        </form>
      </section>
    </main>
  );
}
