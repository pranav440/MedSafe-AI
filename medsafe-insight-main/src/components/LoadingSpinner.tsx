import { cn } from "@/lib/utils";

export function LoadingSpinner({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center justify-center py-12", className)}>
      <div className="relative h-10 w-10">
        <div className="absolute inset-0 rounded-full border-2 border-muted" />
        <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </div>
    </div>
  );
}
