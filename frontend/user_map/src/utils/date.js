export function formatDate(date) {
  return date.toISOString().split("T")[0];
}

export function addDays(date, days) {

  const copy = new Date(date);

  copy.setDate(copy.getDate() + days);

  return copy;
}