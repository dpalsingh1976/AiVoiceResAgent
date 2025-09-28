
import Link from "next/link";

export function Navbar() {
  return (
    <nav className="bg-primary text-primary-foreground p-4 flex justify-between items-center">
      <Link href="/" className="text-lg font-bold">
        VoiceFlow AI
      </Link>
      <div className="space-x-4">
        <Link href="/dashboard" className="hover:underline">
          Dashboard
        </Link>
        <Link href="/agents" className="hover:underline">
          Agents
        </Link>
        <Link href="/phone-numbers" className="hover:underline">
          Phone Numbers
        </Link>
        <Link href="/call-logs" className="hover:underline">
          Call Logs
        </Link>
        <Link href="/menu" className="hover:underline">
          Menu
        </Link>
        <Link href="/orders" className="hover:underline">
          Orders
        </Link>
        <Link href="/reservations" className="hover:underline">
          Reservations
        </Link>
        <Link href="/campaigns" className="hover:underline">
          Campaigns
        </Link>
        <Link href="/social-media" className="hover:underline">
          Social Media
        </Link>
      </div>
    </nav>
  );
}


