'use client'

import React, { useEffect, useRef, memo } from 'react';

type ComparisonSymbolObject = {
  symbol: string;
  position: "SameScale";
};

function StockChart({ symbol, comparisonSymbols }: { symbol: string, comparisonSymbols: ComparisonSymbolObject[] }) {
  const container = useRef<HTMLDivElement>(null);
  
  useEffect(
    () => {
    if (!container.current) return
      const script = document.createElement("script");
      script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
      script.type = "text/javascript";
      script.async = true;
      script.innerHTML = `
     {
        "symbol": "${symbol}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "${!comparisonSymbols ? '1' : '2'}",
        "locale": "en",
        "calendar": false,
        "toolbar_bg": "#f1f3f6",
        "withdateranges": true,
        "hide_side_toolbar": ${!!comparisonSymbols},
        "allow_symbol_change": false,
        ${comparisonSymbols ? `"compareSymbols": ${JSON.stringify(comparisonSymbols)},` : ''}
        "hide_top_toolbar": true,
        "save_image": false,
        "studies": [""],
        "show_popup_button": false,
        "popup_width": "1000",
        "popup_height": "650",
        "container_id": "${container.current.id}",
        "hide_volume": ${!!comparisonSymbols}
      }`;
      container.current.replaceChildren(script);
    },
    [symbol, JSON.stringify(comparisonSymbols)]
  );

  return (
    <div className="tradingview-widget-container grid-item" ref={container} style={{ height: "100%", width: "100%" }}>
      <div className="tradingview-widget-container__widget"></div>
      <div className="tradingview-widget-copyright">
          <a
            href="https://www.tradingview.com/"
            rel="noopener nofollow"
            target="_blank"
          >
            <span className="">Track all markets on TradingView</span>
          </a>
        </div>
    </div>
  );
}

export default memo(StockChart)