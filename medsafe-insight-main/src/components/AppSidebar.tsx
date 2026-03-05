import { LayoutDashboard, Activity, FileSearch, FlaskConical, Stethoscope, FileWarning, ShieldPlus } from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

const items = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Vitals Monitor", url: "/vitals", icon: Activity },
  { title: "Prescription Analyzer", url: "/prescription", icon: FileSearch },
  { title: "Drug Interactions", url: "/interactions", icon: FlaskConical },
  { title: "Symptom Guidance", url: "/symptoms", icon: Stethoscope },
  { title: "Side Effect Reporter", url: "/side-effects", icon: FileWarning },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();

  return (
    <Sidebar collapsible="icon">
      <SidebarContent className="pt-4">
        <div className={`px-4 mb-6 flex items-center gap-2.5 ${collapsed ? 'justify-center px-2' : ''}`}>
          <div className="p-1.5 rounded-lg bg-primary/10">
            <ShieldPlus className="h-6 w-6 text-primary" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="font-bold text-base tracking-tight text-foreground">MedSafe AI</h1>
              <p className="text-[10px] text-muted-foreground leading-none">Safety Assistant</p>
            </div>
          )}
        </div>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink
                      to={item.url}
                      end={item.url === "/"}
                      className="hover:bg-muted/50 transition-colors"
                      activeClassName="bg-primary/10 text-primary font-medium"
                    >
                      <item.icon className="mr-2 h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
