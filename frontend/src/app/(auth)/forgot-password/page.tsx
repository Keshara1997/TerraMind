import Link from "next/link";

export default function ForgotPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0b1017] px-4 text-white">
      <div className="w-full max-w-md space-y-4 rounded-xl border border-white/10 bg-[#111923] p-8">
        <h1 className="text-2xl font-semibold">Password reset</h1>
        <p className="text-sm text-slate-400">
          Self-service password reset is not configured yet.
        </p>
        <Link href="/login" className="text-sm text-cyan-400 hover:underline">
          Back to login
        </Link>
      </div>
    </div>
  );
}