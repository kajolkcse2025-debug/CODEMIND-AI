import { X } from "lucide-react";
import { useState } from "react";
import type { KeyboardEvent } from "react";

import { Input } from "@/components/ui/input";

interface TagInputProps {
  id: string;
  value: string[];
  onChange: (value: string[]) => void;
  max?: number;
  placeholder?: string;
  "aria-describedby"?: string | undefined;
  "aria-invalid"?: true | undefined;
}

/** Type a skill and press Enter or comma. Backspace on an empty field removes the last one. */
export function TagInput({ id, value, onChange, max = 30, placeholder, ...aria }: TagInputProps) {
  const [draft, setDraft] = useState("");

  function commit(raw: string) {
    const next = raw.trim();
    if (!next) return;
    if (value.length >= max) return;
    if (value.some((tag) => tag.toLowerCase() === next.toLowerCase())) {
      setDraft("");
      return;
    }
    onChange([...value, next]);
    setDraft("");
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter" || event.key === ",") {
      event.preventDefault();
      commit(draft);
    } else if (event.key === "Backspace" && draft === "" && value.length > 0) {
      onChange(value.slice(0, -1));
    }
  }

  return (
    <div>
      {value.length > 0 ? (
        <ul className="mb-2 flex flex-wrap gap-1.5" aria-label="Your skills">
          {value.map((tag) => (
            <li
              key={tag}
              className="inline-flex items-center gap-1 rounded-sm bg-accent py-0.5 pl-2 pr-1 text-xs text-accent-foreground"
            >
              {tag}
              <button
                type="button"
                className="rounded-sm p-0.5 hover:bg-background/40"
                aria-label={`Remove ${tag}`}
                onClick={() => onChange(value.filter((item) => item !== tag))}
              >
                <X className="size-3" />
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <Input
        id={id}
        value={draft}
        placeholder={placeholder}
        disabled={value.length >= max}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={onKeyDown}
        onBlur={() => commit(draft)}
        {...aria}
      />
    </div>
  );
}
