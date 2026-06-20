import { Alert } from "@mantine/core";

export default function NotificationBlock({
  text,
}) {

  if (!text) {
    return null;
  }

  return (
    <Alert mb="md">
      {text}
    </Alert>
  );
}