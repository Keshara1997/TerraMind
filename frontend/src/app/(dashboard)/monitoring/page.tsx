import { Activity } from "lucide-react";

import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function MonitoringPage() {
  return (
    <PlaceholderPage
      title="Environmental monitoring"
      description="Thresholds, alerts, and scheduled monitoring rules."
      icon={Activity}
    />
  );
}