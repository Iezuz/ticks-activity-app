import { useEffect, useState } from "react";

import ActivityMap from "../components/map/ActivityMap";

import ControlPanel from "../components/panel/ControlPanel";

import PageLoader from "../components/layout/PageLoader";

import {
  fetchRegions,
  fetchRegion,
} from "../api/regions";

import {
  fetchClusterActivity,
} from "../api/clusters";

import {
  fetchBites,
} from "../api/bites";

import {
  showError,
} from "../components/notifications/showError";

import {
  showSuccess,
} from "../components/notifications/showSuccess";

import {
  addDays,
  formatDate,
} from "../utils/date";

export default function MapPage() {

  const today =
    formatDate(new Date());

  const defaultStart =
    formatDate(
      addDays(
        new Date(),
        -30
      )
    );

  const [loading, setLoading] =
    useState(false);

  const [regions, setRegions] =
    useState([]);

  const [selectedRegionId,
    setSelectedRegionId] =
    useState(null);

  const [region, setRegion] =
    useState(null);

  const [activityClusters,
    setActivityClusters] =
    useState([]);

  const [bites, setBites] =
    useState([]);

  const [activityDate,
    setActivityDate] =
    useState(today);

  const [bitesStartDate,
    setBitesStartDate] =
    useState(defaultStart);

  const [bitesEndDate,
    setBitesEndDate] =
    useState(today);

  const [bitesVisible,
    setBitesVisible] =
    useState(false);

  const [bitesMode,
    setBitesMode] =
    useState("clusters");

  useEffect(() => {

    loadRegions();

  }, []);

  useEffect(() => {

    if (!selectedRegionId) {
      return;
    }

    loadRegion();

  }, [selectedRegionId]);

  useEffect(() => {

    if (!selectedRegionId) {
      return;
    }

    loadActivity();

  }, [
    selectedRegionId,
    activityDate,
  ]);

  async function loadRegions() {

    try {

      console.log(
        "LOAD REGIONS START"
      );

      setLoading(true);

      const data =
        await fetchRegions();

      console.log(
        "LOAD REGIONS SUCCESS",
        data
      );

      setRegions(data);

      if (data.length > 0) {

        setSelectedRegionId(
          String(data[0].id)
        );
      }

    } catch (e) {

      console.error(
        "LOAD REGIONS ERROR",
        e
      );

      showError(
        "Ошибка загрузки регионов"
      );

    } finally {

      setLoading(false);
    }
  }

  async function loadRegion() {

    try {

      console.log(
        "LOAD REGION START"
      );

      const data =
        await fetchRegion(
          selectedRegionId
        );

      console.log(
        "LOAD REGION SUCCESS",
        data
      );

      setRegion(data);

    } catch (e) {

      console.error(
        "LOAD REGION ERROR",
        e
      );

      showError(
        "Ошибка загрузки региона"
      );
    }
  }

  async function loadActivity() {

    try {

      console.log(
        "LOAD ACTIVITY START"
      );

      setLoading(true);

      const data =
        await fetchClusterActivity(
          selectedRegionId,
          activityDate
        );

      console.log(
        "LOAD ACTIVITY SUCCESS",
        data
      );

      setActivityClusters(data);

      showSuccess(
        `Активность за ${activityDate}`
      );

    } catch (e) {

      console.error(
        "LOAD ACTIVITY ERROR",
        e
      );

      showError(
        "Ошибка загрузки активности"
      );

    } finally {

      setLoading(false);
    }
  }

  async function toggleBites() {

    if (bitesVisible) {

      setBitesVisible(false);

      return;
    }

    try {

      console.log(
        "LOAD BITES START"
      );

      setLoading(true);

      const data =
        await fetchBites({
          regionId:
            selectedRegionId,

          startDate:
            bitesStartDate,

          endDate:
            bitesEndDate,
        });

      console.log(
        "LOAD BITES SUCCESS",
        data
      );

      setBites(data);

      setBitesVisible(true);

    } catch (e) {

      console.error(
        "LOAD BITES ERROR",
        e
      );

      showError(
        "Ошибка загрузки укусов"
      );

    } finally {

      setLoading(false);
    }
  }

  return (
    <>
      <PageLoader
        visible={loading}
      />

      <ControlPanel
        regions={regions}
        selectedRegionId={
          selectedRegionId
        }
        onRegionChange={
          setSelectedRegionId
        }

        activityDate={
          activityDate
        }
        onActivityDateChange={
          setActivityDate
        }

        bitesStartDate={
          bitesStartDate
        }
        bitesEndDate={
          bitesEndDate
        }

        onBitesStartDateChange={
          setBitesStartDate
        }

        onBitesEndDateChange={
          setBitesEndDate
        }

        bitesVisible={
          bitesVisible
        }

        onToggleBites={
          toggleBites
        }

        bitesMode={
          bitesMode
        }

        onBitesModeChange={
          setBitesMode
        }
      />

      <ActivityMap
        region={region}
        activityClusters={
          activityClusters
        }
        bites={bites}
        bitesVisible={
          bitesVisible
        }
        bitesMode={
          bitesMode
        }
      />
    </>
  );
}