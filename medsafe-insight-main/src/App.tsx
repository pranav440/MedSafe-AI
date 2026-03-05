import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { TopBar } from "@/components/TopBar";
import { RefreshProvider } from "@/hooks/useRefresh";
import Index from "./pages/Index";
import VitalsMonitor from "./pages/VitalsMonitor";
import PrescriptionAnalyzer from "./pages/PrescriptionAnalyzer";
import DrugInteractions from "./pages/DrugInteractions";
import SymptomGuidance from "./pages/SymptomGuidance";
import SideEffectReporter from "./pages/SideEffectReporter";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <RefreshProvider>
          <SidebarProvider>
            <div className="min-h-screen flex w-full dark">
              <AppSidebar />
              <div className="flex-1 flex flex-col">
                <TopBar />
                <main className="flex-1 p-6">
                  <Routes>
                    <Route path="/" element={<Index />} />
                    <Route path="/vitals" element={<VitalsMonitor />} />
                    <Route path="/prescription" element={<PrescriptionAnalyzer />} />
                    <Route path="/interactions" element={<DrugInteractions />} />
                    <Route path="/symptoms" element={<SymptomGuidance />} />
                    <Route path="/side-effects" element={<SideEffectReporter />} />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </main>
              </div>
            </div>
          </SidebarProvider>
        </RefreshProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
