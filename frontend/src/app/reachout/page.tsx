"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { PdlCandidate, searchCandidates, triggerReachoutCall } from "@/lib/api";

// People Data Labs' free/trial tier matches people but redacts contact fields (phone/email
// come back null) - recruiters confirm/enter the real number before the call goes out.

export default function ReachoutPage() {
  const [jobDescription, setJobDescription] = useState("");
  const [roleTitle, setRoleTitle] = useState("");
  const [location, setLocation] = useState("");
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [jobDescriptionId, setJobDescriptionId] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<PdlCandidate[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [phones, setPhones] = useState<Record<number, string>>({});
  const [callingIndex, setCallingIndex] = useState<number | null>(null);
  const [calledIndexes, setCalledIndexes] = useState<Set<number>>(new Set());

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setSearching(true);
    setError(null);
    setCandidates([]);
    setPhones({});
    try {
      const res = await searchCandidates({ job_description: jobDescription, role_title: roleTitle, location: location || undefined });
      setJobDescriptionId(res.job_description_id);
      setCandidates(res.candidates);
      setPhones(Object.fromEntries(res.candidates.map((c, i) => [i, c.phone ?? ""])));
      setHasSearched(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setSearching(false);
    }
  }

  async function handleCall(candidate: PdlCandidate, index: number) {
    const phone = phones[index]?.trim();
    if (!jobDescriptionId || !phone) return;
    setCallingIndex(index);
    setError(null);
    try {
      await triggerReachoutCall({
        job_description_id: jobDescriptionId,
        name: candidate.name,
        phone,
        email: candidate.email,
        title: candidate.title,
        company: candidate.company,
      });
      setCalledIndexes((prev) => new Set(prev).add(index));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Call failed");
    } finally {
      setCallingIndex(null);
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <Card>
        <CardHeader>
          <CardTitle>1. Find candidates from a job description</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex flex-col gap-4">
            <div className="grid gap-2">
              <Label htmlFor="jd">Job description</Label>
              <Textarea id="jd" required rows={6} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="role">Role title (used to match people, e.g. &quot;backend engineer&quot;)</Label>
                <Input id="role" required value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="location">Location (optional)</Label>
                <Input id="location" value={location} onChange={(e) => setLocation(e.target.value)} />
              </div>
            </div>
            <Button type="submit" disabled={searching} className="w-fit">
              {searching ? "Searching..." : "Search candidates"}
            </Button>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </form>
        </CardContent>
      </Card>

      {hasSearched && candidates.length === 0 && (
        <p className="text-sm text-zinc-500">
          No matches for that role title. Try a broader title (e.g. &quot;engineer&quot; instead of a
          niche one) or drop the location filter.
        </p>
      )}

      {candidates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>2. Reach out via voice call</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Company</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {candidates.map((c, i) => (
                  <TableRow key={i}>
                    <TableCell>{c.name}</TableCell>
                    <TableCell>{c.title ?? "—"}</TableCell>
                    <TableCell>{c.company ?? "—"}</TableCell>
                    <TableCell>
                      <Input
                        className="h-8 w-40"
                        placeholder="+91..."
                        value={phones[i] ?? ""}
                        onChange={(e) => setPhones((prev) => ({ ...prev, [i]: e.target.value }))}
                        disabled={calledIndexes.has(i)}
                      />
                    </TableCell>
                    <TableCell>
                      {calledIndexes.has(i) ? (
                        <Badge variant="secondary">Call queued</Badge>
                      ) : (
                        <Button
                          size="sm"
                          disabled={!phones[i]?.trim() || callingIndex === i}
                          onClick={() => handleCall(c, i)}
                        >
                          {callingIndex === i ? "Calling..." : "Call"}
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <p className="mt-3 text-xs text-zinc-500">
              PDL&apos;s free tier matches people but doesn&apos;t expose phone numbers — confirm/enter a
              real number per row before calling. Check the Dashboard for call outcomes.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
