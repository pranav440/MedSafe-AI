import { useState } from "react";
import { FlaskConical, AlertTriangle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { AlertBanner } from "@/components/AlertBanner";
import { api, type InteractionResult } from "@/services/api";

export default function DrugInteractions() {
  const [input, setInput] = useState("Warfarin\nAspirin");
  const [result, setResult] = useState<InteractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCheck = async () => {
    const medicines = input.split("\n").map(s => s.trim()).filter(Boolean);
    if (medicines.length < 2) {
      setError("Please enter at least 2 medicine names.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.checkInteractions(medicines);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to check interactions.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Drug Interaction Checker</h2>
        <p className="text-sm text-muted-foreground mt-1">Enter medicine names (one per line) to check for interactions</p>
      </div>

      <div className="glass-card p-6 space-y-4">
        <Textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          rows={4}
          placeholder={"Enter medicine names, one per line:\nWarfarin\nAspirin"}
          className="bg-background/50 text-foreground placeholder:text-muted-foreground/60"
        />
        <Button onClick={handleCheck} disabled={loading} className="w-full">
          <FlaskConical className="h-4 w-4 mr-2" />
          Check Interactions
        </Button>
      </div>

      {loading && <LoadingSpinner />}
      {error && <AlertBanner severity="MEDIUM" message={error} />}

      {result && (
        <>
          <div className="glass-card p-5">
            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">Medicines checked:</strong>{" "}
              {result.medicines_checked.join(", ")}
            </p>
          </div>

          {result.interactions_found.length > 0 ? (
            <div className="space-y-3">
              <AlertBanner severity="HIGH" message="Drug interactions detected!" />
              {result.interactions_found.map((ix, i) => (
                <div key={i} className="glass-card p-5">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-severity-high mt-0.5 shrink-0" />
                    <div>
                      <p className="text-sm font-semibold text-foreground">
                        {ix.drug_1} ↔ {ix.drug_2}
                        <span className="ml-2 text-xs px-2 py-0.5 rounded-full severity-high">
                          {ix.severity}
                        </span>
                      </p>
                      <p className="text-sm text-muted-foreground mt-1">{ix.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-3 glass-card p-5">
              <CheckCircle className="h-5 w-5 text-severity-low" />
              <p className="text-sm text-foreground">
                {result.safe_message || "No known interactions found. Always consult a healthcare professional."}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
