import { notifications } from "@mantine/notifications";

export function showError(message) {

  console.error(message);

  notifications.show({
    color: "red",
    title: "Ошибка",
    message,
  });
}