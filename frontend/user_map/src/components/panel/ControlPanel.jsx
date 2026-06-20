import {
  Paper,
  Stack,
  Select,
  Button,
  Text,
} from "@mantine/core";

export default function ControlPanel({
  regions,
  selectedRegionId,
  onRegionChange,

  activityDate,
  onActivityDateChange,

  bitesStartDate,
  bitesEndDate,

  onBitesStartDateChange,
  onBitesEndDateChange,

  bitesVisible,
  onToggleBites,

  bitesMode,
  onBitesModeChange,
}) {

  return (
    <Paper
      shadow="md"
      p="md"
      style={{
        position: "absolute",
        zIndex: 1000,
        top: 20,
        left: 20,
        width: 360,
      }}
    >

      <Stack>

        <Text fw={700}>
          Карта активности клещей
        </Text>

        <Select
          label="Регион"
          data={regions.map((r) => ({
            value: String(r.id),
            label: r.name,
          }))}
          value={selectedRegionId}
          onChange={onRegionChange}
        />

        <div>
          <Text size="sm" mb={4}>
            Дата активности
          </Text>

          <input
            type="date"
            value={activityDate}
            onChange={(e) =>
              onActivityDateChange(
                e.target.value
              )
            }
            style={{
              width: "100%",
              padding: "8px",
            }}
          />
        </div>

        <Text fw={600}>
          Исторические укусы
        </Text>

        <div>
          <Text size="sm" mb={4}>
            Начальная дата
          </Text>

          <input
            type="date"
            value={bitesStartDate}
            onChange={(e) =>
              onBitesStartDateChange(
                e.target.value
              )
            }
            style={{
              width: "100%",
              padding: "8px",
            }}
          />
        </div>

        <div>
          <Text size="sm" mb={4}>
            Конечная дата
          </Text>

          <input
            type="date"
            value={bitesEndDate}
            onChange={(e) =>
              onBitesEndDateChange(
                e.target.value
              )
            }
            style={{
              width: "100%",
              padding: "8px",
            }}
          />
        </div>

        <Select
          label="Режим отображения"
          data={[
            {
              value: "clusters",
              label: "Кластеры",
            },
            {
              value: "heatmap",
              label: "Heatmap",
            },
          ]}
          value={bitesMode}
          onChange={onBitesModeChange}
        />

        <Button
          variant={
            bitesVisible
              ? "filled"
              : "light"
          }
          onClick={onToggleBites}
        >
          {
            bitesVisible
              ? "Скрыть укусы"
              : "Показать укусы"
          }
        </Button>

      </Stack>

    </Paper>
  );
}