'use client'

import React, { useEffect, useRef, memo } from 'react'

export function StockNews({ symbol }: { symbol: string }) {
  const container = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!container.current) return
    const script = document.createElement('script')
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-timeline.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = `
      {
        "feedMode": "symbol",
        "symbol": "${symbol}",
        "isTransparent": true,
        "displayMode": "regular",
        "colorTheme": "light",
        "locale": "en"
        }`

    container.current.replaceChildren(script)

    return () => {
      if (container.current) {
        const scriptElement = container.current.querySelector('script')
        if (scriptElement) {
          container.current.removeChild(scriptElement)
        }
      }
    }
  }, [symbol])

  return (
      <div className="tradingview-widget-container" ref={container} style={{ height: "60vh" }}>
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
  )
}

export default memo(StockNews)