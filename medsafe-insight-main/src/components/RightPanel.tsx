import { Bell, Clock, TrendingUp, Users, AlertTriangle, CheckCircle, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface Alert {
  id: number;
  message: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  time: string;
}

const recentAlerts: Alert[] = [
  { id: 1, message: "Heart rate spike detected (112 bpm)", severity: "HIGH", time: "2m ago" },
  { id: 2, message: "Oxygen level dropped to 93%", severity: "MEDIUM", time: "8m ago" },
  { id: 3, message: "Blood pressure normalized", severity: "LOW", time: "15m ago" },
  { id: 4, message: "Anomaly score elevated (0.72)", severity: "HIGH", time: "22m ago" },
  { id: 5, message: "Vitals within normal range", severity: "LOW", time: "30m ago" },
];

const activityLog = [
  { action: "Prescription analyzed", detail: "3 medicines extracted", time: "5m ago", icon: CheckCircle },
  { action: "Drug interaction check", detail: "Warfarin + Aspirin flagged", time: "12m ago", icon: AlertTriangle },
  { action: "Side effect reported", detail: "Ibuprofen — nausea", time: "25m ago", icon: Activity },
  { action: "Symptom guidance", detail: "Fever, headache query", time: "40m ago", icon: TrendingUp },
];

const severityIcon = {
  LOW: CheckCircle,
  MEDIUM: Bell,
  HIGH: AlertTriangle,
};

const severityDot = {
  LOW: "bg-severity-low",
  MEDIUM: "bg-severity-medium",
  HIGH: "bg-severity-high",
};

export function RightPanel() {
  return (
    <div className="w-80 shrink-0 space-y-5 hidden xl:block">
      {/* Quick Stats */}
      <div className="glass-card p-5 space-y-4">
        <h3 className="text-sm font-semibold text-card-foreground flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-primary" />
          Quick Stats
        </h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: "Readings Today", value: "148", color: "text-chart-blue" },
            { label: "Alerts Triggered", value: "12", color: "text-chart-orange" },
            { label: "High Severity", value: "3", color: "text-chart-red" },
            { label: "Reports Filed", value: "7", color: "text-chart-teal" },
          ].map((stat) => (
            <div key={stat.label} className="bg-muted/50 rounded-lg p-3 text-center">
              <p className={cn("text-xl font-bold", stat.color)}>{stat.value}</p>
              <p className="text-[10px] text-muted-foreground mt-0.5">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="glass-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-card-foreground flex items-center gap-2">
          <Bell className="h-4 w-4 text-severity-medium" />
          Recent Alerts
        </h3>
        <div className="space-y-2.5 max-h-[260px] overflow-y-auto pr-1 scrollbar-thin">
          {recentAlerts.map((alert) => {
            const Icon = severityIcon[alert.severity];
            return (
              <div
                key={alert.id}
                className="flex items-start gap-2.5 p-2.5 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors cursor-default animate-slide-in"
              >
                <div className={cn("mt-0.5 h-2 w-2 rounded-full shrink-0", severityDot[alert.severity])} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium leading-snug truncate text-card-foreground">{alert.message}</p>
                  <p className="text-[10px] text-muted-foreground mt-0.5 flex items-center gap-1">
                    <Clock className="h-2.5 w-2.5" />
                    {alert.time}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Activity Feed */}
      <div className="glass-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-card-foreground flex items-center gap-2">
          <Activity className="h-4 w-4 text-accent" />
          Activity Feed
        </h3>
        <div className="space-y-3">
          {activityLog.map((item, i) => (
            <div key={i} className="flex items-start gap-3 animate-slide-in" style={{ animationDelay: `${i * 60}ms` }}>
              <div className="p-1.5 rounded-md bg-primary/10 text-primary mt-0.5">
                <item.icon className="h-3 w-3" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-card-foreground">{item.action}</p>
                <p className="text-[10px] text-muted-foreground">{item.detail}</p>
              </div>
              <span className="text-[10px] text-muted-foreground shrink-0 mt-0.5">{item.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="glass-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-card-foreground flex items-center gap-2">
          <Users className="h-4 w-4 text-chart-teal" />
          System Status
        </h3>
        <div className="space-y-2">
          {[
            { name: "Vitals Engine", status: "Operational", ok: true },
            { name: "AI Anomaly Model", status: "Operational", ok: true },
            { name: "OCR Service", status: "Operational", ok: true },
            { name: "Drug DB", status: "Syncing", ok: false },
          ].map((s) => (
            <div key={s.name} className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{s.name}</span>
              <span className={cn("flex items-center gap-1.5 font-medium", s.ok ? "text-severity-low" : "text-severity-medium")}>
                <span className={cn("h-1.5 w-1.5 rounded-full", s.ok ? "bg-severity-low animate-pulse-glow" : "bg-severity-medium")} />
                {s.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
