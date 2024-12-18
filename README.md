<h2 align="center">
 <br>
 <img src="https://i.imgur.com/f1C7EdN.png" alt="AI Voice StockBot Powered by Groq with Tool Use and Generative UI" width="250">
 <br>
 <br>
Talk to Alice, an AI Voice Agent Providing Real-Time Stock Market Answers with Interactive Charts, Spreadsheets, and More!
 <br>
</h2>

<p align="center">
 <a href="#Overview">Overview</a> •
 <a href="#Features">Features</a> •
  <a href="#Interfaces">Interfaces</a> •
 <a href="#Quickstart">Quickstart</a> •
 <a href="#Credits">Credits</a>
</p>

<br>


https://github.com/user-attachments/assets/3bcd4562-5a14-42fd-a89c-164bccdf76d5


## Overview

Voice StockBot is an AI-powered voice chatbot that leverages 8090's xRx framework, Whisper and Llama3 70b on Groq, TTS on Elevenlabs, Polygon.io's stock API, and TradingView’s live widgets to respond in conversation with the user with live, interactive charts and interfaces specifically tailored to your requests. Groq's speed makes tool calling and providing a response near instantaneous, allowing for a sequence of two API calls with separate specialized prompts to return a response.

> [!IMPORTANT]
>  Note: StockBot may provide inaccurate information and does not provide investment advice. It is for entertainment and instructional use only.

## Features

- 🤖 **Real-time AI Voice Chatbot**: Engage with AI powered by Llama3 70b to request stock news, information, and charts through talking directly with the agent
- 📊 **Interactive Stock Charts**: Receive near-instant, context-aware responses with interactive TradingView charts that host live data
- 🔄 **Adaptive Interface**: Dynamically render TradingView UI components for financial interfaces tailored to your specific query
- ⚡ **Groq-Powered Performance**: Leverage Groq's cutting-edge inference technology for near-instantaneous responses and seamless user experience
- 🌐 **Multi-Asset Market Coverage**: Access comprehensive data and analysis across stocks, forex, bonds, and cryptocurrencies

## Example Interfaces
| Description | Widget |
|-------------|--------|
| **Breakdown of Financial Data for Stocks**<br>Get detailed financial metrics and key performance indicators for any stock. | ![Breakdown of Financial Data for Stocks](https://github.com/user-attachments/assets/272dfae2-4911-43c1-8fdc-e7af0fa9ff1d) |
| **Show Current Price of Stocks**<br>Track and compare the price of stocks over the past day. | ![Price of Stocks](https://github.com/user-attachments/assets/eaf06277-ed76-4220-a164-a06d878bacbd) |
| **Financial Data in Spreadsheets**<br>Create spreadsheets of financial data for any public company | ![Financial Data](https://github.com/user-attachments/assets/697adbbe-98a8-4ba2-a412-0e291e0d5aff) |
| **Compare Price History of Company With Industry Competitors**<br>Track and compare the historical prices of companies in the same industry together. | ![Price History of Stocks](https://github.com/user-attachments/assets/27fe8f31-a64f-4cb7-8f48-c64589400cd1) |
| **Heatmap of Daily Market Performance**<br>Visualize market trends at a glance with an interactive heatmap. | ![Heatmap of Daily Market Performance](https://github.com/user-attachments/assets/3e22d79b-b07c-4f9a-bc59-c93d6c27c3da) |
## Quickstart (To-do)

> [!IMPORTANT]
> To use StockBot, you can use a hosted version at [groq-stockbot.vercel.app](https://groq-stockbot.vercel.app/).
> Alternatively, you can run StockBot locally using the quickstart instructions.


You will need a Groq API Key to run the application. You can obtain one [here on the Groq console](https://console.groq.com/keys).

To get started locally, you can run the following:

```bash
cp .env.example .env.local
```

Add your Groq API key to .env.local, then run:

```bash
pnpm install
pnpm dev
```

Your app should now be running on [localhost:3000](http://localhost:3000/).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) to see the latest changes and versions. Major versions are archived.

## Credits

This app was developed by [Benjamin Klieger](https://x.com/benjaminklieger) at [Groq](https://groq.com) and uses the xRx framework created by 8090 Solutions: [Github Repository](https://github.com/8090-inc/xrx-core).
