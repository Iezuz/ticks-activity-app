import React from "react";
import ReactDOM from "react-dom/client";

import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";

import { BrowserRouter } from "react-router-dom";

import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import "leaflet/dist/leaflet.css";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";


import App from "./App";

import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <MantineProvider>
        <Notifications />
        <App />
      </MantineProvider>
    </BrowserRouter>
  </React.StrictMode>
);