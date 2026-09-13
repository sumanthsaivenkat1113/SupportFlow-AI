import Eyebrow from "./Eyebrow";

interface SectionHeadingProps {
  eyebrow: string;
  title: string;
  description: string;
}

export default function SectionHeading({
  eyebrow,
  title,
  description,
}: SectionHeadingProps) {
  return (
    <div className="max-w-2xl">
      <Eyebrow>{eyebrow}</Eyebrow>

      <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] text-white sm:text-4xl">
        {title}
      </h2>

      <p className="mt-5 leading-7 text-[#A8B3CF]">
        {description}
      </p>
    </div>
  );
}