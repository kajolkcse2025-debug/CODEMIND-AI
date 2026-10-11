/** aria props to spread on the control inside a FormField. */
export function fieldAria(id: string, error: string | undefined, hasHint = false) {
  return {
    id,
    "aria-invalid": error ? (true as const) : undefined,
    "aria-describedby": error ? `${id}-error` : hasHint ? `${id}-hint` : undefined,
  };
}
