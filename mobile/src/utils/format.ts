// Matches the web app's existing (unembellished) formatting exactly --
// e.g. no thousands-separator grouping on fees. This is a straight port,
// not an enhancement; nicer number formatting is a separate decision.

export function formatPackage(value: number | null | undefined): string {
  return value != null ? `${value} LPA` : "—";
}

export function formatFees(value: number | null | undefined): string {
  return value != null ? `₹${value}` : "—";
}

export function formatPercentage(value: number | null | undefined): string {
  return value != null ? `${value}%` : "—";
}
