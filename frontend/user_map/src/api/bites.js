import { api } from "./client";

export async function fetchBites({
  regionId,
  startDate,
  endDate,
}) {

  console.log("FETCH BITES", {
    regionId,
    startDate,
    endDate,
  });

  const res = await api.get("/bites", {
    params: {
      region_id: regionId,
      start_date: startDate,
      end_date: endDate,
    },
  });

  return res.data;
}