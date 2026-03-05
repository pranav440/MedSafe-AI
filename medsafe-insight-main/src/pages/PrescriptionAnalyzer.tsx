import { useState } from "react";
import { Upload, FileSearch, Type } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { MedicineList } from "@/components/MedicineList";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { AlertBanner } from "@/components/AlertBanner";
import { api, type PrescriptionResult } from "@/services/api";

export default function PrescriptionAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState("");
  const [result, setResult] = useState<PrescriptionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImageAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.analyzePrescription(file);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze prescription image.");
    } finally {
      setLoading(false);
    }
  };

  const handleTextAnalyze = async () => {
    if (!textInput.trim()) {
      setError("Please enter some prescription text.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.analyzePrescription(undefined, textInput);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze prescription text.");
    } finally {
      setLoading(false);
    }
  };

  const medicineNames = result?.medicines_found?.map(m => `${m.medicine} (${m.active_salt}, ${m.confidence}%)`) || [];

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Prescription Analyzer</h2>
        <p className="text-sm text-muted-foreground mt-1">Upload a prescription image or paste text to extract medicine names via OCR</p>
      </div>

      <Tabs defaultValue="image" className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="image" className="flex items-center gap-2">
            <Upload className="h-4 w-4" /> Image Upload
          </TabsTrigger>
          <TabsTrigger value="text" className="flex items-center gap-2">
            <Type className="h-4 w-4" /> Text Input
          </TabsTrigger>
        </TabsList>

        <TabsContent value="image">
          <div className="glass-card p-6 space-y-4">
            <label className="flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary/50 transition-colors">
              <Upload className="h-10 w-10 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{file ? file.name : "Click to upload prescription image"}</span>
              <input type="file" accept="image/*" className="hidden" onChange={e => setFile(e.target.files?.[0] || null)} />
            </label>

            <Button onClick={handleImageAnalyze} disabled={!file || loading} className="w-full">
              <FileSearch className="h-4 w-4 mr-2" />
              Analyze Prescription
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="text">
          <div className="glass-card p-6 space-y-4">
            <Textarea
              value={textInput}
              onChange={e => setTextInput(e.target.value)}
              rows={5}
              placeholder="Paste prescription text here, e.g.&#10;Take Paracetamol 500mg twice daily.&#10;Amoxicillin 250mg thrice daily."
              className="bg-background/50 text-foreground placeholder:text-muted-foreground/60"
            />
            <Button onClick={handleTextAnalyze} disabled={loading} className="w-full">
              <FileSearch className="h-4 w-4 mr-2" />
              Extract Medicines from Text
            </Button>
          </div>
        </TabsContent>
      </Tabs>

      {loading && <LoadingSpinner />}
      {error && <AlertBanner severity="MEDIUM" message={error} />}

      {result && result.raw_text && (
        <div className="glass-card p-5 space-y-2">
          <h3 className="font-semibold text-sm text-foreground">Extracted Text</h3>
          <pre className="text-xs text-muted-foreground bg-background/50 p-3 rounded-lg whitespace-pre-wrap">{result.raw_text}</pre>
        </div>
      )}

      {medicineNames.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-semibold text-sm text-foreground">Medicines Found ({medicineNames.length})</h3>
          <MedicineList medicines={medicineNames} />
        </div>
      )}
    </div>
  );
}
