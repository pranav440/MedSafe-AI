import { useState } from "react";
import { FileWarning, Send, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { AlertBanner } from "@/components/AlertBanner";
import { api, type SideEffectResult } from "@/services/api";

export default function SideEffectReporter() {
  const [form, setForm] = useState({ age: "", gender: "", medicine: "", dosage: "", symptoms: "" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SideEffectResult | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!form.age || !form.gender || !form.medicine || !form.symptoms) {
      setError("Please fill in all required fields (age, gender, medicine, symptoms).");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.reportSideEffect({
        age: parseInt(form.age),
        gender: form.gender,
        medicine: form.medicine,
        dosage: form.dosage || "not specified",
        symptoms: form.symptoms.split(",").map(s => s.trim()).filter(Boolean),
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to submit side effect report.");
    } finally {
      setLoading(false);
    }
  };

  const isValid = form.age && form.gender && form.medicine && form.symptoms;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Side Effect Reporter</h2>
        <p className="text-sm text-muted-foreground mt-1">Report medication side effects for AI-powered safety analysis</p>
      </div>

      <div className="glass-card p-6 space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label className="text-foreground">Age</Label>
            <Input type="number" placeholder="e.g., 35" value={form.age} onChange={e => setForm(f => ({ ...f, age: e.target.value }))} className="bg-background/50 text-foreground placeholder:text-muted-foreground/60" />
          </div>
          <div className="space-y-2">
            <Label className="text-foreground">Gender</Label>
            <Select value={form.gender} onValueChange={v => setForm(f => ({ ...f, gender: v }))}>
              <SelectTrigger className="bg-background/50 text-foreground"><SelectValue placeholder="Select gender" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Male">Male</SelectItem>
                <SelectItem value="Female">Female</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2">
          <Label className="text-foreground">Medicine Name</Label>
          <Input placeholder="e.g., Ibuprofen" value={form.medicine} onChange={e => setForm(f => ({ ...f, medicine: e.target.value }))} className="bg-background/50 text-foreground placeholder:text-muted-foreground/60" />
        </div>

        <div className="space-y-2">
          <Label className="text-foreground">Dosage</Label>
          <Input placeholder="e.g., 400mg twice daily" value={form.dosage} onChange={e => setForm(f => ({ ...f, dosage: e.target.value }))} className="bg-background/50 text-foreground placeholder:text-muted-foreground/60" />
        </div>

        <div className="space-y-2">
          <Label className="text-foreground">Symptoms Experienced (comma separated)</Label>
          <Textarea placeholder="e.g., nausea, dizziness, stomach upset" rows={4} value={form.symptoms} onChange={e => setForm(f => ({ ...f, symptoms: e.target.value }))} className="bg-background/50 text-foreground placeholder:text-muted-foreground/60" />
        </div>

        <Button onClick={handleSubmit} disabled={!isValid || loading} className="w-full">
          <Send className="h-4 w-4 mr-2" />
          Submit Report
        </Button>
      </div>

      {loading && <LoadingSpinner />}
      {error && <AlertBanner severity="MEDIUM" message={error} />}

      {result && (
        <div className="space-y-4 animate-slide-in">
          {/* Analysis */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-foreground mb-2">🧠 AI Analysis</h3>
            <p className="text-sm text-muted-foreground">{result.analysis}</p>
          </div>

          {/* Urgency */}
          <div className={`glass-card p-5 ${result.urgency.includes("HIGH") ? "border-severity-high/30" : "border-severity-low/30"}`}>
            <div className="flex items-center gap-2">
              {result.urgency.includes("HIGH") ? (
                <AlertTriangle className="h-5 w-5 text-severity-high" />
              ) : (
                <CheckCircle className="h-5 w-5 text-severity-low" />
              )}
              <p className="text-sm font-medium text-foreground">{result.urgency}</p>
            </div>
          </div>

          {/* Recommendations */}
          <div className="glass-card p-5 space-y-2">
            <h3 className="text-sm font-semibold text-foreground">📋 Recommendations</h3>
            {result.recommendations.map((rec, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                <span className="text-primary font-bold">{i + 1}.</span>
                <span>{rec}</span>
              </div>
            ))}
          </div>

          {/* Disclaimer */}
          <div className="glass-card p-4 border-severity-medium/30">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 text-severity-medium shrink-0 mt-0.5" />
              <p className="text-xs text-muted-foreground">
                <strong>Disclaimer:</strong> {result.disclaimer}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
