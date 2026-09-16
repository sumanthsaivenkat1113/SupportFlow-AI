import { MetricCard } from "./MetricCard";
import { MetricData } from "@/types/dashboard";

interface MetricsGridProps {
  metrics: MetricData[];
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric, idx) => (
        <MetricCard key={idx} {...metric} />
      ))}
    </div>
  );
}