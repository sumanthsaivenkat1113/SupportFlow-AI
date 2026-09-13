import {
  Database,
  Users,
  Zap,
} from "lucide-react";

import ValueItem from "./ValueItem";

export default function ValueStrip() {
  return (
    <section className="border-y border-[#1D2942] bg-[#080D1C]/60">
      <div className="mx-auto grid max-w-7xl grid-cols-1 divide-y divide-[#1D2942] px-5 sm:grid-cols-3 sm:divide-x sm:divide-y-0 lg:px-8">

        <ValueItem
          icon={<Zap className="h-4 w-4" />}
          title="Automate repetitive work"
          text="Resolve common requests without manual handling."
        />

        <ValueItem
          icon={<Database className="h-4 w-4" />}
          title="Use your own knowledge"
          text="Ground responses in the documents your team provides."
        />

        <ValueItem
          icon={<Users className="h-4 w-4" />}
          title="Keep humans in control"
          text="Route uncertain tickets to human review."
        />

      </div>
    </section>
  );
}