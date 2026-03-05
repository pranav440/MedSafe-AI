import { useState } from "react";
import { Stethoscope, Search, AlertTriangle, Lightbulb, Heart, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SymptomResponseCard } from "@/components/SymptomResponseCard";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { AlertBanner } from "@/components/AlertBanner";
import { api, type SymptomResult } from "@/services/api";

export default function SymptomGuidance() {
  const [input, setInput] = useState("fever\nheadache\nfatigue");
  const [result, setResult] = useState<SymptomResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    const symptoms = input.split("\n").map(s => s.trim()).filter(Boolean);
    if (!symptoms.length) {
      setError("Please enter at least one symptom.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.getSymptomGuidance(symptoms);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to get symptom guidance.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Symptom Guidance</h2>
        <p className="text-sm text-muted-foreground mt-1">Enter your symptoms for AI-powered health guidance</p>
      </div>

      <div className="glass-card p-6 space-y-4">
        <Textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          rows={3}
          placeholder={"Enter symptoms, one per line:\nfever\nheadache"}
          className="bg-background/50 text-foreground placeholder:text-muted-foreground/60"
        />
        <Button onClick={handleSubmit} disabled={loading} className="w-full">
          <Search className="h-4 w-4 mr-2" />
          Get Guidance
        </Button>
      </div>

      {loading && <LoadingSpinner />}
      {error && <AlertBanner severity="MEDIUM" message={error} />}

      {result && result.matched_conditions.length > 0 && (
        <>
          {result.matched_conditions.map((cond, i) => (
            <div key={i} className="space-y-4">
              <div className="glass-card p-4">
                <p className="text-sm font-semibold text-foreground">
                  🏷 {cond.condition}
                  <span className="ml-2 text-xs text-muted-foreground">Match: {cond.match_score}%</span>
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <SymptomResponseCard title="Possible Causes" items={cond.possible_causes} icon={Stethoscope} accentColor="text-chart-blue" />
                <SymptomResponseCard title="Home Remedies" items={cond.home_remedies} icon={Lightbulb} accentColor="text-chart-teal" />
                <SymptomResponseCard title="Lifestyle Advice" items={cond.lifestyle_advice} icon={Heart} accentColor="text-chart-green" />
                <SymptomResponseCard title="Warning Signs" items={cond.warning_signs} icon={ShieldAlert} accentColor="text-chart-red" />
              </div>
            </div>
          ))}
        </>
      )}

      {result && result.matched_conditions.length === 0 && (
        <div className="glass-card p-5 text-center">
          <p className="text-sm text-muted-foreground">No matching conditions found. Try different symptom descriptions.</p>
        </div>
      )}

      {result && (
        <div className="glass-card p-4 border-severity-medium/30">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-severity-medium shrink-0 mt-0.5" />
            <p className="text-xs text-muted-foreground">
              <strong>Disclaimer:</strong> {result.disclaimer}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
