const REGION_API = "http://localhost:8000/regions";
const BITE_API = "http://localhost:8000/bites";
const CLUSTER_ACTIVITY_API = "http://localhost:8000/clusters";

let map = L.map('map');

L.tileLayer(
'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
).addTo(map);

let currentRegionId = null;

let bitesLayerVisible = false;

let currentMode = "clusters";

let clusterLayer = L.markerClusterGroup();
let clusterPolygonsLayer = L.layerGroup();
let heatLayer = null;



function getClusterColor(value){

    if(value === 0) return "#fd171700";
    if(value < 5) return "#fa0e0e52";
    if(value < 10) return "#ff0000ab";
    if(value < 20) return "#f70000";

    return "#d73027";
}



function setTodayDate(){

    const today = new Date().toISOString().split('T')[0];
    document.getElementById("activityDate").value = today;

}



async function loadRegions(){

    const res = await fetch(REGION_API);
    const regions = await res.json();

    const select = document.getElementById("regionSelect");

    regions.forEach(r=>{

        const option = document.createElement("option");
        option.value = r.id;
        option.textContent = r.name;

        select.appendChild(option);

    });

    if(regions.length>0){

        currentRegionId = regions[0].id;
        select.value = currentRegionId;

        await loadRegion(currentRegionId);
        await loadClusterPolygons();

    }

}



async function loadRegion(regionId){

    currentRegionId = regionId;

    const res = await fetch(`${REGION_API}/${regionId}`);
    const region = await res.json();

    const tempLayer = L.geoJSON(region.boundary);
    const bounds = tempLayer.getBounds();

    map.fitBounds(bounds,{padding:[20,20]});

}



async function loadClusters(){

    if(!currentRegionId) return;

    const start = document.getElementById("dateStart").value;
    const end = document.getElementById("dateEnd").value;

    let url = `${BITE_API}?region_id=${currentRegionId}`;

    if(start) url += `&start_date=${start}`;
    if(end) url += `&end_date=${end}`;

    const res = await fetch(url);
    const bites = await res.json();

    clusterLayer.clearLayers();

    if(heatLayer){
        map.removeLayer(heatLayer);
    }

    let heatData = [];

    bites.forEach(bite=>{

        const coords = bite.point_of_bite.coordinates;

        const lat = coords[1];
        const lng = coords[0];

        const marker = L.marker([lat,lng]);

        clusterLayer.addLayer(marker);

        heatData.push([lat,lng,1]);

    });

    heatLayer = L.heatLayer(
        heatData,
        {
            radius:40,
            blur:20,
            maxZoom:17
        }
    );

}



async function loadClusterPolygons(){

    if(!currentRegionId) return;

    const date = document.getElementById("activityDate").value;

    if(!date) return;

    const url = `${CLUSTER_ACTIVITY_API}/region/${currentRegionId}/activity?date_par=${date}`;

    const res = await fetch(url);
    const clusters = await res.json();

    clusterPolygonsLayer.clearLayers();

    if(clusters.length === 0){
        showNotification("Нет данных активности за выбранную дату");
        return;
    }

    clusters.forEach(c=>{

        const geometry = JSON.parse(c.geometry);

        const layer = L.geoJSON(
            geometry,
            {
                style:{
                    color:"#333",
                    weight:0,
                    fillColor:getClusterColor(c.amount),
                    fillOpacity:0.6
                }
            }
        );

        layer.bindPopup(`Количество укусов: ${c.amount}`);

        clusterPolygonsLayer.addLayer(layer);

    });

}



function updateBiteLayers(){

    map.removeLayer(clusterLayer);

    if(heatLayer){
        map.removeLayer(heatLayer);
    }

    if(!bitesLayerVisible) return;

    if(currentMode==="clusters"){
        map.addLayer(clusterLayer);
    }

    if(currentMode==="heatmap"){
        map.addLayer(heatLayer);
    }

}



function showNotification(text){

    const box = document.getElementById("notification");
    box.textContent = text;
    box.style.display = "block";

    setTimeout(()=>{
        box.style.display = "none";
    },4000);

}



document
.getElementById("applyFilter")
.addEventListener("click", async ()=>{

    if(bitesLayerVisible){

        map.removeLayer(clusterLayer);

        if(heatLayer){
            map.removeLayer(heatLayer);
        }

        bitesLayerVisible=false;

        document
        .getElementById("applyFilter")
        .textContent="Показать";

    } else {

        await loadClusters();

        bitesLayerVisible=true;

        updateBiteLayers();

        document
        .getElementById("applyFilter")
        .textContent="Скрыть";

    }

});



document
.getElementById("viewMode")
.addEventListener("change",e=>{

    currentMode=e.target.value;

    updateBiteLayers();

});



document
.getElementById("regionSelect")
.addEventListener("change",async e=>{

    await loadRegion(e.target.value);

    clusterLayer.clearLayers();
    clusterPolygonsLayer.clearLayers();

    if(heatLayer){
        map.removeLayer(heatLayer);
    }

    bitesLayerVisible=false;

    document
    .getElementById("applyFilter")
    .textContent="Показать";

    await loadClusterPolygons();

});



document
.getElementById("activityDate")
.addEventListener("change", async ()=>{

    await loadClusterPolygons();

});



setTodayDate();

map.addLayer(clusterPolygonsLayer);

loadRegions();