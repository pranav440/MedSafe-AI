import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";

interface VitalsChartProps {
  data: Array<Record<string, any>>;
  dataKey: string;
  title: string;
  color?: string;
  type?: "line" | "area";
}

export function VitalsChart({ data, dataKey, title, color = "hsl(210, 80%, 55%)", type = "area" }: VitalsChartProps) {
  const Chart = type === "area" ? AreaChart : LineChart;

  return (
    <div className="glass-card p-5 animate-slide-in">
      <h3 className="text-sm font-semibold text-card-foreground mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <Chart data={data}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" stroke="currentColor" opacity={0.3} />
          <XAxis dataKey="time" className="fill-muted-foreground" tick={{ fontSize: 11, fill: "hsl(215, 15%, 60%)" }} stroke="hsl(215, 15%, 60%)" />
          <YAxis className="fill-muted-foreground" tick={{ fontSize: 11, fill: "hsl(215, 15%, 60%)" }} stroke="hsl(215, 15%, 60%)" />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              color: "hsl(var(--card-foreground))",
              fontSize: 12,
            }}
          />
          {type === "area" ? (
            <Area type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} fill={`url(#gradient-${dataKey})`} />
          ) : (
            <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
          )}
        </Chart>
      </ResponsiveContainer>
    </div>
  );
}
