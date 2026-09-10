import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import {
  Layers,
  ZoomIn,
  ZoomOut,
  Crosshair,
  MapPin,
  Wind,
  Navigation,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { degreesToCardinal, getBeaufortLevel, windService, WindPoint } from '../../services/windService';

type MapViewType = 'road' | 'satellite' | 'hybrid';

interface WindMapCanvasProps {
  latitude: number;
  longitude: number;
  locationName: string;
  activeWindPoint: WindPoint;
  onUseLocation: (lat: number, lon: number, name?: string) => void;
  onInspectLocation?: (point: WindPoint, lat: number, lon: number) => void;
  t: (key: string) => string;
}

export const WindMapCanvas: React.FC<WindMapCanvasProps> = ({
  latitude,
  longitude,
  locationName,
  activeWindPoint,
  onUseLocation,
  onInspectLocation,
  t
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const clickMarkerRef = useRef<L.Marker | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const labelsLayerRef = useRef<L.TileLayer | null>(null);

  const [activeView, setActiveView] = useState<MapViewType>('satellite');
  const [clickedData, setClickedData] = useState<{
    lat: number;
    lng: number;
    windPoint?: WindPoint;
    loading: boolean;
  } | null>(null);

  const animFrameIdRef = useRef<number | null>(null);
  const prefersReducedMotion = useRef<boolean>(
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [latitude, longitude],
        zoom: 12,
        zoomControl: false,
        attributionControl: false
      });

      mapInstanceRef.current = map;

      // Primary Center Marker
      const centerIcon = L.divIcon({
        className: 'wind-center-pin',
        html: `<div style="background-color: #0284c7; color: white; border: 2.5px solid white; border-radius: 9999px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(2,132,199,0.5); font-size: 15px;">📍</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });
      markerRef.current = L.marker([latitude, longitude], { icon: centerIcon }).addTo(map);

      // Map Click Event
      map.on('click', async (e: L.LeafletMouseEvent) => {
        const { lat, lng } = e.latlng;
        setClickedData({ lat, lng, loading: true });

        // Update or create click pin
        if (clickMarkerRef.current) {
          clickMarkerRef.current.setLatLng([lat, lng]);
        } else {
          const clickIcon = L.divIcon({
            className: 'wind-inspect-pin',
            html: `<div style="background-color: #f59e0b; color: white; border: 2px solid white; border-radius: 9999px; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); font-size: 13px;">🎯</div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14],
          });
          clickMarkerRef.current = L.marker([lat, lng], { icon: clickIcon }).addTo(map);
        }

        try {
          const fetched = await windService.getWindData(lat, lng, 'Inspected Coordinate');
          setClickedData({ lat, lng, windPoint: fetched.current, loading: false });

          if (onInspectLocation) {
            onInspectLocation(fetched.current, lat, lng);
          }

          const speedText = fetched.current.windSpeed !== null ? `${fetched.current.windSpeed} km/h` : 'N/A';
          const dirText = fetched.current.windDirection !== null ? `${fetched.current.windDirectionCardinal} (${fetched.current.windDirection}°)` : 'N/A';
          const gustText = fetched.current.windGust !== null ? `${fetched.current.windGust} km/h` : 'N/A';

          const popupContent = `
            <div style="font-family: inherit; font-size: 12px; min-width: 170px; line-height: 1.4; color: #1e293b;">
              <div style="font-weight: 700; color: #0f172a; margin-bottom: 2px;">${t('inspecting_coordinate')}</div>
              <div style="color: #64748b; font-size: 11px; margin-bottom: 6px;">
                Lat: ${lat.toFixed(4)}°, Lon: ${lng.toFixed(4)}°
              </div>
              <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 6px; margin-bottom: 8px;">
                <div><strong>${t('wind_speed')}:</strong> ${speedText}</div>
                <div><strong>${t('wind_direction')}:</strong> ${dirText}</div>
                <div><strong>${t('wind_gusts')}:</strong> ${gustText}</div>
              </div>
              <button id="btn-use-clicked-location" style="background-color: #0284c7; color: white; border: none; padding: 6px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; width: 100%;">
                ${t('use_this_location')}
              </button>
            </div>
          `;

          if (clickMarkerRef.current) {
            clickMarkerRef.current.bindPopup(popupContent).openPopup();
          }
        } catch {
          setClickedData({ lat, lng, loading: false });
        }
      });
    }

    return () => {
      if (animFrameIdRef.current) {
        cancelAnimationFrame(animFrameIdRef.current);
        animFrameIdRef.current = null;
      }
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
      if (target && target.id === 'btn-use-clicked-location' && clickedData) {
        onUseLocation(clickedData.lat, clickedData.lng, `Location (${clickedData.lat.toFixed(3)}°, ${clickedData.lng.toFixed(3)}°)`);
        if (clickMarkerRef.current && mapInstanceRef.current) {
          mapInstanceRef.current.closePopup();
        }
      }
    };
    document.addEventListener('click', handlePopupClick);
    return () => document.removeEventListener('click', handlePopupClick);
  }, [clickedData, onUseLocation]);

  // Update Center Pin and Viewport
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (markerRef.current) {
      markerRef.current.setLatLng([latitude, longitude]);
    }
    map.setView([latitude, longitude], map.getZoom(), { animate: true });
  }, [latitude, longitude]);

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

  // Canvas Wind Particle & Directional Flow Visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Resize canvas to match display size
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const deg = activeWindPoint.windDirection !== null && activeWindPoint.windDirection !== undefined
      ? activeWindPoint.windDirection
      : 0;
    const speedKmh = activeWindPoint.windSpeed !== null && activeWindPoint.windSpeed !== undefined
      ? activeWindPoint.windSpeed
      : 10;

    const beaufort = getBeaufortLevel(speedKmh);

    // Vector Calculation:
    // Meteorological wind deg indicates where wind comes FROM.
    // Flow travels in direction:
    // dx = -sin(deg * PI / 180)
    // dy = cos(deg * PI / 180)
    const rad = (deg * Math.PI) / 180;
    const flowX = -Math.sin(rad);
    const flowY = Math.cos(rad);

    // Speed scale factor
    const particleSpeed = Math.max(0.7, Math.min(speedKmh * 0.08, 4.5));

    // If reduced motion is requested, render clean static arrow grid
    if (prefersReducedMotion.current) {
      const rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      const step = 60;
      const arrowLen = 22;

      ctx.save();
      ctx.strokeStyle = beaufort.color;
      ctx.fillStyle = beaufort.color;
      ctx.lineWidth = 2;

      for (let x = step / 2; x < rect.width; x += step) {
        for (let y = step / 2; y < rect.height; y += step) {
          ctx.save();
          ctx.translate(x, y);
          ctx.rotate(Math.atan2(flowY, flowX));

          // Draw Arrow
          ctx.beginPath();
          ctx.moveTo(-arrowLen / 2, 0);
          ctx.lineTo(arrowLen / 2, 0);
          ctx.stroke();

          ctx.beginPath();
          ctx.moveTo(arrowLen / 2, 0);
          ctx.lineTo(arrowLen / 2 - 5, -4);
          ctx.lineTo(arrowLen / 2 - 5, 4);
          ctx.closePath();
          ctx.fill();

          ctx.restore();
        }
      }
      ctx.restore();
      return () => window.removeEventListener('resize', resizeCanvas);
    }

    // Dynamic Streamline Particles
    const PARTICLE_COUNT = 140;
    const particles: {
      x: number;
      y: number;
      age: number;
      maxAge: number;
      size: number;
      alpha: number;
    }[] = [];

    const rect = canvas.getBoundingClientRect();
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * rect.width,
        y: Math.random() * rect.height,
        age: Math.floor(Math.random() * 80),
        maxAge: 60 + Math.floor(Math.random() * 50),
        size: 1.2 + Math.random() * 1.5,
        alpha: 0.2 + Math.random() * 0.6
      });
    }

    let isRunning = true;

    const render = () => {
      if (!isRunning) return;

      const w = canvas.getBoundingClientRect().width;
      const h = canvas.getBoundingClientRect().height;

      // Soft clear with slight fade for wind motion trail effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
      ctx.clearRect(0, 0, w, h);

      ctx.save();
      ctx.strokeStyle = beaufort.color;
      ctx.fillStyle = beaufort.color;
      ctx.lineWidth = 1.6;
      ctx.lineCap = 'round';

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Draw particle line streak along flow vector
        const tailX = p.x - flowX * (particleSpeed * 3);
        const tailY = p.y - flowY * (particleSpeed * 3);

        const fade = Math.sin((p.age / p.maxAge) * Math.PI);
        ctx.globalAlpha = p.alpha * fade * 0.85;

        ctx.beginPath();
        ctx.moveTo(tailX, tailY);
        ctx.lineTo(p.x, p.y);
        ctx.stroke();

        // Advance position
        p.x += flowX * particleSpeed;
        p.y += flowY * particleSpeed;
        p.age++;

        // Wrap around borders or reset if aged
        if (p.age >= p.maxAge || p.x < -20 || p.x > w + 20 || p.y < -20 || p.y > h + 20) {
          p.x = Math.random() * w;
          p.y = Math.random() * h;
          p.age = 0;
          p.maxAge = 60 + Math.floor(Math.random() * 50);
        }
      }

      ctx.restore();

      // Pause animation when tab is not visible to save battery/resources
      if (!document.hidden) {
        animFrameIdRef.current = requestAnimationFrame(render);
      } else {
        setTimeout(() => {
          if (isRunning) animFrameIdRef.current = requestAnimationFrame(render);
        }, 300);
      }
    };

    animFrameIdRef.current = requestAnimationFrame(render);

    return () => {
      isRunning = false;
      if (animFrameIdRef.current) {
        cancelAnimationFrame(animFrameIdRef.current);
        animFrameIdRef.current = null;
      }
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [activeWindPoint]);

  const handleZoomIn = () => mapInstanceRef.current?.zoomIn();
  const handleZoomOut = () => mapInstanceRef.current?.zoomOut();
  const handleRecenter = () => {
    mapInstanceRef.current?.setView([latitude, longitude], 13, { animate: true });
  };

  return (
    <div className="relative w-full h-[520px] rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-md select-none">
      {/* Leaflet Map Target */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Wind Flow Streamline Canvas Overlay */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-10"
      />

      {/* Top Map Controls: Standard / Satellite / Hybrid */}
      <div className="absolute top-4 left-4 z-20 flex bg-white/90 dark:bg-slate-900/90 backdrop-blur-md rounded-xl p-1 shadow-lg border border-slate-200/80 dark:border-slate-700/80">
        <button
          onClick={() => setActiveView('road')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeView === 'road'
              ? 'bg-sky-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          {t('standard_layer')}
        </button>
        <button
          onClick={() => setActiveView('satellite')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeView === 'satellite'
              ? 'bg-sky-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          {t('satellite_layer')}
        </button>
        <button
          onClick={() => setActiveView('hybrid')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeView === 'hybrid'
              ? 'bg-sky-600 text-white shadow-sm'
              : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
          }`}
        >
          {t('hybrid_layer')}
        </button>
      </div>

      {/* Floating Live Vector HUD in Map Corner */}
      <div className="absolute top-4 right-4 z-20 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-3.5 py-2 rounded-xl shadow-lg border border-slate-200/80 dark:border-slate-700/80 flex items-center gap-2.5">
        <div
          className="w-7 h-7 rounded-lg flex items-center justify-center text-white shadow-sm"
          style={{ backgroundColor: getBeaufortLevel(activeWindPoint.windSpeed).color }}
        >
          <Wind className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs font-bold text-slate-800 dark:text-slate-100 flex items-center gap-1.5">
            <span>{activeWindPoint.windSpeed !== null ? `${activeWindPoint.windSpeed} km/h` : '--'}</span>
            <span className="text-slate-400">&bull;</span>
            <span>{activeWindPoint.windDirectionCardinal}</span>
          </div>
          <div className="text-[10px] text-slate-500 dark:text-slate-400">
            {activeWindPoint.windDirection !== null ? `${activeWindPoint.windDirection}° Azimuth` : 'Unavailable'}
          </div>
        </div>
      </div>

      {/* Right Zoom & Recenter Controls */}
      <div className="absolute bottom-6 right-4 z-20 flex flex-col gap-2">
        <button
          onClick={handleRecenter}
          title="Recenter Map"
          className="p-2.5 rounded-xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-md text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 transition"
        >
          <Crosshair className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-2.5 rounded-xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-md text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 transition"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-2.5 rounded-xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-md text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 shadow-md border border-slate-200 dark:border-slate-700 transition"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
      </div>

      {/* Click Hint Bar */}
      <div className="absolute bottom-4 left-4 z-20 hidden sm:flex items-center gap-1.5 bg-slate-900/80 backdrop-blur-md text-white px-3 py-1.5 rounded-lg text-xs shadow-md border border-slate-700/50">
        <MapPin className="w-3.5 h-3.5 text-sky-400" />
        <span>{t('click_map_inspect')}</span>
      </div>
    </div>
  );
};
