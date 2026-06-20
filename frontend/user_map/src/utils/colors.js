export function getClusterColor(value) {

  if (value === null || value === undefined) {
    return "#cccccc";
  }

  if (value <= 0) {
    return "#ffe5e5";
  }

  if (value < 3) {
    return "#ffb3b3";
  }

  if (value < 6) {
    return "#ff8080";
  }

  if (value < 10) {
    return "#ff4d4d";
  }

  if (value < 20) {
    return "#ff1a1a";
  }

  return "#cc0000";
}