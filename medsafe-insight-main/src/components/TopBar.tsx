import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useRefresh } from "@/hooks/useRefresh";
import { useState } from "react";

export function TopBar() {
  const { triggerRefresh } = useRefresh();
  const [spinning, setSpinning] = useState(false);

  const handleRefresh = () => {
    setSpinning(true);
    triggerRefresh();
    setTimeout(() => setSpinning(false), 700);
  };

  return (
    <header className="h-14 flex items-center justify-between border-b border-border/50 px-4 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <SidebarTrigger />
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-severity-low animate-pulse-glow" />
          <span className="text-xs text-muted-foreground font-medium">System Online (v7.0-Stable)</span>
        </div>
      </div>
      <Button variant="ghost" size="sm" onClick={handleRefresh} className="text-muted-foreground hover:text-foreground">
        <RefreshCw className={`h-4 w-4 mr-1.5 transition-transform ${spinning ? "animate-spin" : ""}`} />
        Refresh
      </Button>
    </header>
  );
}
