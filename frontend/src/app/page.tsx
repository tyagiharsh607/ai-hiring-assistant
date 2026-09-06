import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="grid gap-6 sm:grid-cols-3">
      <Link href="/screening">
        <Card className="h-full transition-colors hover:border-zinc-400">
          <CardHeader>
            <CardTitle>Screening Call</CardTitle>
            <CardDescription>
              Trigger a Hunar voice agent to call a candidate directly and screen them against a job
              description.
            </CardDescription>
          </CardHeader>
        </Card>
      </Link>
      <Link href="/reachout">
        <Card className="h-full transition-colors hover:border-zinc-400">
          <CardHeader>
            <CardTitle>People Search & Reachout</CardTitle>
            <CardDescription>
              Paste a JD, find matching people via People Data Labs, and reach out with a voice agent
              call.
            </CardDescription>
          </CardHeader>
        </Card>
      </Link>
      <Link href="/dashboard">
        <Card className="h-full transition-colors hover:border-zinc-400">
          <CardHeader>
            <CardTitle>Dashboard</CardTitle>
            <CardDescription>
              See every call placed, its status, and the structured answers extracted from the
              conversation.
            </CardDescription>
          </CardHeader>
        </Card>
      </Link>
    </div>
  );
}
