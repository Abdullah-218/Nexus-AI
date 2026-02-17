"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import { ChevronRight, ChevronLeft, Plus, X, Loader2, Briefcase, Zap, Star, AlertTriangle } from "lucide-react";
import { onboardUser } from "@/lib/api";
import { useStore } from "@/store/useStore";
import ParticleBackground from "@/components/ParticleBackground";

const steps = ["Profile", "Skills", "Your Role"];

function TagInput({ label, value, onChange, placeholder, icon: Icon, color }: any) {
  const [input, setInput] = useState("");
  const add = () => {
    const v = input.trim();
    if (v && !value.includes(v)) { onChange([...value, v]); setInput(""); }
  };
  return (
    <div>
      <label className="block text-sm font-medium text-white/60 mb-2 flex items-center gap-2">
        <Icon size={14} className={color} />{label}
      </label>
      <div className="flex gap-2 mb-2">
        <input value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), add())}
          placeholder={placeholder} className="input-field" />
        <button type="button" onClick={add} className="btn-ghost px-4 py-3">
          <Plus size={16} />
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {value.map((v: string) => (
          <span key={v} className="tag flex items-center gap-1.5">
            {v}
            <button onClick={() => onChange(value.filter((x: string) => x !== v))} className="hover:text-red-400">
              <X size={11} />
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  const router       = useRouter();
  const params       = useSearchParams();
  const setUser      = useStore((s) => s.setUser);
  const setRole      = useStore((s) => s.setRole);
  const markOnboarded = useStore((s) => s.markOnboarded);

  const userId = params.get("uid") || "";
  const email  = params.get("email") || "";

  const [step,      setStep]      = useState(0);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState("");

  // Form state
  const [name,       setName]       = useState("");
  const [phone,      setPhone]      = useState("");
  const [expYears,   setExpYears]   = useState(0);
  const [skills,     setSkills]     = useState<string[]>([]);
  const [strengths,  setStrengths]  = useState<string[]>([]);
  const [weaknesses, setWeaknesses] = useState<string[]>([]);
  const [targetRole, setTargetRole] = useState("");

  async function handleSubmit() {
    setLoading(true);
    setError("");
    try {
      const result = await onboardUser({
        name, email, target_role: targetRole,
        skills, strengths, weaknesses,
        experience_years: expYears, phone,
      });
      setUser(result.user_id, name);
      setRole(targetRole);
      markOnboarded();
      router.push(`/readiness?uid=${result.user_id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const canNext = step === 0
    ? name.trim().length > 0
    : step === 1
    ? skills.length > 0 && strengths.length > 0 && weaknesses.length > 0
    : targetRole.trim().length > 0;

  return (
    <div className="min-h-screen bg-[#0F1117] bg-grid flex items-center justify-center px-4">
      <ParticleBackground />
      <div className="fixed top-20 right-20 w-64 h-64 bg-violet-600/8 rounded-full blur-3xl pointer-events-none" />

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="w-full max-w-lg">
        {/* Progress */}
        <div className="flex items-center gap-2 mb-8 justify-center">
          {steps.map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all
                ${i <= step ? "bg-blue-600 text-white shadow-glow" : "bg-white/[0.06] text-white/30"}`}>
                {i + 1}
              </div>
              <span className={`text-sm ${i === step ? "text-white" : "text-white/30"}`}>{s}</span>
              {i < steps.length - 1 && <div className={`w-8 h-px ${i < step ? "bg-blue-600" : "bg-white/10"}`} />}
            </div>
          ))}
        </div>

        <div className="glass p-8">
          <AnimatePresence mode="wait">
            {step === 0 && (
              <motion.div key="s0" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
                <h2 className="text-2xl font-black mb-1">Tell us about you</h2>
                <p className="text-white/40 text-sm mb-6">Basic info to personalise your career navigator.</p>
                <div>
                  <label className="block text-sm font-medium text-white/60 mb-2">Full Name *</label>
                  <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex Johnson" className="input-field" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-white/60 mb-2">Email</label>
                  <input value={email} disabled className="input-field opacity-50 cursor-not-allowed" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-white/60 mb-2">Phone</label>
                    <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+1 555 000" className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/60 mb-2">Years of Experience</label>
                    <input type="number" min={0} value={expYears} onChange={(e) => setExpYears(+e.target.value)} className="input-field" />
                  </div>
                </div>
              </motion.div>
            )}

            {step === 1 && (
              <motion.div key="s1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
                <h2 className="text-2xl font-black mb-1">Skills & Attributes</h2>
                <p className="text-white/40 text-sm mb-6">Press Enter or click + to add each item.</p>
                <TagInput label="Current Skills" value={skills} onChange={setSkills} placeholder="e.g. Python, React" icon={Zap} color="text-blue-400" />
                <TagInput label="Strengths" value={strengths} onChange={setStrengths} placeholder="e.g. problem-solving" icon={Star} color="text-yellow-400" />
                <TagInput label="Weaknesses" value={weaknesses} onChange={setWeaknesses} placeholder="e.g. SQL, public speaking" icon={AlertTriangle} color="text-orange-400" />
              </motion.div>
            )}

            {step === 2 && (
              <motion.div key="s2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-5">
                <h2 className="text-2xl font-black mb-1">Your Target Role</h2>
                <p className="text-white/40 text-sm mb-6">What career position are you aiming for?</p>
                <div>
                  <label className="block text-sm font-medium text-white/60 mb-2 flex items-center gap-2">
                    <Briefcase size={14} className="text-violet-400" /> Target Role *
                  </label>
                  <input value={targetRole} onChange={(e) => setTargetRole(e.target.value)}
                    placeholder="e.g. Full Stack Developer, Data Scientist" className="input-field" />
                </div>
                {error && (
                  <div className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-xl p-3">{error}</div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Nav buttons */}
          <div className="flex justify-between mt-8">
            <button onClick={() => setStep(s => s - 1)} disabled={step === 0} className="btn-ghost flex items-center gap-2 disabled:opacity-0">
              <ChevronLeft size={16} /> Back
            </button>
            {step < steps.length - 1 ? (
              <button onClick={() => setStep(s => s + 1)} disabled={!canNext} className="btn-primary flex items-center gap-2">
                Next <ChevronRight size={16} />
              </button>
            ) : (
              <button onClick={handleSubmit} disabled={!canNext || loading} className="btn-primary flex items-center gap-2">
                {loading ? <><Loader2 size={16} className="animate-spin" /> Creating...</> : <>Launch Navigator <ChevronRight size={16} /></>}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
