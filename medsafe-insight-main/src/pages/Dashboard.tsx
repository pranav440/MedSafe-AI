import { Heart, Droplets, Gauge, Brain, ShieldAlert } from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { VitalsChart } from "@/components/VitalsChart";
import { AlertBanner } from "@/components/AlertBanner";
import { RightPanel } from "@/components/RightPanel";
import { useVitalsData } from "@/hooks/useMockData";
import { LoadingSpinner } from "@/components/LoadingSpinner";

export default function Dashboard() {
  const { vitals, history, loading, error } = useVitalsData();

  if (loading) return <LoadingSpinner />;

  return (
    <div className="flex gap-6">
      {/* Main Content */}
      <div className="flex-1 min-w-0 space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-1">Real-time patient monitoring overview</p>
        </div>

        {error && (
          <AlertBanner severity="MEDIUM" message={error} />
        )}

        {vitals.severity === "HIGH" && (
          <AlertBanner severity="HIGH" message="Critical anomaly detected — immediate review recommended." />
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard title="Heart Rate" value={`${vitals.heart_rate} bpm`} icon={Heart} subtitle="Normal range: 60-100" />
          <MetricCard title="Oxygen Level" value={`${vitals.oxygen_level}%`} icon={Droplets} subtitle="Normal: >95%" />
          <MetricCard title="Blood Pressure" value={vitals.blood_pressure} icon={Gauge} subtitle="mmHg" />
          <MetricCard title="Anomaly Score" value={vitals.anomaly_score.toFixed(2)} icon={Brain} severity={vitals.severity} />
          <MetricCard title="Severity" value={vitals.severity} icon={ShieldAlert} severity={vitals.severity} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <VitalsChart data={history} dataKey="heart_rate" title="Heart Rate Trend" color="hsl(0, 72%, 55%)" />
          <VitalsChart data={history} dataKey="oxygen_level" title="Oxygen Level Trend" color="hsl(210, 80%, 55%)" />
          <VitalsChart data={history} dataKey="anomaly_score" title="Anomaly Score Trend" color="hsl(25, 95%, 55%)" />
        </div>
      </div>

      {/* Right Panel */}
      <RightPanel />
    </div>
  );
}
