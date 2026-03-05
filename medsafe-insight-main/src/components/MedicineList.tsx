import { Pill } from "lucide-react";

interface MedicineListProps {
  medicines: string[];
}

export function MedicineList({ medicines }: MedicineListProps) {
  return (
    <div className="space-y-2">
      {medicines.map((med, i) => (
        <div key={i} className="flex items-center gap-3 glass-card p-3 animate-slide-in" style={{ animationDelay: `${i * 80}ms` }}>
          <div className="p-2 rounded-lg bg-accent/10 text-accent">
            <Pill className="h-4 w-4" />
          </div>
          <span className="font-medium text-sm">{med}</span>
        </div>
      ))}
    </div>
  );
}
