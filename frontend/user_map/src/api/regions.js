import { api } from "./client";

export async function fetchRegions() {

  console.log("FETCH REGIONS");

  const res = await api.get("/regions");

  return res.data;
}

export async function fetchRegion(id) {

  console.log("FETCH REGION", id);

  const res = await api.get(`/regions/${id}`);

  return res.data;
}