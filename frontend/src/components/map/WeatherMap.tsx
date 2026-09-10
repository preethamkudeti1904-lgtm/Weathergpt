import React, { useEffect, useRef, useState } from 'react';
import { useWeather } from '../../contexts/WeatherContext';
import { locationService } from '../../services/locationService';
import {
  Layers,
  MapPin,
  Navigation,
  Compass,
  Thermometer,
  CloudRain,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  Locate,
  Info,
  CheckCircle2
} from 'lucide-react';
import L from 'leaflet';

type MapViewType = 'road' | 'satellite' | 'hybrid';

export const WeatherMap: React.FC = () => {
  const {
    currentLocation,
    location,
    latitude,
    longitude,
    accuracy,
    locationSource,
    gpsStatus,
    gpsError,
    isFollowingLocation,
    toggleFollowLocation,
    useMyLocation,
    setCoordinates,
    weather,
    alerts,
    t
  } = useWeather();

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const accuracyCircleRef = useRef<L.Circle | null>(null);
  const clickMarkerRef = useRef<L.Marker | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const labelsLayerRef = useRef<L.TileLayer | null>(null);
  const overlayGroupRef = useRef<L.LayerGroup | null>(null);

  const [activeView, setActiveView] = useState<MapViewType>('satellite');
  const [showTempLayer, setShowTempLayer] = useState<boolean>(true);
  const [showRainLayer, setShowRainLayer] = useState<boolean>(true);
  const [showAlertsLayer, setShowAlertsLayer] = useState<boolean>(true);
  const [clickedCoords, setClickedCoords] = useState<{ lat: number; lng: number } | null>(null);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [latitude, longitude],
        zoom: locationSource === 'gps' ? 15 : 12,
        zoomControl: false,
      });

      overlayGroupRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;

      // Handle Map Click to Explore Weather
      map.on('click', (e: L.LeafletMouseEvent) => {
        const { lat, lng } = e.latlng;
        setClickedCoords({ lat, lng });

        if (clickMarkerRef.current) {
          clickMarkerRef.current.setLatLng([lat, lng]);
        } else {
          const clickIcon = L.divIcon({
            className: 'click-pin',
            html: `<div style="background-color: #f59e0b; color: white; border: 2px solid white; border-radius: 9999px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); font-size: 13px;">🎯</div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14],
          });
          clickMarkerRef.current = L.marker([lat, lng], { icon: clickIcon }).addTo(map);
        }

        const selectedLocLabel = t('selected_location') || 'Selected Location';
        const getWeatherLabel = t('get_weather_here') || 'Get Weather Here';

        const popupContent = `
          <div style="font-family: inherit; font-size: 12px; min-width: 160px;">
            <div style="font-weight: bold; margin-bottom: 2px;">${selectedLocLabel}</div>
            <div style="color: #64748b; font-size: 11px; margin-bottom: 6px;">
              Lat: ${lat.toFixed(4)}°, Lng: ${lng.toFixed(4)}°
            </div>
            <button id="btn-get-weather-here" style="background-color: #0284c7; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer; width: 100%;">
              ${getWeatherLabel}
            </button>
          </div>
        `;

        clickMarkerRef.current.bindPopup(popupContent).openPopup();
      });
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Delegate button click inside Leaflet popup
  useEffect(() => {
    const handlePopupClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target && target.id === 'btn-get-weather-here' && clickedCoords) {
        setCoordinates(clickedCoords.lat, clickedCoords.lng, 'map_click');
        if (clickMarkerRef.current && mapInstanceRef.current) {
          mapInstanceRef.current.closePopup();
        }
      }
    };
    document.addEventListener('click', handlePopupClick);
    return () => document.removeEventListener('click', handlePopupClick);
  }, [clickedCoords, setCoordinates]);

  // Update Base Tile Layers (Road, Satellite, Hybrid)
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (tileLayerRef.current) map.removeLayer(tileLayerRef.current);
    if (labelsLayerRef.current) map.removeLayer(labelsLayerRef.current);

    if (activeView === 'road') {
      tileLayerRef.current = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);
    } else if (activeView === 'satellite') {
      tileLayerRef.current = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
          attribution: '&copy; Esri &mdash; Earthstar Geographics',
          maxZoom: 18,
        }
      ).addTo(map);
    } else if (activeView === 'hybrid') {
      tileLayerRef.current = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        {
          attribution: '&copy; Esri',
          maxZoom: 18,
        }
      ).addTo(map);

      labelsLayerRef.current = L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
        {
          subdomains: 'abcd',
          maxZoom: 19,
        }
      ).addTo(map);
    }
  }, [activeView]);

  // Update Location Marker, Accuracy Circle & Camera
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Pan camera if following location or GPS update
    if (isFollowingLocation || locationSource === 'gps') {
      const targetZoom = locationSource === 'gps' ? Math.max(map.getZoom(), 15) : map.getZoom();
      map.setView([latitude, longitude], targetZoom, { animate: true });
    }

    const isGps = locationSource === 'gps';
    const shortName = currentLocation?.name?.split(',')[0]?.trim() || location.split(',')[0]?.trim() || 'Location';

    // Marker with place name label (Section 13)
    const customIcon = L.divIcon({
      className: 'custom-weather-pin-container',
      html: `
        <div style="display: flex; flex-direction: column; align-items: center; pointer-events: auto; transform: translate(-50%, -100%);">
          <div style="background-color: #0f172a; color: white; border: 1.5px solid ${isGps ? '#10b981' : '#38bdf8'}; border-radius: 9999px; padding: 4px 10px; font-size: 11px; font-weight: 700; white-space: nowrap; box-shadow: 0 4px 12px rgba(0,0,0,0.4); display: flex; align-items: center; gap: 5px;">
            <span style="font-size: 13px;">📍</span>
            <span>${shortName}</span>
            ${isGps ? '<span style="width: 7px; height: 7px; border-radius: 9999px; background-color: #10b981; display: inline-block; box-shadow: 0 0 6px #10b981;" title="Live GPS Active"></span>' : ''}
          </div>
          <div style="width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-top: 6px solid ${isGps ? '#10b981' : '#38bdf8'};"></div>
        </div>
      `,
      iconSize: [0, 0],
      iconAnchor: [0, 0],
    });

    if (markerRef.current) {
      markerRef.current.setLatLng([latitude, longitude]);
      markerRef.current.setIcon(customIcon);
    } else {
      markerRef.current = L.marker([latitude, longitude], { icon: customIcon }).addTo(map);
    }

    // Clean map info window / popup (Section 14)
    const districtStr = currentLocation?.district || (currentLocation?.name?.includes('District') ? currentLocation.name.split(',')[1]?.trim() : '');
    const stateStr = currentLocation?.state || '';
    const countryStr = currentLocation?.country || 'India';
    const subAddress = [districtStr, stateStr, countryStr].filter(Boolean).join(', ');

    const popupContent = `
      <div style="font-family: inherit; padding: 6px 4px; min-width: 190px; color: #0f172a;">
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 2px;">
          <span style="font-size: 16px;">📍</span>
          <strong style="font-size: 14px; color: #0f172a;">${shortName}</strong>
        </div>
        ${subAddress ? `<div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">${subAddress}</div>` : ''}
        <div style="border-top: 1px solid #e2e8f0; padding-top: 6px; font-size: 11px; color: #334155; line-height: 1.5;">
          <div><strong>Lat:</strong> ${latitude.toFixed(4)}° | <strong>Lon:</strong> ${longitude.toFixed(4)}°</div>
          ${accuracy ? `<div><strong>GPS Accuracy:</strong> ±${accuracy} m</div>` : ''}
          ${weather ? `<div style="margin-top: 4px; font-weight: 600; color: #0284c7;">${weather.temperature}°C — ${weather.condition}</div>` : ''}
          <div style="font-size: 10px; color: #94a3b8; margin-top: 4px; text-transform: uppercase;">
            SOURCE: ${locationSource.toUpperCase()}${locationSource === 'default' ? ' (Initial Default)' : ''}
          </div>
        </div>
      </div>
    `;

    markerRef.current.bindPopup(popupContent);

    // Accuracy Circle for GPS readings (Section 8)
    if (accuracy && accuracy > 0) {
      if (accuracyCircleRef.current) {
        accuracyCircleRef.current.setLatLng([latitude, longitude]);
        accuracyCircleRef.current.setRadius(accuracy);
      } else {
        accuracyCircleRef.current = L.circle([latitude, longitude], {
          radius: accuracy,
          color: '#10b981',
          fillColor: '#34d399',
          fillOpacity: 0.15,
          weight: 1.5,
        }).addTo(map);
      }
    } else if (accuracyCircleRef.current) {
      map.removeLayer(accuracyCircleRef.current);
      accuracyCircleRef.current = null;
    }
  }, [latitude, longitude, location, accuracy, locationSource, isFollowingLocation, weather, currentLocation]);

  // Update Weather Overlays
  useEffect(() => {
    const map = mapInstanceRef.current;
    const overlayGroup = overlayGroupRef.current;
    if (!map || !overlayGroup) return;

    overlayGroup.clearLayers();

    // 1. Temperature Thermal Ring
    if (showTempLayer && weather) {
      const tempColor = weather.temperature > 35 ? '#ef4444' : weather.temperature > 25 ? '#f59e0b' : '#3b82f6';
      const tempCircle = L.circle([latitude, longitude], {
        color: tempColor,
        fillColor: tempColor,
        fillOpacity: 0.12,
        radius: 25000,
        weight: 1.5,
      }).bindTooltip(`Thermal Zone: ${weather.temperature}°C`, { permanent: false });
      overlayGroup.addLayer(tempCircle);
    }

    // 2. Precipitation Zone
    if (showRainLayer && weather && weather.precipitation !== null && weather.precipitation !== undefined && weather.precipitation > 0) {
      const rainCircle = L.circle([latitude, longitude], {
        color: '#0284c7',
        fillColor: '#0284c7',
        fillOpacity: 0.2,
        radius: 18000,
        weight: 2,
        dashArray: '4, 6',
      }).bindTooltip(`Precipitation: ${weather.precipitation} mm`, { permanent: false });
      overlayGroup.addLayer(rainCircle);
    }

    // 3. Official Threat & Disaster Alert Zones
    if (showAlertsLayer && alerts) {
      const allActive = [...(alerts.direct_alerts || []), ...(alerts.regional_alerts || [])];
      const listToRender = allActive.length > 0 ? allActive : (alerts.alerts || []);

      listToRender.forEach((a) => {
        const aLat = a.centroid_lat !== null && a.centroid_lat !== undefined ? a.centroid_lat : latitude;
        const aLon = a.centroid_lon !== null && a.centroid_lon !== undefined ? a.centroid_lon : longitude;
        const color = a.color_code?.toLowerCase() === 'red' ? '#ef4444'
          : a.color_code?.toLowerCase() === 'orange' ? '#f97316'
          : a.color_code?.toLowerCase() === 'yellow' ? '#eab308'
          : '#3b82f6';

        // Add warning zone circle
        const radiusMeters = (a.radius_km || 30.0) * 1000;
        const alertCircle = L.circle([aLat, aLon], {
          color: color,
          fillColor: color,
          fillOpacity: 0.18,
          weight: 2,
          dashArray: '5, 5'
        }).bindTooltip(`⚠️ ${a.title} (${a.severity})`, { permanent: false });
        overlayGroup.addLayer(alertCircle);

        // Add prominent alert marker
        const alertIcon = L.divIcon({
          className: 'alert-pin',
          html: `<div style="background-color: ${color}; color: white; border: 2px solid white; border-radius: 9999px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.4); font-size: 13px; font-weight: bold; cursor: pointer;">⚠️</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14],
        });

        const alertMarker = L.marker([aLat, aLon], { icon: alertIcon });
        const popupContent = `
          <div style="font-family: sans-serif; max-width: 240px;">
            <div style="font-size: 10px; font-weight: bold; text-transform: uppercase; color: ${color}; letter-spacing: 0.5px;">
              OFFICIAL WARNING • ${a.severity}
            </div>
            <div style="font-size: 13px; font-weight: bold; color: #0f172a; margin-top: 2px;">
              ${a.title}
            </div>
            <div style="font-size: 10px; color: #64748b; margin-top: 2px;">
              Source: ${a.source}
            </div>
            <div style="font-size: 10px; color: #475569; margin-top: 4px; font-weight: 500;">
              🕒 Valid: ${a.start_time} — ${a.end_time}
            </div>
            <p style="font-size: 11px; color: #334155; margin-top: 6px; line-height: 1.4;">
              ${a.description}
            </p>
            ${a.recommended_action ? `
              <div style="margin-top: 6px; padding: 6px; background-color: #fef3c7; border-radius: 6px; font-size: 10px; color: #92400e; border: 1px solid #fde68a;">
                <strong>Instruction:</strong> ${a.recommended_action}
              </div>
            ` : ''}
          </div>
        `;
        alertMarker.bindPopup(popupContent);
        overlayGroup.addLayer(alertMarker);
      });
    }
  }, [showTempLayer, showRainLayer, showAlertsLayer, weather, alerts, latitude, longitude]);


  const handleUseMyLocationClick = async () => {
    await useMyLocation();
    if (mapInstanceRef.current) {
      mapInstanceRef.current.setView([latitude, longitude], 16, { animate: true });
    }
  };

  const isPoorAccuracy = accuracy !== null && accuracy > 300;

  return (
    <div className="space-y-3">
      {/* Top GPS Status & Live Control Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm text-xs">
        <div className="flex items-center gap-3">
          {/* Main "Use My Location" Button */}
          <button
            onClick={handleUseMyLocationClick}
            disabled={gpsStatus === 'loading'}
            className="px-3.5 py-1.5 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white font-semibold flex items-center gap-2 transition shadow-sm"
            title="Request exact GPS coordinates from browser"
          >
            {gpsStatus === 'loading' ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Navigation className="w-4 h-4 text-white" />
            )}
            <span>{gpsStatus === 'loading' ? 'Locating GPS...' : 'Use My Location'}</span>
          </button>

          {/* Coordinates & Accuracy Indicator */}
          <div className="flex items-center gap-2 font-mono text-[11px] text-slate-600 dark:text-slate-300">
            <span className="font-semibold text-slate-900 dark:text-white">
              {locationService.formatCoordinates(latitude, longitude)}
            </span>
            {accuracy !== null && (
              <span className={`px-2 py-0.5 rounded font-sans text-[10px] font-bold border ${
                isPoorAccuracy
                  ? 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800'
                  : 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800'
              }`}>
                {t('gps_accuracy')}: ±{accuracy} m
              </span>
            )}
          </div>
        </div>

        {/* Right side: Follow location toggle */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleFollowLocation}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition flex items-center gap-1.5 ${
              isFollowingLocation
                ? 'bg-primary-50 dark:bg-primary-950/60 border-primary-300 dark:border-primary-800 text-primary-700 dark:text-primary-300'
                : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400'
            }`}
            title="Toggle camera tracking when coordinates update"
          >
            <Locate className="w-3.5 h-3.5" />
            <span>{t('follow_my_location')}: {isFollowingLocation ? 'ON' : 'OFF'}</span>
          </button>
        </div>
      </div>

      {/* Accuracy & Permission Warning Callout */}
      {isPoorAccuracy && (
        <div className="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-900 text-xs text-amber-800 dark:text-amber-300 flex items-center gap-2">
          <Info className="w-4 h-4 flex-shrink-0" />
          <span>{t('accuracy_low_warning')}</span>
        </div>
      )}

      {gpsError && (
        <div className="p-2.5 rounded-lg bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-xs text-red-700 dark:text-red-300 flex items-center justify-between">
          <span>{gpsError}</span>
          <button
            onClick={handleUseMyLocationClick}
            className="px-2 py-0.5 rounded bg-red-200 dark:bg-red-900 font-semibold"
          >
            {t('enable_location')}
          </button>
        </div>
      )}

      {/* Main Map Container */}
      <div className="relative w-full h-[550px] rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm bg-slate-100 dark:bg-slate-900">
        <div ref={mapContainerRef} className="w-full h-full" />

        {/* Layer Switcher & Overlays Control Box */}
        <div className="absolute top-3 right-3 z-[1000] bg-white/95 dark:bg-slate-900/95 backdrop-blur border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 shadow-lg text-xs space-y-2.5 max-w-[200px]">
          <div>
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1.5">
              {t('weatherMap')}
            </span>
            <div className="grid grid-cols-3 gap-1">
              <button
                onClick={() => setActiveView('road')}
                className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                  activeView === 'road'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                }`}
              >
                {t('map_roadmap')}
              </button>
              <button
                onClick={() => setActiveView('satellite')}
                className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                  activeView === 'satellite'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                }`}
              >
                {t('map_satellite')}
              </button>
              <button
                onClick={() => setActiveView('hybrid')}
                className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                  activeView === 'hybrid'
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                }`}
              >
                {t('map_hybrid')}
              </button>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1.5">
              {t('weatherMap')}
            </span>
            <div className="space-y-1.5">
              <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={showTempLayer}
                  onChange={(e) => setShowTempLayer(e.target.checked)}
                  className="rounded text-primary-600 focus:ring-0"
                />
                <span className="flex items-center gap-1">
                  <Thermometer className="w-3 h-3 text-red-500" /> {t('temperature')}
                </span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={showRainLayer}
                  onChange={(e) => setShowRainLayer(e.target.checked)}
                  className="rounded text-primary-600 focus:ring-0"
                />
                <span className="flex items-center gap-1">
                  <CloudRain className="w-3 h-3 text-blue-500" /> {t('precipitation')}
                </span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer text-slate-700 dark:text-slate-300">
                <input
                  type="checkbox"
                  checked={showAlertsLayer}
                  onChange={(e) => setShowAlertsLayer(e.target.checked)}
                  className="rounded text-primary-600 focus:ring-0"
                />
                <span className="flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 text-amber-500" /> {t('alerts')}
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Floating Controls: Zoom & Quick GPS */}
        <div className="absolute bottom-3 right-3 z-[1000] flex flex-col gap-1.5">
          <button
            onClick={handleUseMyLocationClick}
            className="w-8 h-8 rounded-lg bg-primary-600 text-white flex items-center justify-center shadow-md hover:bg-primary-700 transition"
            title={t('use_my_location')}
          >
            <Navigation className="w-4 h-4" />
          </button>

          <button
            onClick={() => mapInstanceRef.current?.zoomIn()}
            className="w-8 h-8 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center shadow-md hover:bg-slate-50 dark:hover:bg-slate-800 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>

          <button
            onClick={() => mapInstanceRef.current?.zoomOut()}
            className="w-8 h-8 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 flex items-center justify-center shadow-md hover:bg-slate-50 dark:hover:bg-slate-800 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
        </div>

        {/* Footer info: Click anywhere hint */}
        <div className="absolute bottom-3 left-3 z-[1000] px-3 py-1 rounded bg-slate-900/85 text-white text-[11px] font-medium backdrop-blur shadow flex items-center gap-2">
          <span>💡 {t('map_click_hint')}</span>
        </div>
      </div>
    </div>
  );
};
