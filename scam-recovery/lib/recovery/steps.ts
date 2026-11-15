import type { Answers } from "../types";

export interface Option {
  value: string;
  label: string;
}

export interface Step {
  id: keyof Answers;
  kind: "yesno" | "choice" | "text";
  title: string;
  help?: string;
  options?: Option[];
  inputType?: "text" | "tel" | "email";
  autoComplete?: string;
  placeholder?: string;
  optional?: boolean;
  showIf?: (a: Answers) => boolean;
  /** Return a calm, plain error message, or null when the value is fine. */
  validate?: (v: string) => string | null;
}

/** One question per screen. Order here is the order people see. */
export const STEPS: Step[] = [
  {
    id: "paid",
    kind: "yesno",
    title: "Did you give the caller any money, gift cards, or bank details?",
    help: "It is okay to say yes. We just want to help you in the right order.",
  },
  {
    id: "paidHow",
    kind: "choice",
    title: "How did you give it?",
    showIf: (a) => a.paid === true,
    options: [
      { value: "transfer", label: "I sent money from my bank" },
      { value: "giftcards", label: "I read out numbers from gift cards" },
      { value: "card", label: "I gave my card or bank details" },
      { value: "unsure", label: "I am not sure" },
    ],
  },
  {
    id: "remote",
    kind: "yesno",
    title: "Did you install anything, or let them control your phone or computer?",
    help: "For example, they may have asked you to download a program, or to press keys while on the phone.",
  },
  {
    id: "secrets",
    kind: "yesno",
    title: "Did you tell them a password, or a code that came by text?",
  },
  {
    id: "phone",
    kind: "text",
    title: "What phone number did they call from?",
    help: "Look at your phone's recent calls. If you cannot find it, press Skip.",
    inputType: "tel",
    autoComplete: "off",
    placeholder: "For example: 800 555 0199",
    optional: true,
    validate: (v) => (v.replace(/\D/g, "").length >= 7 ? null : "That number looks a little short. Please check it."),
  },
  {
    id: "name",
    kind: "text",
    title: "What is your first name?",
    help: "So we can talk to you properly. It stays on this device.",
    inputType: "text",
    autoComplete: "given-name",
    optional: true,
  },
  {
    id: "email",
    kind: "text",
    title: "What is your email address?",
    help: "Only if you want us to look for scam messages in your email later. You can skip this.",
    inputType: "email",
    autoComplete: "email",
    placeholder: "name@example.com",
    optional: true,
    validate: (v) => (/^\S+@\S+\.\S+$/.test(v) ? null : "That does not look like an email address yet. Please check it."),
  },
];

export function nextStepId(cur: keyof Answers, a: Answers): keyof Answers | null {
  const i = STEPS.findIndex((s) => s.id === cur);
  for (let j = i + 1; j < STEPS.length; j++) {
    const s = STEPS[j];
    if (!s.showIf || s.showIf(a)) return s.id;
  }
  return null;
}

export function prevStepId(cur: keyof Answers, a: Answers): keyof Answers | null {
  const i = STEPS.findIndex((s) => s.id === cur);
  for (let j = i - 1; j >= 0; j--) {
    const s = STEPS[j];
    if (!s.showIf || s.showIf(a)) return s.id;
  }
  return null;
}
