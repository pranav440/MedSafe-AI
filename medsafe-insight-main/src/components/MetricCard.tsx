import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  severity?: "LOW" | "MEDIUM" | "HIGH";
  trend?: "up" | "down" | "stable";
  className?: string;
}

export function MetricCard({ title, value, icon: Icon, subtitle, severity, className }: MetricCardProps) {
  const severityColors = {
    LOW: "border-severity-low/30 shadow-[0_0_15px_hsl(var(--severity-low)/0.1)]",
    MEDIUM: "border-severity-medium/30 shadow-[0_0_15px_hsl(var(--severity-medium)/0.1)]",
    HIGH: "border-severity-high/30 shadow-[0_0_15px_hsl(var(--severity-high)/0.1)]",
  };

  const iconColors = {
    LOW: "text-severity-low bg-severity-low/10",
    MEDIUM: "text-severity-medium bg-severity-medium/10",
    HIGH: "text-severity-high bg-severity-high/10",
  };

  return (
    <div className={cn(
      "glass-card p-5 transition-all duration-300 hover:scale-[1.02] animate-slide-in",
      severity ? severityColors[severity] : "glow-blue",
      className
    )}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground font-medium">{title}</p>
          <p className="text-2xl font-bold tracking-tight text-card-foreground">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        <div className={cn(
          "p-2.5 rounded-lg",
          severity ? iconColors[severity] : "text-primary bg-primary/10"
        )}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
      {severity && (
        <div className="mt-3 flex items-center gap-2">
          <span className={cn(
            "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border",
            severity === "LOW" && "severity-low",
            severity === "MEDIUM" && "severity-medium",
            severity === "HIGH" && "severity-high",
          )}>
            {severity}
          </span>
        </div>
      )}
    </div>
  );
}
