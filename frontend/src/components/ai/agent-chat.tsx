"use client";

import { useState } from "react";
import { agentService } from "@/services/agent.service";

interface Props {
  projectId: string;
}

export default function AgentChat({ projectId }: Props) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const result = await agentService.ask(projectId, {
        question: question.trim(),
      });

      setAnswer(result.answer);
    } catch {
      setError("Unable to complete the geospatial analysis.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4 rounded-xl border p-5">
      <div>
        <h2 className="text-lg font-semibold">
          Aleph Geospatial Agent
        </h2>

        <p className="text-sm text-muted-foreground">
          Ask questions about your project's environmental data.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Analyse the vegetation trend in this project..."
          maxLength={4000}
          rows={4}
          className="w-full rounded-lg border bg-background p-3"
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
        >
          {loading ? "Analysing..." : "Ask Aleph"}
        </button>
      </form>

      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}

      {answer && (
        <div className="whitespace-pre-wrap rounded-lg bg-muted p-4">
          {answer}
        </div>
      )}
    </section>
  );
}