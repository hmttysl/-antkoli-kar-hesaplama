import { useEffect, useState } from 'react';
import { Building, DollarSign } from 'lucide-react';

interface TooltipData {
  name: string;
  revenue: number;
  flag: string;
  x: number;
  y: number;
}

interface CountryTooltipProps {
  data: TooltipData;
}

export function CountryTooltip({ data }: CountryTooltipProps) {
  const [position, setPosition] = useState({ x: data.x, y: data.y });

  useEffect(() => {
    // Adjust position to prevent tooltip from going off-screen
    const tooltipWidth = 180;
    const tooltipHeight = 120;
    const padding = 20;

    let x = data.x + 15;
    let y = data.y - tooltipHeight / 2;

    // Check if tooltip goes off right edge
    if (x + tooltipWidth > window.innerWidth - padding) {
      x = data.x - tooltipWidth - 15;
    }

    // Check if tooltip goes off top edge
    if (y < padding) {
      y = padding;
    }

    // Check if tooltip goes off bottom edge
    if (y + tooltipHeight > window.innerHeight - padding) {
      y = window.innerHeight - tooltipHeight - padding;
    }

    setPosition({ x, y });
  }, [data.x, data.y]);

  // Format revenue with dots as thousand separators
  const formatRevenue = (value: number) => {
    return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  };

  return (
    <div
      className="fixed pointer-events-none z-50"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      <div className="bg-white rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.08)] p-3.5 min-w-[170px]">
        <div className="flex items-center gap-2 mb-2.5">
          <div className="text-xl">{data.flag}</div>
          <span className="font-medium text-gray-900 text-sm">{data.name}</span>
        </div>
        
        <div className="space-y-1.5">
          <div className="text-xs text-gray-500">Toplam Ciro</div>
          <div className="text-base font-semibold text-gray-900">
            ₺ {formatRevenue(data.revenue)}
          </div>
        </div>
      </div>
    </div>
  );
}
