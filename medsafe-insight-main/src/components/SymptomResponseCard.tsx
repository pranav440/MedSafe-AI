import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SymptomResponseCardProps {
  title: string;
  items: string[];
  icon: LucideIcon;
  accentColor?: string;
}

export function SymptomResponseCard({ title, items, icon: Icon, accentColor = "text-primary" }: SymptomResponseCardProps) {
  if (!items.length) return null;
  return (
    <div className="glass-card p-5 animate-slide-in">
      <div className="flex items-center gap-2 mb-3">
        <Icon className={cn("h-5 w-5", accentColor)} />
        <h3 className="font-semibold text-sm text-card-foreground">{title}</h3>
      </div>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
            <span className={cn("mt-1.5 h-1.5 w-1.5 rounded-full shrink-0 bg-current", accentColor)} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
