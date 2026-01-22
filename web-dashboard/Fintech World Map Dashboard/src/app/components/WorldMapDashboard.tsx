import { useState } from 'react';
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from 'react-simple-maps';
import { CountryTooltip } from './CountryTooltip';

// TopoJSON world map URL
const geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// Country data with revenue information
const countryData = {
  CAN: { name: 'Canada', revenue: 4281, color: '#9DCEDC' },
  DEU: { name: 'Germany', revenue: 2281, color: '#A3B4D4' },
  IND: { name: 'India', revenue: 27360, color: '#B8A7DC' },
  BRA: { name: 'Brazil', revenue: 27360, color: '#8FD4A0' },
  AUS: { name: 'Australia', revenue: 16001, color: '#FFE599' },
};

// Country code to flag emoji mapping
const countryFlags: Record<string, string> = {
  CAN: '🇨🇦',
  DEU: '🇩🇪',
  IND: '🇮🇳',
  BRA: '🇧🇷',
  AUS: '🇦🇺',
};

interface TooltipData {
  name: string;
  revenue: number;
  flag: string;
  x: number;
  y: number;
}

export function WorldMapDashboard() {
  const [hoveredCountry, setHoveredCountry] = useState<TooltipData | null>(null);

  const handleMouseEnter = (geo: any, event: React.MouseEvent) => {
    const countryCode = geo.id;
    const data = countryData[countryCode as keyof typeof countryData];
    
    if (data) {
      const rect = event.currentTarget.getBoundingClientRect();
      setHoveredCountry({
        name: data.name,
        revenue: data.revenue,
        flag: countryFlags[countryCode],
        x: event.clientX,
        y: event.clientY,
      });
    }
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (hoveredCountry) {
      setHoveredCountry({
        ...hoveredCountry,
        x: event.clientX,
        y: event.clientY,
      });
    }
  };

  const handleMouseLeave = () => {
    setHoveredCountry(null);
  };

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center">
      <div className="absolute bottom-8 left-8 text-sm text-gray-500 space-y-1">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-200 rounded-sm" />
          <span>Company</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-200 rounded-sm" />
          <span>Administrator (Hi)</span>
        </div>
      </div>

      <div className="w-full max-w-6xl px-8">
        <ComposableMap
          projection="geoMercator"
          projectionConfig={{
            scale: 140,
            center: [10, 20],
          }}
          style={{
            width: '100%',
            height: 'auto',
          }}
        >
          <ZoomableGroup center={[10, 20]} zoom={1}>
            <Geographies geography={geoUrl}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const countryCode = geo.id;
                  const data = countryData[countryCode as keyof typeof countryData];
                  const isActive = !!data;

                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      onMouseEnter={(event) => handleMouseEnter(geo, event)}
                      onMouseMove={handleMouseMove}
                      onMouseLeave={handleMouseLeave}
                      style={{
                        default: {
                          fill: isActive ? data.color : '#FFFFFF',
                          stroke: '#D1D5DB',
                          strokeWidth: 0.5,
                          outline: 'none',
                        },
                        hover: {
                          fill: isActive ? data.color : '#FFFFFF',
                          stroke: '#D1D5DB',
                          strokeWidth: 0.5,
                          outline: 'none',
                          filter: isActive ? 'drop-shadow(0 4px 6px rgba(0,0,0,0.07))' : 'none',
                          cursor: isActive ? 'pointer' : 'default',
                        },
                        pressed: {
                          fill: isActive ? data.color : '#FFFFFF',
                          stroke: '#D1D5DB',
                          strokeWidth: 0.5,
                          outline: 'none',
                        },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>
      </div>

      {hoveredCountry && <CountryTooltip data={hoveredCountry} />}
    </div>
  );
}

