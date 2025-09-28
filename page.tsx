import { Navbar } from "@/components/navbar";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-grow p-4">
        <h1 className="text-3xl font-bold">Welcome to VoiceFlow AI Dashboard</h1>
        <p className="mt-4">This is where you can manage your agents, phone numbers, and view call logs.</p>
      </main>
    </div>
  );
}

