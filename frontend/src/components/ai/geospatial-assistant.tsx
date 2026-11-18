"use client";

import { useState } from "react";
import { aiService } from "@/services/ai.service";

interface Props {
  projectId: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

const suggestions = [
  "How has vegetation changed over this period?",
  "Explain the latest NDVI observation.",
  "Summarise the vegetation condition.",
  "What limitations should I consider in this analysis?",
];

export default function GeospatialAssistant({
  projectId,
}: Props) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function sendQuestion(value = question) {
    const text = value.trim();

    if (!text || !projectId || loading) return;

    setError("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);

    setQuestion("");

    try {
      const result = await aiService.ask(projectId, {
        question: text,
      });

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.answer,
        },
      ]);
    } catch {
      setError("Unable to get an AI response. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-xl border bg-white p-5">
      <div className="mb-5">
        <h2 className="text-lg font-semibold">
          Geospatial AI Assistant
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Ask questions about your project's satellite observations.
        </p>
      </div>

      {messages.length === 0 && (
        <div className="mb-5 space-y-2">
          <p className="text-sm font-medium">
            Try asking:
          </p>

          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => sendQuestion(suggestion)}
              disabled={loading}
              className="block w-full rounded-lg border p-3 text-left text-sm hover:bg-gray-50 disabled:opacity-50"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}

      <div className="mb-4 max-h-[450px] space-y-4 overflow-y-auto">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`rounded-xl p-4 ${
              message.role === "user"
                ? "ml-8 bg-blue-50"
                : "mr-8 bg-gray-50"
            }`}
          >
            <p className="mb-2 text-xs font-semibold uppercase text-gray-500">
              {message.role === "user" ? "You" : "Aleph AI"}
            </p>

            <p className="whitespace-pre-wrap text-sm leading-6">
              {message.content}
            </p>
          </div>
        ))}

        {loading && (
          <p className="text-sm text-gray-500">
            Analysing project observations...
          </p>
        )}
      </div>

      {error && (
        <p className="mb-3 text-sm text-red-600">{error}</p>
      )}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          void sendQuestion();
        }}
        className="flex gap-2"
      >
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about your satellite data..."
          maxLength={2000}
          disabled={loading}
          className="min-w-0 flex-1 rounded-lg border p-3 text-sm"
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-lg bg-blue-600 px-5 text-sm font-medium text-white disabled:opacity-50"
        >
          Ask
        </button>
      </form>
    </section>
  );
}