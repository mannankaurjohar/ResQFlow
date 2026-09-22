import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { GisOverviewData } from '../types';
import api from '../services/api';
import { useApp } from '../context/AppContext';
import { Layers } from 'lucide-react';

interface GisMapProps {
  height?: string;
  onSelectRequest?: (req: any) => void;
  highlightLocation?: string;
}

export const GisMap: React.FC<GisMapProps> = ({
  height = '560px'
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupsRef = useRef<{
    [key: string]: L.LayerGroup;
  }>({});

  // Keeps track of the last set of locations used for
  // map fitting, so the map doesn't jump every 2 seconds.
  const fittedDataKeyRef = useRef<string>('');

  const [gisData, setGisData] =
    useState<GisOverviewData | null>(null);

  const [layers, setLayers] = useState({
    zones: true,
    requests: true,
    warehouses: true,
    reliefCenters: true,
    deliveries: true,
    blockedRoads: true
  });

  const {
    setActiveMatchModalRequest
  } = useApp();

  // ============================================================
  // LOAD / REFRESH GIS DATA
  // ============================================================

  useEffect(() => {
    let mounted = true;

    const loadGIS = async () => {
      try {
        const data = await api.getGisOverview();

        if (mounted) {
          setGisData(data);
        }
      } catch (error) {
        console.error(
          'Failed to load GIS data:',
          error
        );
      }
    };

    // Initial load
    loadGIS();

    // Refresh every 2 seconds so newly submitted requests,
    // flood escalation and delivery changes appear on the map.
    const refreshTimer =
      window.setInterval(
        loadGIS,
        2000
      );

    return () => {
      mounted = false;
      window.clearInterval(refreshTimer);
    };
  }, []);

  // ============================================================
  // INITIALIZE LEAFLET MAP
  // ============================================================

  useEffect(() => {
    if (
      !mapContainerRef.current ||
      mapInstanceRef.current
    ) {
      return;
    }

    const map = L.map(
      mapContainerRef.current,
      {
        center: [14.515, 75.315],
        zoom: 12,
        zoomControl: true
      }
    );

    // OpenStreetMap basemap.
    // This removes the previous CARTO API-key problem.
    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution:
          '&copy; OpenStreetMap contributors',
        maxZoom: 19
      }
    ).addTo(map);

    mapInstanceRef.current = map;

    // Create all GIS layer groups.
    layerGroupsRef.current = {
      zones: L.layerGroup().addTo(map),
      requests: L.layerGroup().addTo(map),
      warehouses: L.layerGroup().addTo(map),
      reliefCenters: L.layerGroup().addTo(map),
      deliveries: L.layerGroup().addTo(map),
      blockedRoads: L.layerGroup().addTo(map)
    };

    setTimeout(() => {
      map.invalidateSize();
    }, 300);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
      layerGroupsRef.current = {};
    };
  }, []);

  // ============================================================
  // RENDER ALL GIS LAYERS
  // ============================================================

  useEffect(() => {
    if (
      !mapInstanceRef.current ||
      !gisData
    ) {
      return;
    }

    const map =
      mapInstanceRef.current;

    const {
      zones = [],
      requests = [],
      warehouses = [],
      relief_centers = [],
      deliveries = [],
      blocked_roads = []
    } = gisData;

    const groups =
      layerGroupsRef.current;

    // ==========================================================
    // FLOOD ZONES
    // ==========================================================

    groups.zones?.clearLayers();

    if (layers.zones) {
      zones.forEach(zone => {
        if (
          !zone.polygon ||
          zone.polygon.length === 0
        ) {
          return;
        }

        const isSevere =
          zone.severity_level ===
            'SEVERE' ||
          zone.severity_level ===
            'CRITICAL';

        const color =
          isSevere
            ? '#DC2626'
            : '#EA580C';

        const polygon =
          L.polygon(
            zone.polygon as [
              number,
              number
            ][],
            {
              color,
              weight: 2,
              opacity: 0.85,
              fillColor: color,
              fillOpacity:
                isSevere
                  ? 0.28
                  : 0.16,
              dashArray:
                isSevere
                  ? '4,4'
                  : undefined
            }
          );

        polygon.bindPopup(`
          <div style="
            padding:8px;
            font-size:12px;
            min-width:210px;
          ">
            <div style="
              font-weight:700;
              font-size:14px;
              color:#0F1E36;
              margin-bottom:6px;
            ">
              ${zone.name}
            </div>

            <div>
              Severity:
              <b>${zone.severity_level}</b>
            </div>

            <div>
              Water Level:
              <b>${zone.water_level_meters} m</b>
            </div>

            <div>
              Population:
              <b>${zone.population.toLocaleString()}</b>
            </div>

            <div>
              Households:
              <b>${zone.households}</b>
            </div>

            <div>
              Critical Requests:
              <b>${zone.critical_requests_count}</b>
            </div>
          </div>
        `);

        polygon.addTo(
          groups.zones
        );
      });
    }

    // ==========================================================
    // COMMUNITY REQUESTS
    // ==========================================================

    groups.requests?.clearLayers();

    if (layers.requests) {
      requests.forEach(req => {
        const isCritical =
          req.priority_classification ===
            'CRITICAL' ||
          req.priority_score >= 80;

        const isDelivered =
          req.status ===
          'DELIVERED';

        const markerColor =
          isDelivered
            ? '#059669'
            : isCritical
            ? '#DC2626'
            : '#EA580C';

        const iconHtml = `
          <div style="
            background:${markerColor};
            width:28px;
            height:28px;
            border-radius:50%;
            border:3px solid white;
            box-shadow:
              0 2px 6px rgba(0,0,0,0.35);
            display:flex;
            align-items:center;
            justify-content:center;
            color:white;
            font-size:10px;
            font-weight:700;
          ">
            ${
              isDelivered
                ? '✓'
                : Math.round(
                    req.priority_score ||
                    50
                  )
            }
          </div>
        `;

        const icon =
          L.divIcon({
            html: iconHtml,
            className:
              'resqflow-request-icon',
            iconSize: [
              28,
              28
            ],
            iconAnchor: [
              14,
              14
            ]
          });

        const marker =
          L.marker(
            [
              req.lat,
              req.lon
            ],
            { icon }
          );

        marker.bindPopup(`
          <div style="
            padding:8px;
            font-size:12px;
            min-width:220px;
          ">

            <div style="
              font-weight:700;
              font-size:14px;
              color:#0F1E36;
            ">
              ${req.location_name}
            </div>

            <div style="
              color:${markerColor};
              font-weight:700;
              margin:4px 0 7px;
            ">
              ${req.priority_classification}
              —
              ${Math.round(
                req.priority_score
              )}/100
            </div>

            <div>
              Affected:
              <b>${req.affected_people} people</b>
            </div>

            <div>
              Vulnerable:
              <b>${req.vulnerable_count}</b>
            </div>

            <div>
              Urgency:
              <b>${req.urgency}</b>
            </div>

            <div>
              Status:
              <b>${req.status}</b>
            </div>

            <div style="
              margin-top:6px;
            ">
              <b>Needs:</b>
              ${
                req.items &&
                req.items.length
                  ? req.items.join(
                      ', '
                    )
                  : 'Not specified'
              }
            </div>

            <button
              onclick="
                window.__openMatchModal &&
                window.__openMatchModal(${req.id})
              "
              style="
                margin-top:9px;
                width:100%;
                background:#D97450;
                color:white;
                border:0;
                padding:7px;
                border-radius:5px;
                font-size:11px;
                font-weight:700;
                cursor:pointer;
              "
            >
              Match Resources
            </button>

          </div>
        `);

        marker.addTo(
          groups.requests
        );
      });
    }

    // ==========================================================
    // WAREHOUSES
    // ==========================================================

    groups.warehouses?.clearLayers();

    if (layers.warehouses) {
      warehouses.forEach(warehouse => {
        const icon =
          L.divIcon({
            html: `
              <div style="
                background:#0F1E36;
                width:28px;
                height:28px;
                border-radius:6px;
                border:2px solid white;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:14px;
                box-shadow:
                  0 2px 5px rgba(0,0,0,0.25);
              ">
                📦
              </div>
            `,
            className:
              'resqflow-warehouse-icon',
            iconSize: [
              28,
              28
            ],
            iconAnchor: [
              14,
              14
            ]
          });

        const marker =
          L.marker(
            [
              warehouse.lat,
              warehouse.lon
            ],
            { icon }
          );

        marker.bindPopup(`
          <div style="
            padding:8px;
            font-size:12px;
            min-width:210px;
          ">

            <div style="
              font-weight:700;
              font-size:14px;
              color:#0F1E36;
              margin-bottom:5px;
            ">
              ${warehouse.name}
            </div>

            <div>
              Code:
              <b>${warehouse.code}</b>
            </div>

            <div>
              Capacity:
              <b>${warehouse.capacity_sqm} m²</b>
            </div>

            <div style="
              margin-top:7px;
              font-weight:700;
            ">
              Available Inventory
            </div>

            <div style="
              margin-top:4px;
              line-height:1.5;
            ">
              ${
                warehouse.inventory &&
                warehouse.inventory.length
                  ? warehouse.inventory
                      .slice(0, 8)
                      .map(
                        item =>
                          `${item.item_name}: <b>${item.available} ${item.unit}</b>`
                      )
                      .join(
                        '<br/>'
                      )
                  : 'No inventory data'
              }
            </div>

          </div>
        `);

        marker.addTo(
          groups.warehouses
        );
      });
    }

    // ==========================================================
    // RELIEF CENTERS
    // ==========================================================

    groups.reliefCenters?.clearLayers();

    if (layers.reliefCenters) {
      relief_centers.forEach(center => {
        const icon =
          L.divIcon({
            html: `
              <div style="
                background:#2563EB;
                width:28px;
                height:28px;
                border-radius:50%;
                border:2px solid white;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:14px;
                box-shadow:
                  0 2px 6px rgba(0,0,0,0.3);
              ">
                ⛺
              </div>
            `,
            className:
              'resqflow-relief-center-icon',
            iconSize: [
              28,
              28
            ],
            iconAnchor: [
              14,
              14
            ]
          });

        const marker =
          L.marker(
            [
              center.lat,
              center.lon
            ],
            { icon }
          );

        const occupancyPercentage =
          center.capacity > 0
            ? Math.round(
                (
                  center.occupancy /
                  center.capacity
                ) * 100
              )
            : 0;

        marker.bindPopup(`
          <div style="
            padding:8px;
            font-size:12px;
            min-width:200px;
          ">

            <div style="
              font-weight:700;
              font-size:14px;
              color:#0F1E36;
              margin-bottom:6px;
            ">
              ${center.name}
            </div>

            <div>
              Capacity:
              <b>${center.capacity}</b>
            </div>

            <div>
              Occupancy:
              <b>${center.occupancy}</b>
              (${occupancyPercentage}%)
            </div>

            <div>
              Medical Support:
              <b>
                ${
                  center.has_medical
                    ? 'Available'
                    : 'Not available'
                }
              </b>
            </div>

          </div>
        `);

        marker.addTo(
          groups.reliefCenters
        );
      });
    }

    // ==========================================================
    // DELIVERY ROUTES
    // ==========================================================

    groups.deliveries?.clearLayers();

    if (layers.deliveries) {
      deliveries.forEach(delivery => {
        if (
          !delivery.waypoints ||
          delivery.waypoints.length < 2
        ) {
          return;
        }

        const latlngs =
          delivery.waypoints.map(
            waypoint =>
              [
                waypoint.lat,
                waypoint.lon
              ] as [
                number,
                number
              ]
          );

        const isDelivered =
          delivery.status ===
          'DELIVERED';

        const line =
          L.polyline(
            latlngs,
            {
              color:
                isDelivered
                  ? '#059669'
                  : '#0284C7',
              weight: 4,
              opacity: 0.85,
              dashArray:
                isDelivered
                  ? undefined
                  : '7,6'
            }
          );

        line.bindPopup(`
          <div style="
            padding:7px;
            font-size:12px;
          ">

            <b>Relief Delivery</b>

            <br/>

            Relief ID:
            <b>${delivery.relief_id}</b>

            <br/>

            Status:
            <b>${delivery.status}</b>

            <br/>

            Vehicle:
            <b>${delivery.vehicle}</b>

            <br/>

            Destination:
            <b>${delivery.destination}</b>

          </div>
        `);

        line.addTo(
          groups.deliveries
        );
      });
    }

    // ==========================================================
    // BLOCKED / INUNDATED ROADS
    // ==========================================================

    groups.blockedRoads?.clearLayers();

    if (layers.blockedRoads) {
      blocked_roads.forEach(road => {
        const icon =
          L.divIcon({
            html: `
              <div style="
                background:#B91C1C;
                color:white;
                width:22px;
                height:22px;
                border-radius:4px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:11px;
                font-weight:700;
                box-shadow:
                  0 2px 5px rgba(0,0,0,0.3);
              ">
                ⛔
              </div>
            `,
            className:
              'resqflow-road-icon',
            iconSize: [
              22,
              22
            ],
            iconAnchor: [
              11,
              11
            ]
          });

        L.marker(
          [
            road.lat,
            road.lon
          ],
          { icon }
        )
          .bindPopup(`
            <div style="
              padding:7px;
              font-size:12px;
              min-width:180px;
            ">

              <b style="
                color:#B91C1C;
              ">
                ${road.name}
              </b>

              <div style="
                margin-top:4px;
              ">
                ${road.reason}
              </div>

              <div>
                Status:
                <b>${road.status}</b>
              </div>

            </div>
          `)
          .addTo(
            groups.blockedRoads
          );
      });
    }

    // ==========================================================
    // MAP POPUP ACTION
    // ==========================================================

    (
      window as any
    ).__openMatchModal =
      (reqId: number) => {
        api
          .getRequestById(
            reqId
          )
          .then(req =>
            setActiveMatchModalRequest(
              req
            )
          )
          .catch(error =>
            console.error(
              'Request lookup failed:',
              error
            )
          );
      };

    // ==========================================================
    // AUTO-FIT MAP TO CURRENT DATA
    //
    // This is the part that keeps the map centered around the
    // actual ResQFlow data instead of a hard-coded location.
    // ==========================================================

    const points: [
      number,
      number
    ][] = [];

    // Community requests
    requests.forEach(req => {
      if (
        Number.isFinite(
          req.lat
        ) &&
        Number.isFinite(
          req.lon
        )
      ) {
        points.push([
          req.lat,
          req.lon
        ]);
      }
    });

    // Warehouses
    warehouses.forEach(
      warehouse => {
        if (
          Number.isFinite(
            warehouse.lat
          ) &&
          Number.isFinite(
            warehouse.lon
          )
        ) {
          points.push([
            warehouse.lat,
            warehouse.lon
          ]);
        }
      }
    );

    // Relief centers
    relief_centers.forEach(
      center => {
        if (
          Number.isFinite(
            center.lat
          ) &&
          Number.isFinite(
            center.lon
          )
        ) {
          points.push([
            center.lat,
            center.lon
          ]);
        }
      }
    );

    // Blocked roads
    blocked_roads.forEach(
      road => {
        if (
          Number.isFinite(
            road.lat
          ) &&
          Number.isFinite(
            road.lon
          )
        ) {
          points.push([
            road.lat,
            road.lon
          ]);
        }
      }
    );

    // Flood-zone centers
    zones.forEach(zone => {
      if (
        Array.isArray(
          zone.center
        ) &&
        zone.center.length === 2
      ) {
        points.push([
          zone.center[0],
          zone.center[1]
        ]);
      }
    });

    // Create a signature of the actual data locations.
    // The map only refits when the locations really change.
    const dataKey =
      JSON.stringify(
        points
      );

    if (
      points.length > 0 &&
      dataKey !==
        fittedDataKeyRef.current
    ) {
      const bounds =
        L.latLngBounds(
          points
        );

      if (
        bounds.isValid()
      ) {
        map.fitBounds(
          bounds,
          {
            padding: [
              40,
              40
            ],
            maxZoom: 14
          }
        );

        fittedDataKeyRef.current =
          dataKey;
      }
    }

    setTimeout(() => {
      map.invalidateSize();
    }, 100);

  }, [
    gisData,
    layers,
    setActiveMatchModalRequest
  ]);

  // ============================================================
  // UI
  // ============================================================

  return (
    <div className="relative z-0 isolate rounded-xl overflow-hidden border border-slate/20 shadow-soft bg-ivory">

      <div
        ref={
          mapContainerRef
        }
        style={{
          height,
          width: '100%'
        }}
      />

      {/* ========================================================
          GIS LAYER CONTROL
      ========================================================= */}

      <div className="
        absolute
        top-3
        right-3
        z-[1000]
        bg-ivory/95
        backdrop-blur-sm
        border
        border-slate/30
        p-2.5
        rounded-lg
        shadow-card
        text-xs
      ">

        <div className="
          flex
          items-center
          space-x-1.5
          font-bold
          text-navy
          mb-2
          pb-1
          border-b
          border-slate/20
        ">

          <Layers
            className="
              w-3.5
              h-3.5
              text-terracotta
            "
          />

          <span>
            GIS Layers
          </span>

        </div>

        <div className="
          space-y-1.5
        ">

          {/* Flood zones */}

          <label className="
            flex
            items-center
            space-x-2
            cursor-pointer
            text-slate-dark
          ">

            <input
              type="checkbox"
              checked={
                layers.zones
              }
              onChange={e =>
                setLayers({
                  ...layers,
                  zones:
                    e.target
                      .checked
                })
              }
              className="
                rounded
                text-terracotta
              "
            />

            <span>
              Flood Inundation Zones
            </span>

          </label>

          {/* Community requests */}

          <label className="
            flex
            items-center
            space-x-2
            cursor-pointer
            text-slate-dark
          ">

            <input
              type="checkbox"
              checked={
                layers.requests
              }
              onChange={e =>
                setLayers({
                  ...layers,
                  requests:
                    e.target
                      .checked
                })
              }
              className="
                rounded
                text-terracotta
              "
            />

            <span>
              Community Needs
            </span>

          </label>

          {/* Warehouses */}

          <label className="
            flex
            items-center
            space-x-2
            cursor-pointer
            text-slate-dark
          ">

            <input
              type="checkbox"
              checked={
                layers.warehouses
              }
              onChange={e =>
                setLayers({
                  ...layers,
                  warehouses:
                    e.target
                      .checked
                })
              }
              className="
                rounded
                text-terracotta
              "
            />

            <span>
              Depots & Warehouses
            </span>

          </label>

          {/* Relief centers */}

          <label className="
            flex
            items-center
            space-x-2
            cursor-pointer
            text-slate-dark
          ">

            <input
              type="checkbox"
              checked={
                layers.reliefCenters
              }
              onChange={e =>
                setLayers({
                  ...layers,
                  reliefCenters:
                    e.target
                      .checked
                })
              }
              className="
                rounded
                text-terracotta
              "
            />

            <span>
              Relief Centers
            </span>

          </label>

          {/* Deliveries */}

          <label className="
            flex
            items-center
            space-x-2
            cursor-pointer
            text-slate-dark
          ">

            <input
              type="checkbox"
              checked={
                layers.deliveries
              }
              onChange={e =>
                setLayers({
                  ...layers,
                  deliveries:
                    e.target
                      .checked
                })
              }
              className="
                rounded
                text-terracotta
              "
            />

            <span>
              Active Convoys
            </span>

          </label>

          {/* Blocked roads */}

          <label className="
            flex
            items-center
            space-x-2
            cursor-pointer
            text-slate-dark
          ">

            <input
              type="checkbox"
              checked={
                layers.blockedRoads
              }
              onChange={e =>
                setLayers({
                  ...layers,
                  blockedRoads:
                    e.target
                      .checked
                })
              }
              className="
                rounded
                text-terracotta
              "
            />

            <span>
              Inundated Roads
            </span>

          </label>

        </div>

      </div>

    </div>
  );
};
