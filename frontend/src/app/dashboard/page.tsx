"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DashboardCall, listCalls, syncCalls } from "@/lib/api";

function statusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  if (["COMPLETED"].includes(status)) return "default";
  if (["FAILED", "NOT_CONNECTED", "CANCELLED"].includes(status)) return "destructive";
  if (["IN_PROGRESS", "RINGING", "INITIATED", "SCHEDULED"].includes(status)) return "secondary";
  return "outline";
}

export default function DashboardPage() {
  const [calls, setCalls] = useState<DashboardCall[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  async function load() {
    try {
      // Best-effort: pull any status Hunar has that the webhook hasn't delivered yet.
      await syncCalls().catch(() => undefined);
      setCalls(await listCalls());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load calls");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 8000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <p className="text-sm text-zinc-500">Loading...</p>;
  if (error) return <p className="text-sm text-red-600">{error}</p>;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Calls</h1>
        <Button variant="outline" size="sm" onClick={load}>
          Refresh
        </Button>
      </div>
      {calls.length === 0 && <p className="text-sm text-zinc-500">No calls yet.</p>}
      {calls.map((call) => (
        <Card key={call.call_id}>
          <CardHeader
            className="cursor-pointer"
            onClick={() => setExpanded(expanded === call.call_id ? null : call.call_id)}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">
                {call.candidate_name ?? "Unknown"}{" "}
                <span className="text-xs font-normal text-zinc-500">
                  ({call.flow === "screening" ? "Screening" : "Reachout"})
                </span>
              </CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant={statusVariant(call.status)}>{call.status}</Badge>
                {call.engagement_status && <Badge variant="outline">{call.engagement_status}</Badge>}
              </div>
            </div>
          </CardHeader>
          {expanded === call.call_id && (
            <CardContent className="flex flex-col gap-3 text-sm">
              <p className="text-zinc-500">
                {call.candidate_phone} · {call.candidate_title ?? "—"} · {new Date(call.created_at).toLocaleString()}
              </p>
              {call.summary && (
                <div>
                  <p className="font-medium">Summary</p>
                  <p className="text-zinc-700">{call.summary}</p>
                </div>
              )}
              {call.result && (
                <div>
                  <p className="font-medium">Extracted answers</p>
                  <pre className="whitespace-pre-wrap rounded bg-zinc-100 p-3 text-xs">
                    {JSON.stringify(call.result, null, 2)}
                  </pre>
                </div>
              )}
              {call.transcript && (
                <div>
                  <p className="font-medium">Transcript</p>
                  <pre className="whitespace-pre-wrap rounded bg-zinc-100 p-3 text-xs">{call.transcript}</pre>
                </div>
              )}
              {call.recording_url && (
                <audio controls src={call.recording_url} className="w-full">
                  <track kind="captions" />
                </audio>
              )}
              {!call.summary && !call.result && !call.transcript && (
                <p className="text-zinc-500">Waiting for the call to complete...</p>
              )}
            </CardContent>
          )}
        </Card>
      ))}
    </div>
  );
}
