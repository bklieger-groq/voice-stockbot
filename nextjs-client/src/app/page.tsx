"use client";
jsx;

import Image from "next/image";
import { useRef, useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { jsx } from "react/jsx-runtime";
import { useMicVAD } from "@ricky0123/vad-react"

import { SkinConfigurations } from "./types/skinConfig";

import { SyncLoader, PulseLoader, ScaleLoader } from "react-spinners";

import StockChart from "./components/tradingview/stock-chart";
import StockPrice from "./components/tradingview/stock-price";
import EtfHeatmap from "./components/tradingview/etf-heatmap";
import MarketHeatmap from "./components/tradingview/market-heatmap";
import MarketOverview from "./components/tradingview/market-overview";
import MarketTrending from "./components/tradingview/market-trending";
import StockFinancials from "./components/tradingview/stock-financials";
import StockNews from "./components/tradingview/stock-news";
import StockScreener from "./components/tradingview/stock-screener";

import xRxClient, { ChatMessage } from "../../../xrx-core/react-xrx-client/src";

interface DataItem {
  date: string;
  value: number;
}

declare global {
  interface Window {
    webkitAudioContext: typeof AudioContext;
  }
}

const NEXT_PUBLIC_ORCHESTRATOR_HOST =
  process.env.NEXT_PUBLIC_ORCHESTRATOR_HOST || "localhost";
const NEXT_PUBLIC_ORCHESTRATOR_PORT =
  process.env.NEXT_PUBLIC_ORCHESTRATOR_PORT || "8000";
const NEXT_PUBLIC_ORCHESTRATOR_PATH =
  process.env.NEXT_PUBLIC_ORCHESTRATOR_PATH || "/api/v1/ws";
const NEXT_PUBLIC_UI_DEBUG_MODE =
  process.env.NEXT_PUBLIC_UI_DEBUG_MODE === "true";
const TTS_SAMPLE_RATE = process.env.TTS_SAMPLE_RATE || "24000";
const STT_SAMPLE_RATE = process.env.STT_SAMPLE_RATE || "16000";
const NEXT_PUBLIC_GREETING_FILENAME = process.env.NEXT_PUBLIC_GREETING_FILENAME || "greeting.mp3";
  
// see SkinConfigurations for available agents
const NEXT_PUBLIC_AGENT = process.env.NEXT_PUBLIC_AGENT || "pizza-agent";
const skinConfig = SkinConfigurations[NEXT_PUBLIC_AGENT];


export default function Home() {

  const {
    // State variables
    isRecording,
    isVoiceMode,
    isUserSpeaking,
    chatHistory,
    isAgentSpeaking,
    isAgentThinking,
    isAudioPlaying,
    showStartButton,
    isAudioGenerationDone,

    // Set functions
    setIsRecording,
    setIsVoiceMode,
    setIsUserSpeaking,
    setChatHistory,
    setIsAgentSpeaking,
    setIsAgentThinking,
    setIsAudioPlaying,
    setShowStartButton,
    setIsAudioGenerationDone,

    // Handler functions
    startAgent,
    toggleIsRecording,
    toggleVoiceMode,
    sendMessage,
    sendAction

  } = xRxClient({
    orchestrator_host: NEXT_PUBLIC_ORCHESTRATOR_HOST,
    orchestrator_port: NEXT_PUBLIC_ORCHESTRATOR_PORT,
    orchestrator_path: NEXT_PUBLIC_ORCHESTRATOR_PATH,
    greeting_filename: NEXT_PUBLIC_GREETING_FILENAME,
    orchestrator_ssl: false,
    stt_sample_rate: parseInt(STT_SAMPLE_RATE, 10),
    tts_sample_rate: parseInt(TTS_SAMPLE_RATE, 10),
  });

  /* Voice Activity Detection */
  useMicVAD({
    startOnLoad: true,
    onSpeechStart: () => {
      console.log("User started talking");
      // if (isRecording){
        setIsUserSpeaking(true);
      // }
    },
    onSpeechEnd: () => {
      console.log("User stopped talking");
      setIsUserSpeaking(false);
    },
  })

  const [message, setMessage] = useState("");
  const [latestWidget, setLatestWidget] = useState<{
    type: string;
    details: string;
  } | null>(null);


  const [loadingButtons, setLoadingButtons] = useState<{
    [key: string]: boolean;
  }>({});
  const [currentPage, setCurrentPage] = useState("welcome");

  /* Click Handlers */
  const handleStartClick = () => {
    startAgent();
    setCurrentPage("home");
  }
  
  const handleRecordClick = () => {
    toggleIsRecording();
  }

  const exportToCSV = (data: DataItem[], filename: string) => {
    // Convert data array to CSV string
    const csvRows = [];
  
    // Get headers (keys from the first object)
    const headers = Object.keys(data[0]) as Array<keyof DataItem>;

    csvRows.push(headers.join(','));
  
    // Loop over the rows
    for (const row of data) {
      const values = headers.map((header: keyof DataItem) => {
        const escaped = ('' + row[header]).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }
  
    // Create a Blob from the CSV string
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
  
    // Create a link to trigger the download
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', `${filename}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };


  const renderWidget = useCallback(() => {
    let widget:any = chatHistory.findLast(chat => chat.type === 'widget')?.message;
    let details: any;
    if (!widget){
      return null;
    }

    try { 
      details = JSON.parse(widget.details);
    } catch (error) {
      console.log("Error: we received invalid json for the widget.");
      console.log(error);
      console.log(widget.details);
      details = [];
    }

    if (Array.isArray(details) && details.length > 0) {

      return details.map((widget, index) => {
        const { type, parameters, data } = widget;
        console.log("Rendering widget: ",type,parameters,data);

        switch (type) {
          case 'showStockPrice':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-price-${index}`}>
                <StockPrice symbol={parameters.symbol} />
              </div>
            );
          case 'showStockChart':
            return (
                <StockChart 
                  symbol={parameters.symbol} 
                  comparisonSymbols={parameters.comparisonSymbols}
                />
            );
          case 'showStockFinancials':
            return (
                <StockFinancials symbol={parameters.symbol} />
            );
          case 'showStockNews':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-news-${index}`}>
                <StockNews symbol={parameters.symbol} />
              </div>
            );
          case 'showStockScreener':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-screener-${index}`}>
                <StockScreener />
              </div>
            );
          case 'showMarketOverview':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-market-overview-${index}`}>
                <MarketOverview />
              </div>
            );
          case 'showMarketHeatmap':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-market-heatmap-${index}`}>
                <MarketHeatmap />
              </div>
            );
          case 'showETFHeatmap':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-etf-heatmap-${index}`}>
                <EtfHeatmap />
              </div>
            );
          case 'showTrendingStocks':
            return (
              <div key={`widget-${index}`} className="widget" id={`stock-trending-stocks-${index}`}>
                <MarketTrending />
              </div>
            );
          case 'showInformation':
            return (
              <div key={`widget-${index}`} className="flex items-center justify-center min-h-[200px]">
                <div className="p-6 rounded-lg shadow-lg max-w-md w-full text-center bg-white border-4 border-orange-500">
                  <h2 className="text-xl font-bold mb-4">{parameters.title}</h2>
                  <p className="text-gray-700">{parameters.content}</p>
                </div>
              </div>
            );
            case 'showSpreadsheet':
      return (
        <div key={`widget-${index}`} className="flex items-center justify-center min-h-[600px]">
      <div className="rounded-lg max-w-4xl w-full bg-white">
        <h2 className="text-xl font-bold mb-2 px-4 py-2 mt-10">
          {parameters.symbol}{" "}{parameters.metric.charAt(0).toUpperCase() + parameters.metric.slice(1)}
        </h2>
        <button
        onClick={() => exportToCSV(data, parameters.metric)}
        className="mb-2 px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-700"
      >
        Download Spreadsheet
      </button>
        <div className="overflow-auto" style={{maxHeight: "60vh"}}>
          <table className="min-w-[50%] text-sm text-left border border-gray-100">
            <thead className="bg-gray-100 border-b border-gray-300">
              <tr>
                <th className="px-2 py-1 font-medium text-gray-700 border-r border-gray-300">Filing Date of 10Q</th>
                <th className="px-2 py-1 font-medium text-gray-700">{parameters.metric.charAt(0).toUpperCase() + parameters.metric.slice(1)} Value</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item: { date: string; value: number }, idx: number) => (
                <tr key={idx} className="border-b border-gray-200">
                  <td className="px-2 py-1 border-r border-gray-300">{item.date}</td>
                  <td className="px-2 py-1">{item.value.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
      );
          default:
            return null;
        }
      });
    }
  }, [chatHistory]);


  useEffect(() => {
    const lastMessage = chatHistory.findLast((chat) => chat.type === "widget");
    if (lastMessage) {
      setLatestWidget(lastMessage.message as any);
    }
    setLoadingButtons({});
  }, [chatHistory]);

  return (
    <main className="mainContainer">
    {showStartButton && (
      <div className="startButtonContainer">
        <button className="widget-button" style={{padding: '10px 30px'}} onClick={handleStartClick}>Start</button>
      </div>
    )}
    <div className="chatContainer flex-auto">
      <div className={`iconContainer flex ${!isVoiceMode ? 'hidden' : ''}`}>
        <SyncLoader
                color={"#F15950"}
                loading={isAgentSpeaking}
                size={20}
                />
        <PulseLoader
            color={"#F15950"}
            loading={isAgentThinking}
            size={20}
            />

        <div style={{
          width: isAgentSpeaking || isAgentThinking ? '0px' : '50px',
          height: isAgentSpeaking || isAgentThinking ? '0px' : '50px',
          borderRadius: '50%',
          backgroundColor: '#F15950',
          transition: 'all 0.5s',
          position: 'absolute',
          left: '50%',
          top: '40',
          transform: isAgentSpeaking || isAgentThinking ? 'translate(-50%, 0) scale(0)' : 'translate(-50%, 0) scale(1)',
          transformOrigin: 'center center'
        }}></div>
        
      </div>
      <div />
<div className="chatMessageContainer flex">
  <div className="widgetMessageContainer">
    <div key="widget" className="chatMessage widgetMessage">
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, calc(50% - 10px)), 1fr))',
      gap: '1rem',
      justifyContent: 'center',
      alignContent: 'center',
      width: '100vw',
      // height: 'calc(100vh - 600px)',
      padding: '3rem',
      boxSizing: 'border-box',
    }}
    className="grid-container">
      {renderWidget()}
      </div>
    </div>
  </div>
</div>
    </div>
    <div className='inputContainer'>
      <div className='flex'>
          <div className="textInputContainer" >
            <div id='speechDetection' style={{ justifyContent: 'center' }}>
              <ScaleLoader
                className="voiceIndicator"
                color={"rgb(var(--foreground-rgb))"}
                loading={isUserSpeaking}
                radius={10}
                height={20}
                width={20}
                speedMultiplier={2}
              />
              <ScaleLoader
                className="voiceIndicator"
                color={"rgb(var(--foreground-rgb))"}
                loading={!isUserSpeaking}
                radius={5}
                height={7}
                width={20}
                speedMultiplier={0.00001}
              />
              <Image
                className="micButton"
                src={isRecording ? "/mic_on.svg" : "/mic_off.svg"}
                width={50}
                height={50}
                alt="Microphone Icon"
                onClick={handleRecordClick}
                style={{ marginLeft: 'auto' }}
              />
            </div>
          </div>
      </div>   
      <div className='speechControls'>
        {NEXT_PUBLIC_UI_DEBUG_MODE && (
          <button className="modeButton" onClick={() => toggleVoiceMode()}>
            <Image
              src={isVoiceMode ? '/chat.svg' : '/mic_on.svg'} 
              width={20} 
              height={10} 
              alt="Microphone Icon"
            />
            <span>{isVoiceMode ? 'Toggle to text mode' : 'Toggle to audio mode'}</span>
          </button>
        )}
      </div>    
    </div>
  </main>
);
}
