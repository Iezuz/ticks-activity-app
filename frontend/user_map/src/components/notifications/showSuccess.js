import { notifications } from "@mantine/notifications";

export function showSuccess(message) {

  console.log(message);

  notifications.show({
    color: "green",
    title: "Успешно",
    message,
  });
}