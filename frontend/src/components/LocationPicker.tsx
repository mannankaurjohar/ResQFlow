import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import {
  Search,
  MapPin,
  CheckCircle2,
  MousePointer2
} from 'lucide-react';

interface LocationPickerProps {
  locationName: string;
  latitude: number | null;
  longitude: number | null;
  onLocationChange: (
    name: string,
    latitude: number,
    longitude: number
  ) => void;
}

interface SearchResult {
  display_name: string;
  lat: string;
  lon: string;
}

const DEFAULT_CENTER: [number, number] = [
  23.2599,
  77.4126
];

const DEFAULT_ZOOM = 12;

export const LocationPicker: React.FC<
  LocationPickerProps
> = ({
  locationName,
  latitude,
  longitude,
  onLocationChange
}) => {
  const mapContainerRef =
    useRef<HTMLDivElement>(null);

  const mapRef =
    useRef<L.Map | null>(null);

  const markerRef =
    useRef<L.Marker | null>(null);

  const [searchText, setSearchText] =
    useState('');

  const [searchResults, setSearchResults] =
    useState<SearchResult[]>([]);

  const [searching, setSearching] =
    useState(false);

  const [mapReady, setMapReady] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  // ==========================================================
  // INITIALISE MAP
  // ==========================================================

  useEffect(() => {
    if (
      !mapContainerRef.current ||
      mapRef.current
    ) {
      return;
    }

    const initialPosition: [
      number,
      number
    ] =
      latitude !== null &&
      longitude !== null
        ? [latitude, longitude]
        : DEFAULT_CENTER;

    const map = L.map(
      mapContainerRef.current,
      {
        center: initialPosition,
        zoom:
          latitude !== null &&
          longitude !== null
            ? 15
            : DEFAULT_ZOOM,
        zoomControl: true
      }
    );

    L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        attribution:
          '&copy; OpenStreetMap contributors',
        maxZoom: 19
      }
    ).addTo(map);

    mapRef.current = map;

    // Existing selected point
    if (
      latitude !== null &&
      longitude !== null
    ) {
      setMarker(
        map,
        latitude,
        longitude,
        locationName
      );
    }

    // Click anywhere on map
    map.on(
      'click',
      async event => {
        const lat =
          event.latlng.lat;

        const lon =
          event.latlng.lng;

        setError(null);

        setMarker(
          map,
          lat,
          lon,
          'Selected location'
        );

        // Immediately save coordinates
        onLocationChange(
          `Selected location (${lat.toFixed(
            5
          )}, ${lon.toFixed(5)})`,
          lat,
          lon
        );

        // Try reverse geocoding
        try {
          const response =
            await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(
                lat
              )}&lon=${encodeURIComponent(
                lon
              )}&zoom=18&addressdetails=1`,
              {
                headers: {
                  Accept:
                    'application/json'
                }
              }
            );

          if (!response.ok) {
            return;
          }

          const data =
            await response.json();

          const name =
            data.display_name ||
            `Selected location (${lat.toFixed(
              5
            )}, ${lon.toFixed(5)})`;

          setMarker(
            map,
            lat,
            lon,
            name
          );

          onLocationChange(
            name,
            lat,
            lon
          );
        } catch (err) {
          console.error(
            'Reverse geocoding failed:',
            err
          );
        }
      }
    );

    setMapReady(true);

    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
  }, []);

  // ==========================================================
  // SET MARKER
  // ==========================================================

  const setMarker = (
    map: L.Map,
    lat: number,
    lon: number,
    title: string
  ) => {
    if (markerRef.current) {
      markerRef.current.remove();
    }

    const markerIcon =
      L.divIcon({
        html: `
          <div style="
            width:34px;
            height:34px;
            border-radius:50% 50% 50% 0;
            transform:rotate(-45deg);
            background:#D97450;
            border:3px solid white;
            box-shadow:
              0 2px 8px rgba(0,0,0,0.35);
            display:flex;
            align-items:center;
            justify-content:center;
          ">
            <div style="
              width:10px;
              height:10px;
              background:white;
              border-radius:50%;
            "></div>
          </div>
        `,
        className:
          'resqflow-location-marker',
        iconSize: [34, 34],
        iconAnchor: [17, 34]
      });

    const marker =
      L.marker(
        [lat, lon],
        {
          icon: markerIcon,
          draggable: true
        }
      ).addTo(map);

    marker.bindPopup(`
      <div style="
        font-size:12px;
        min-width:180px;
        padding:4px;
      ">
        <b>${title}</b>
        <br/><br/>
        Latitude:
        ${lat.toFixed(6)}
        <br/>
        Longitude:
        ${lon.toFixed(6)}
      </div>
    `);

    marker.on(
      'dragend',
      async event => {
        const marker =
          event.target as L.Marker;

        const position =
          marker.getLatLng();

        const newLat =
          position.lat;

        const newLon =
          position.lng;

        let newName =
          `Selected location (${newLat.toFixed(
            5
          )}, ${newLon.toFixed(5)})`;

        onLocationChange(
          newName,
          newLat,
          newLon
        );

        try {
          const response =
            await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(
                newLat
              )}&lon=${encodeURIComponent(
                newLon
              )}&zoom=18&addressdetails=1`,
              {
                headers: {
                  Accept:
                    'application/json'
                }
              }
            );

          if (response.ok) {
            const data =
              await response.json();

            newName =
              data.display_name ||
              newName;
          }
        } catch {
          // Keep coordinate-based name
        }

        onLocationChange(
          newName,
          newLat,
          newLon
        );

        marker.bindPopup(`
          <div style="
            font-size:12px;
            padding:4px;
          ">
            <b>${newName}</b>
            <br/><br/>
            ${newLat.toFixed(6)},
            ${newLon.toFixed(6)}
          </div>
        `);
      }
    );

    markerRef.current =
      marker;

    map.setView(
      [lat, lon],
      15,
      {
        animate: true
      }
    );
  };

  // ==========================================================
  // SEARCH
  // ==========================================================

  const searchLocation =
    async () => {
      const query =
        searchText.trim();

      if (!query) {
        return;
      }

      setSearching(true);
      setError(null);

      try {
        const response =
          await fetch(
            `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(
              query
            )}&countrycodes=in&limit=5&addressdetails=1`,
            {
              headers: {
                Accept:
                  'application/json'
              }
            }
          );

        if (!response.ok) {
          throw new Error(
            'Location search failed.'
          );
        }

        const data =
          (await response.json()) as SearchResult[];

        if (!data.length) {
          setSearchResults([]);
          setError(
            'No matching location found. Try a village, locality, landmark or address.'
          );
          return;
        }

        setSearchResults(data);

      } catch (err) {
        console.error(
          'Location search error:',
          err
        );

        setError(
          'Unable to search for this location right now.'
        );
      } finally {
        setSearching(false);
      }
    };

  // ==========================================================
  // SELECT SEARCH RESULT
  // ==========================================================

  const selectSearchResult =
    (result: SearchResult) => {
      const lat =
        Number(result.lat);

      const lon =
        Number(result.lon);

      if (
        !Number.isFinite(lat) ||
        !Number.isFinite(lon)
      ) {
        return;
      }

      setSearchText(
        result.display_name
      );

      setSearchResults([]);

      setError(null);

      if (mapRef.current) {
        setMarker(
          mapRef.current,
          lat,
          lon,
          result.display_name
        );
      }

      onLocationChange(
        result.display_name,
        lat,
        lon
      );
    };

  // ==========================================================
  // ENTER KEY
  // ==========================================================

  const handleKeyDown =
    (
      event: React.KeyboardEvent
    ) => {
      if (
        event.key === 'Enter'
      ) {
        event.preventDefault();
        searchLocation();
      }
    };

  return (
    <div className="space-y-3">

      {/* Heading */}

      <div className="
        flex
        items-center
        gap-2
      ">
        <MapPin className="
          w-4
          h-4
          text-terracotta
        "/>

        <div>
          <div className="
            font-bold
            text-navy
            text-sm
          ">
            Affected Location
          </div>

          <div className="
            text-[10px]
            text-slate
          ">
            Search for the location or
            select it directly on the map.
          </div>
        </div>
      </div>

      {/* Search */}

      <div className="
        relative
      ">

        <div className="
          flex
          gap-2
        ">

          <div className="
            flex-1
            relative
          ">

            <Search className="
              absolute
              left-3
              top-1/2
              -translate-y-1/2
              w-4
              h-4
              text-slate
            "/>

            <input
              type="text"
              value={searchText}
              onChange={event => {
                setSearchText(
                  event.target.value
                );
                setSearchResults([]);
              }}
              onKeyDown={
                handleKeyDown
              }
              placeholder="
                Search village, locality,
                landmark or address
              "
              className="
                w-full
                bg-white
                border
                border-slate/30
                rounded-lg
                pl-9
                pr-3
                py-2.5
                text-sm
                text-navy
                outline-none
                focus:border-terracotta
              "
            />

          </div>

          <button
            type="button"
            onClick={
              searchLocation
            }
            disabled={searching}
            className="
              px-4
              py-2
              rounded-lg
              bg-terracotta
              text-white
              font-semibold
              text-sm
              disabled:opacity-50
            "
          >
            {searching
              ? 'Searching...'
              : 'Search'}
          </button>

        </div>

        {/* Search results */}

        {searchResults.length >
          0 && (
            <div className="
              absolute
              left-0
              right-0
              mt-1
              bg-white
              border
              border-slate/30
              rounded-lg
              shadow-lg
              overflow-hidden
              z-[2000]
            ">

              {searchResults.map(
                (
                  result,
                  index
                ) => (
                  <button
                    type="button"
                    key={`${result.lat}-${result.lon}-${index}`}
                    onClick={() =>
                      selectSearchResult(
                        result
                      )
                    }
                    className="
                      w-full
                      text-left
                      px-3
                      py-2.5
                      hover:bg-slate-50
                      border-b
                      border-slate/10
                      last:border-0
                    "
                  >

                    <div className="
                      flex
                      items-start
                      gap-2
                    ">

                      <MapPin className="
                        w-4
                        h-4
                        mt-0.5
                        text-terracotta
                        flex-shrink-0
                      "/>

                      <span className="
                        text-xs
                        text-navy
                      ">
                        {
                          result.display_name
                        }
                      </span>

                    </div>

                  </button>
                )
              )}

            </div>
          )}

      </div>

      {error && (
        <div className="
          bg-orange-50
          border
          border-orange-200
          rounded-lg
          px-3
          py-2
          text-xs
          text-orange-800
        ">
          {error}
        </div>
      )}

      {/* Map */}

      <div className="
        relative
        h-[320px]
        rounded-xl
        overflow-hidden
        border
        border-slate/30
      ">

        <div
          ref={
            mapContainerRef
          }
          className="
            absolute
            inset-0
          "
        />

        {mapReady && (
          <div className="
            absolute
            bottom-3
            left-3
            z-[1000]
            bg-white/95
            rounded-lg
            border
            border-slate/20
            shadow
            px-3
            py-2
            text-[10px]
            text-slate-dark
            flex
            items-center
            gap-2
          ">
            <MousePointer2 className="
              w-3.5
              h-3.5
              text-terracotta
            "/>

            Click the map or drag the
            marker to refine the location.
          </div>
        )}

      </div>

      {/* Selected location */}

      {latitude !== null &&
        longitude !== null && (
          <div className="
            bg-emerald-50
            border
            border-emerald-200
            rounded-lg
            p-3
          ">

            <div className="
              flex
              items-start
              gap-2
            ">

              <CheckCircle2 className="
                w-4
                h-4
                text-emerald-600
                mt-0.5
                flex-shrink-0
              "/>

              <div>

                <div className="
                  text-xs
                  font-bold
                  text-emerald-900
                ">
                  Location Selected
                </div>

                <div className="
                  text-xs
                  text-emerald-800
                  mt-0.5
                ">
                  {locationName}
                </div>

                <div className="
                  text-[10px]
                  font-mono
                  text-emerald-700
                  mt-1
                ">
                  {latitude.toFixed(6)},
                  {' '}
                  {longitude.toFixed(6)}
                </div>

              </div>

            </div>

          </div>
        )}

    </div>
  );
};