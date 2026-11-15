import type { Action, Answers } from "../types";
import { US, type Region } from "./region";

/**
 * Builds the ordered "What to do right now" list from the intake answers.
 * Pure function: no I/O, easy to test. Most urgent actions come first.
 */
export function buildPlan(a: Answers, region: Region = US): Action[] {
  const plan: Action[] = [];

  // 1. Money (most time-sensitive)
  if (a.paid) {
    if (a.paidHow === "giftcards") {
      plan.push({
        id: "giftcards",
        title: "Keep your gift cards and the receipt",
        body:
          "Find the gift cards and the store receipt. Call the phone number on the back of the card. Tell them: \"I was scammed. Please freeze this card.\" The sooner you call, the better the chance of getting money back.",
      });
    } else {
      plan.push({
        id: "bank",
        title: "Call your bank right now",
        body:
          "Use the phone number on the back of your bank card. Tell them: \"I was scammed. Please stop any payments and protect my account.\" Ask them to watch your account and replace your card if needed.",
      });
    }
  }

  // 2. Caller still has access to the device
  if (a.remote) {
    plan.push({
      id: "disconnect",
      title: "Cut the caller off",
      body:
        "Turn off your Wi-Fi, or unplug the internet cable. Then switch off the computer or phone. This stops the caller from seeing or using it.",
    });
    plan.push({
      id: "cleanup",
      title: "Get the device checked",
      body:
        "Ask someone you trust, or a local repair shop, to remove anything the caller put on it. Please do not use online banking on that device until it has been checked.",
    });
  }

  // 3. Passwords / codes
  if (a.secrets) {
    plan.push({
      id: "passwords",
      title: "Change your email password",
      body:
        "Use a different device if the caller had control of yours. Pick a new password you have never used before. Your email comes first, because other accounts can be reset from it. Then change your bank password.",
    });
  }

  // 4. Always
  const who = a.phone ? `the number ${a.phone}` : "that number";
  plan.push({
    id: "no-contact",
    title: "Do not answer or call back",
    body: `If ${who} calls again, hang up. Do not give them anything else, even if they sound kind or say they can fix it.`,
  });

  plan.push({
    id: "tell-someone",
    title: "Tell someone you trust",
    body:
      "Call a family member, friend or neighbour. Scams happen to smart, careful people. It is not your fault, and you do not have to handle this alone.",
  });

  plan.push({
    id: "report",
    title: "Report the scam",
    body:
      "Reporting helps stop the scammers and may help you get money back. Have the date, the phone number and what you gave them.",
    call: region.reportLine,
    link: region.reportSite,
  });

  plan.push({
    id: "elder-line",
    title: "Talk to someone who can help",
    body: "Trained people can walk you through what to do next. The call is free.",
    call: region.elderLine,
  });

  plan.push({
    id: "refund-warning",
    title: "Be careful of \"refund\" calls",
    body:
      "Scammers often call again pretending to help you get your money back. They will ask for a fee. Hang up. Real helpers never ask for money.",
  });

  if (a.email) {
    plan.push({
      id: "email-check",
      title: "Look for messages from the scammer",
      body: "We can look through your email for messages that look connected to this scam.",
      link: { label: "Check my email", href: "/email-check" },
    });
  }

  plan.push({
    id: "link-number",
    title: "Get a warning if this happens again",
    body: "If you link your phone number, we can let you know when new scam numbers are reported.",
    link: { label: "Link my phone number", href: "/my-number" },
  });

  return plan;
}
