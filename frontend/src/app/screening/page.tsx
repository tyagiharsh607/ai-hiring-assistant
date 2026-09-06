"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { triggerScreeningCall } from "@/lib/api";

export default function ScreeningPage() {
  const [candidateName, setCandidateName] = useState("");
  const [phone, setPhone] = useState("");
  const [roleTitle, setRoleTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await triggerScreeningCall({
        candidate_name: candidateName,
        phone,
        role_title: roleTitle || undefined,
        job_description: jobDescription,
      });
      setResult(`Call queued (call #${res.call_id}, status: ${res.status}). Check the Dashboard for results.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-xl">
      <Card>
        <CardHeader>
          <CardTitle>Screen a candidate by voice call</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Candidate name</Label>
              <Input id="name" required value={candidateName} onChange={(e) => setCandidateName(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="phone">Phone (E.164, e.g. +9198xxxxxxx)</Label>
              <Input id="phone" required value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="role">Role title (optional)</Label>
              <Input id="role" value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="jd">Job description</Label>
              <Textarea
                id="jd"
                required
                rows={8}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Placing call..." : "Call candidate"}
            </Button>
            {result && <p className="text-sm text-green-700">{result}</p>}
            {error && <p className="text-sm text-red-600">{error}</p>}
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
