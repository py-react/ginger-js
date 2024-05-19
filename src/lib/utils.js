const { clsx } = require("clsx");
const { twMerge } = require("tailwind-merge");

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
