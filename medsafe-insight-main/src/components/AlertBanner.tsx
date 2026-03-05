import { AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface AlertBannerProps {
  severity: "LOW" | "MEDIUM" | "HIGH";
  message: string;
  className?: string;
}

export function AlertBanner({ severity, message, className }: AlertBannerProps) {
  const config = {
    LOW: { icon: CheckCircle, cls: "severity-low border" },
    MEDIUM: { icon: AlertCircle, cls: "severity-medium border" },
    HIGH: { icon: AlertTriangle, cls: "severity-high border animate-pulse-glow" },
  };
  const { icon: Icon, cls } = config[severity];

  return (
    <div className={cn("flex items-center gap-3 px-4 py-3 rounded-lg", cls, className)}>
      <Icon className="h-5 w-5 shrink-0" />
      <span className="text-sm font-medium">{message}</span>
    </div>
  );
}
