export type PaidHow = "transfer" | "giftcards" | "card" | "unsure";

/** Everything the intake wizard collects. Keys match step ids. */
export interface Answers {
  paid?: boolean;
  paidHow?: PaidHow;
  remote?: boolean;
  secrets?: boolean;
  phone?: string;
  name?: string;
  email?: string;
}

export type Risk = "safe" | "suspicious" | "known_scam";

export interface PhoneLookupResult {
  number: string; // normalized, e.g. +18005550199
  risk: Risk;
  reports: number;
  reason: string; // plain-language sentence
  source: "demo" | "live";
}

export interface ScamEmail {
  id: string;
  from: string;
  subject: string;
  date: string;
  snippet: string;
}

export interface Action {
  id: string;
  title: string;
  body: string;
  call?: { label: string; number: string };
  link?: { label: string; href: string };
}
