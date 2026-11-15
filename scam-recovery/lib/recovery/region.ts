/**
 * Region-specific help lines. Defaults are for the United States.
 * To support another country, add another object and select it in plan.ts.
 * Verify numbers before launch; they can change.
 */
export interface Region {
  code: string;
  reportLine: { label: string; number: string };
  elderLine: { label: string; number: string };
  reportSite: { label: string; href: string };
}

export const US: Region = {
  code: "US",
  reportLine: { label: "Call the Federal Trade Commission", number: "18773824357" },
  elderLine: { label: "Call the Elder Fraud Hotline", number: "18333728311" },
  reportSite: { label: "Open the reporting website", href: "https://reportfraud.ftc.gov" },
};
