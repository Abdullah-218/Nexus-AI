"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { Brain, Mail, ArrowRight, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import ParticleBackground from "@/components/ParticleBackground";

export default function AuthPage() {
  const router   = useRouter();
  const setUser  = useStore((s) => s.setUser);
  const setRole  = useStore((s) => s.setRole);
  const markOnboarded = useStore((s) => s.markOnboarded);

  const [email,   setEmail]   = useState("");
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    setError("");

    try {
      // Check if user exists by attempting dashboard lookup
      // We search by email — backend find_by_email handles this
      const res = await api.post("/api/onboard", {
        name: "", email, target_role: "__email_check__",
        skills: [], strengths: [], weaknesses: [], experience_years: 0,
      });

      if (res.data.exists) {
        // Existing user → go to dashboard
        setUser(res.data.user_id, res.data.profile?.name || email);
        setRole(res.data.profile?.target_role || "");
        markOnboarded();
        router.push("/dashboard");
      } else {
        // New user → go to onboarding (pass email via query)
        setUser(res.data.user_id, email);
        router.push(`/onboarding?uid=${res.data.user_id}&email=${encodeURIComponent(email)}`);
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#0F1117] bg-grid flex items-center justify-center px-4">
      <ParticleBackground />
      <div className="fixed top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/8 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center mx-auto mb-4 shadow-glow">
            <Brain size={28} className="text-white" />
          </div>
          <h1 className="text-3xl font-black mb-2">Welcome to Nexus-AI</h1>
          <p className="text-white/40">Enter your email to get started or continue your journey.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="glass p-8 space-y-5">
          <div>
            <label className="block text-sm font-medium text-white/60 mb-2">Email address</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="input-field pl-10"
                required
              />
            </div>
          </div>

          {error && (
            <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl p-3">
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
            {loading ? (
              <><Loader2 size={16} className="animate-spin" /> Checking...</>
            ) : (
              <>Continue <ArrowRight size={16} /></>
            )}
          </button>
        </form>

        <p className="text-center text-white/30 text-xs mt-6">
          New email → onboarding · Existing email → your dashboard
        </p>
      </motion.div>
    </div>
  );
}
