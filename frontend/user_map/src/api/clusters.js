import { api } from "./client";

export async function fetchClusterActivity(regionId, date) {

  console.log("FETCH CLUSTER ACTIVITY", regionId, date);

  const res = await api.get(
    `/clusters/region/${regionId}/activity`,
    {
      params: {
        date_par: date,
      },
    }
  );

  return res.data;
}