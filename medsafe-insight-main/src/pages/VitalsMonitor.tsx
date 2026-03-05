import { useEffect } from "react";
import { Heart, Droplets, Gauge, ShieldAlert } from "lucide-react";
import { MetricCard } from "@/components/MetricCard";
import { VitalsChart } from "@/components/VitalsChart";
import { AlertBanner } from "@/components/AlertBanner";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { useVitalsData } from "@/hooks/useMockData";

export default function VitalsMonitor() {
  const { vitals, history, loading, error, refresh } = useVitalsData();

  useEffect(() => {
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, [refresh]);

  if (loading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Real-Time Vitals Monitor</h2>
        <p className="text-sm text-muted-foreground mt-1">Live vitals updating every 5 seconds</p>
      </div>

      {error && <AlertBanner severity="MEDIUM" message={error} />}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Heart Rate" value={`${vitals.heart_rate} bpm`} icon={Heart} />
        <MetricCard title="Oxygen Level" value={`${vitals.oxygen_level}%`} icon={Droplets} />
        <MetricCard title="Blood Pressure" value={vitals.blood_pressure} icon={Gauge} />
        <MetricCard title="Severity" value={vitals.severity} icon={ShieldAlert} severity={vitals.severity} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <VitalsChart data={history} dataKey="heart_rate" title="Heart Rate (Live)" color="hsl(0, 72%, 55%)" />
        <VitalsChart data={history} dataKey="oxygen_level" title="Oxygen Level (Live)" color="hsl(210, 80%, 55%)" />
      </div>
    </div>
  );
}
