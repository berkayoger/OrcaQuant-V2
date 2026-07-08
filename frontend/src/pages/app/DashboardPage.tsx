import { useEffect, useMemo, useState } from "react";

type MarketRegime = "risk_on" | "mixed" | "risk_off";

type MarketOverview = {
  regime: MarketRegime;
  technical_health: number;
  risk_pressure: number;
  volume_heat: number;
  summary: string;
  watchpoints: string[];
};

type RadarSignal = {
  type: string;
  label: string;
  severity: "positive" | "warning" | "danger" | "info" | "neutral";
};

type AlertSuggestion = {
  symbol: string;
  metric: string;
  condition: string;
  threshold: number;
  title: string;
};

type RadarItem = {
  symbol: string;
  name: string;
  label: string;
  opportunity_score: number;
  risk_level: string;
  risk_score: number;
  technical_score: number;
  change_24h_pct: number;
  summary: string;
  top_advantage: string;
  top_risk: string;
  signals: RadarSignal[];
  suggested_alerts: AlertSuggestion[];
  is_watchlisted: boolean;
  data_source: string;
};

type CockpitAsset = RadarItem & {
  theme: string;
  price: number;
  volume_score: number;
  plain_language_summary: string;
  advantages: string[];
  risks: string[];
};

type Persona = {
  key: string;
  title: string;
  value: string;
};

type CockpitPayload = {
  module: string;
  status: string;
  investment_advice: boolean;
  data_source: string;
  provider_sources?: string[];
  disclaimer: string;
  market_overview: MarketOverview;
  radar: RadarItem[];
  watchlist_focus?: RadarItem[];
  suggested_alerts: AlertSuggestion[];
  assets: CockpitAsset[];
  personas: Persona[];
};

const fallbackSignals: RadarSignal[] = [
  { type: "trend_continuation", label: "Trend devamı", severity: "positive" },
  { type: "neutral_watch", label: "Nötr izleme", severity: "neutral" }
];

const fallbackAlerts: AlertSuggestion[] = [
  { symbol: "SOL", metric: "opportunity_score", condition: ">=", threshold: 80, title: "SOL fırsat skoru güçlenirse haber ver" },
  { symbol: "BTC", metric: "risk_score", condition: ">=", threshold: 65, title: "BTC risk baskısı yükselirse uyar" }
];

const fallbackCockpit: CockpitPayload = {
  module: "market_cockpit",
  status: "frontend_fallback",
  investment_advice: false,
  data_source: "frontend_fallback_until_api_connects",
  provider_sources: ["frontend_fallback"],
  disclaimer: "OrcaQuant yatırım tavsiyesi vermez; riskleri, avantajları ve izlenebilir sinyalleri karar desteği olarak açıklar.",
  market_overview: {
    regime: "mixed",
    technical_health: 64,
    risk_pressure: 48,
    volume_heat: 57,
    summary: "Piyasa karışık modda. İlk MVP ekranı API bağlantısı kurulana kadar örnek kokpit verisiyle çalışır.",
    watchpoints: [
      "BTC yönü ve piyasa genel risk iştahı birlikte takip edilmeli.",
      "Hacim artışı tek başına fırsat değildir; trend ve oynaklıkla birlikte okunmalı.",
      "Yüksek fırsat skoru, düşük risk anlamına gelmez; risk seviyesi ayrı değerlendirilir."
    ]
  },
  radar: [
    {
      symbol: "SOL",
      name: "Solana",
      label: "Riskli fırsat",
      opportunity_score: 76,
      risk_level: "medium",
      risk_score: 58,
      technical_score: 72,
      change_24h_pct: 2.4,
      summary: "SOL radarın üst sıralarında; trend yapısı canlı ama risk orta bölgede.",
      top_advantage: "Hacim tarafında ortalamanın üzerinde ilgi var.",
      top_risk: "Risk orta bölgede; piyasa genel yönüyle doğrulanmalı.",
      signals: fallbackSignals,
      suggested_alerts: [fallbackAlerts[0]],
      is_watchlisted: false,
      data_source: "frontend_fallback"
    },
    {
      symbol: "BTC",
      name: "Bitcoin",
      label: "İzlenebilir",
      opportunity_score: 68,
      risk_level: "low",
      risk_score: 34,
      technical_score: 66,
      change_24h_pct: 0.8,
      summary: "BTC izlenebilir bölgede; piyasa yön filtresi olarak takip edilmeli.",
      top_advantage: "Trend yapısı destekleniyor.",
      top_risk: "Piyasa ani yön değiştirebilir.",
      signals: fallbackSignals,
      suggested_alerts: [fallbackAlerts[1]],
      is_watchlisted: false,
      data_source: "frontend_fallback"
    }
  ],
  watchlist_focus: [],
  suggested_alerts: fallbackAlerts,
  assets: [],
  personas: [
    { key: "pro_analyst", title: "Analiz bilen kullanıcı", value: "Teknik, hacim ve risk verilerini tek kokpitte görür." },
    { key: "new_investor", title: "Analiz bilmeyen yatırımcı", value: "Sinyalleri sade risk/avantaj dilinde okur." },
    { key: "opportunity_hunter", title: "Fırsat arayan kullanıcı", value: "Orca Radar yeni izlenebilir varlıkları öne çıkarır." }
  ]
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";
const WATCHLIST_KEY = "orcaquant.watchlist.symbols";
const LOCAL_ALERTS_KEY = "orcaquant.local.alerts";

function loadStoredWatchlist() {
  if (typeof localStorage === "undefined") return ["BTC", "SOL"];
  try {
    const parsed = JSON.parse(localStorage.getItem(WATCHLIST_KEY) || "[]") as string[];
    return parsed.length ? parsed : ["BTC", "SOL"];
  } catch {
    return ["BTC", "SOL"];
  }
}

function scoreText(score: number) {
  return `${Math.round(score)}/100`;
}

function regimeLabel(regime: MarketRegime) {
  if (regime === "risk_on") return "Risk-on";
  if (regime === "risk_off") return "Risk-off";
  return "Karışık piyasa";
}

function riskLabel(level: string) {
  if (level === "high") return "Yüksek risk";
  if (level === "medium") return "Orta risk";
  return "Düşük risk";
}

function formatChange(value: number) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function normalizeSymbol(symbol: string) {
  return symbol.toUpperCase().replace(/[^A-Z0-9]/g, "");
}

export default function DashboardPage() {
  const [cockpit, setCockpit] = useState<CockpitPayload>(fallbackCockpit);
  const [loading, setLoading] = useState(true);
  const [apiState, setApiState] = useState<"live" | "fallback">("fallback");
  const [watchlist, setWatchlist] = useState<string[]>(loadStoredWatchlist);
  const [symbolInput, setSymbolInput] = useState("");
  const [localAlertCount, setLocalAlertCount] = useState(() => {
    if (typeof localStorage === "undefined") return 0;
    try {
      return (JSON.parse(localStorage.getItem(LOCAL_ALERTS_KEY) || "[]") as AlertSuggestion[]).length;
    } catch {
      return 0;
    }
  });

  useEffect(() => {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(WATCHLIST_KEY, JSON.stringify(watchlist));
    }
  }, [watchlist]);

  useEffect(() => {
    let cancelled = false;

    async function loadCockpit() {
      try {
        setLoading(true);
        const query = watchlist.length ? `?watchlist=${encodeURIComponent(watchlist.join(","))}` : "";
        const response = await fetch(`${API_BASE_URL}/dashboard/${query}`);
        if (!response.ok) throw new Error(`Dashboard API failed: ${response.status}`);
        const payload = (await response.json()) as CockpitPayload;
        if (!cancelled) {
          setCockpit(payload);
          setApiState("live");
        }
      } catch {
        if (!cancelled) {
          setCockpit(fallbackCockpit);
          setApiState("fallback");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadCockpit();
    return () => { cancelled = true; };
  }, [watchlist]);

  const assets = useMemo(() => cockpit.assets.length ? cockpit.assets : cockpit.radar.map((item) => ({
    ...item,
    theme: "MVP radar",
    price: 0,
    volume_score: item.technical_score,
    plain_language_summary: item.summary,
    advantages: [item.top_advantage],
    risks: [item.top_risk]
  })), [cockpit.assets, cockpit.radar]);

  const watchlistSet = useMemo(() => new Set(watchlist), [watchlist]);
  const watchlistFocus = cockpit.watchlist_focus && cockpit.watchlist_focus.length ? cockpit.watchlist_focus : cockpit.radar.filter((item) => watchlistSet.has(item.symbol));

  function toggleWatchlist(symbol: string) {
    const clean = normalizeSymbol(symbol);
    setWatchlist((current) => current.includes(clean) ? current.filter((item) => item !== clean) : [...current, clean].slice(0, 12));
  }

  function addSymbol() {
    const clean = normalizeSymbol(symbolInput);
    if (!clean) return;
    setWatchlist((current) => current.includes(clean) ? current : [...current, clean].slice(0, 12));
    setSymbolInput("");
  }

  function saveLocalAlert(alertSuggestion: AlertSuggestion) {
    if (typeof localStorage === "undefined") return;
    const existing = JSON.parse(localStorage.getItem(LOCAL_ALERTS_KEY) || "[]") as AlertSuggestion[];
    const next = [...existing, alertSuggestion];
    localStorage.setItem(LOCAL_ALERTS_KEY, JSON.stringify(next));
    setLocalAlertCount(next.length);
  }

  return (
    <main className="oq-page">
      <section className="oq-hero">
        <div>
          <p className="oq-kicker">OrcaQuant Market Cockpit</p>
          <h1>Fırsatları, riskleri ve piyasa nabzını tek ekranda yakala.</h1>
          <p className="oq-subtitle">
            Analiz bilenler için veri kokpiti; analiz bilmeyenler için sade risk/avantaj çevirmeni; fırsat arayanlar için Orca Radar.
          </p>
        </div>
        <div className="oq-status-card">
          <span className={`oq-dot oq-dot-${apiState}`} />
          <strong>{apiState === "live" ? "API bağlı" : "Fallback mod"}</strong>
          <small>{loading ? "Kokpit yükleniyor..." : cockpit.status}</small>
          <small>{localAlertCount} yerel alarm taslağı</small>
        </div>
      </section>

      <section className="oq-grid oq-grid-4">
        <MetricCard label="Piyasa modu" value={regimeLabel(cockpit.market_overview.regime)} helper={cockpit.data_source.replace(/_/g, " ")} />
        <MetricCard label="Teknik sağlık" value={scoreText(cockpit.market_overview.technical_health)} helper="Trend + momentum özeti" />
        <MetricCard label="Risk baskısı" value={scoreText(cockpit.market_overview.risk_pressure)} helper="Oynaklık ve uç sinyal filtresi" />
        <MetricCard label="Hacim ısısı" value={scoreText(cockpit.market_overview.volume_heat)} helper="Radar hareketliliği" />
      </section>

      <section className="oq-panel oq-overview">
        <div>
          <p className="oq-section-label">Bugünün piyasa özeti</p>
          <h2>{cockpit.market_overview.summary}</h2>
          <p className="oq-disclaimer">{cockpit.disclaimer}</p>
        </div>
        <ul>
          {cockpit.market_overview.watchpoints.map((watchpoint) => (
            <li key={watchpoint}>{watchpoint}</li>
          ))}
        </ul>
      </section>

      <section className="oq-panel oq-watchlist-panel">
        <div>
          <p className="oq-section-label">Kişisel takip listesi</p>
          <h2>Takip etmekten yorulduğun varlıkları kokpite sabitle.</h2>
          <div className="oq-watchlist-input">
            <input value={symbolInput} onChange={(event) => setSymbolInput(event.target.value)} placeholder="Örn. ETH" onKeyDown={(event) => { if (event.key === "Enter") addSymbol(); }} />
            <button onClick={addSymbol}>Takibe al</button>
          </div>
          <div className="oq-watchlist-chips">
            {watchlist.map((symbol) => <button key={symbol} onClick={() => toggleWatchlist(symbol)}>{symbol} ×</button>)}
          </div>
        </div>
        <div>
          <p className="oq-section-label">Watchlist odağı</p>
          {watchlistFocus.length ? watchlistFocus.map((item) => (
            <div className="oq-mini-row" key={item.symbol}>
              <strong>{item.symbol}</strong>
              <span>{item.label}</span>
              <small>{scoreText(item.opportunity_score)}</small>
            </div>
          )) : <p className="oq-muted">Henüz takip edilen varlık yok.</p>}
        </div>
      </section>

      <section className="oq-section-heading">
        <div>
          <p className="oq-section-label">Orca Radar</p>
          <h2>Yeni avantajları ve izlenebilir varlıkları öne çıkar.</h2>
        </div>
      </section>

      <section className="oq-radar-list">
        {cockpit.radar.map((item, index) => (
          <article className="oq-radar-card" key={item.symbol}>
            <div className="oq-rank">#{index + 1}</div>
            <div className="oq-radar-main">
              <div>
                <strong>{item.symbol}</strong>
                <span>{item.name}</span>
              </div>
              <p>{item.summary}</p>
              <div className="oq-signal-row">
                {item.signals.map((signal) => <span className={`oq-signal oq-signal-${signal.severity}`} key={`${item.symbol}-${signal.type}`}>{signal.label}</span>)}
              </div>
            </div>
            <div className="oq-score-block">
              <span>{item.label}</span>
              <strong>{scoreText(item.opportunity_score)}</strong>
              <small>{riskLabel(item.risk_level)} · {formatChange(item.change_24h_pct)}</small>
              <button onClick={() => toggleWatchlist(item.symbol)}>{watchlistSet.has(item.symbol) ? "Takipten çıkar" : "Takibe al"}</button>
            </div>
          </article>
        ))}
      </section>

      <section className="oq-section-heading">
        <div>
          <p className="oq-section-label">Alarm önerileri</p>
          <h2>Sürekli takip etmek yerine önemli değişimlere alarm kur.</h2>
        </div>
      </section>

      <section className="oq-grid oq-grid-3 oq-alert-grid">
        {cockpit.suggested_alerts.slice(0, 6).map((alertSuggestion) => (
          <article className="oq-alert-card" key={`${alertSuggestion.symbol}-${alertSuggestion.metric}-${alertSuggestion.threshold}`}>
            <span>{alertSuggestion.symbol}</span>
            <h3>{alertSuggestion.title}</h3>
            <p>{alertSuggestion.metric} {alertSuggestion.condition} {alertSuggestion.threshold}</p>
            <button onClick={() => saveLocalAlert(alertSuggestion)}>Alarm taslağı oluştur</button>
          </article>
        ))}
      </section>

      <section className="oq-section-heading">
        <div>
          <p className="oq-section-label">Risk / avantaj çevirmeni</p>
          <h2>Teknik sinyali insan diline çevir.</h2>
        </div>
      </section>

      <section className="oq-grid oq-grid-asset">
        {assets.map((asset) => (
          <article className="oq-asset-card" key={asset.symbol}>
            <header>
              <div>
                <span className="oq-chip">{asset.theme}</span>
                <h3>{asset.symbol} <small>{asset.name}</small></h3>
              </div>
              <strong>{scoreText(asset.opportunity_score)}</strong>
            </header>
            <p>{asset.plain_language_summary}</p>
            <div className="oq-signal-row">
              {asset.signals.map((signal) => <span className={`oq-signal oq-signal-${signal.severity}`} key={`${asset.symbol}-${signal.type}`}>{signal.label}</span>)}
            </div>
            <div className="oq-asset-metrics">
              <span>Teknik {scoreText(asset.technical_score)}</span>
              <span>Risk {scoreText(asset.risk_score)}</span>
              <span>{formatChange(asset.change_24h_pct)}</span>
              <span>{asset.data_source.replace(/_/g, " ")}</span>
            </div>
            <div className="oq-two-col">
              <div>
                <h4>Avantajlar</h4>
                <ul>{asset.advantages.map((advantage) => <li key={advantage}>{advantage}</li>)}</ul>
              </div>
              <div>
                <h4>Riskler</h4>
                <ul>{asset.risks.map((risk) => <li key={risk}>{risk}</li>)}</ul>
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="oq-grid oq-grid-3 oq-personas">
        {cockpit.personas.map((persona) => (
          <article key={persona.key}>
            <h3>{persona.title}</h3>
            <p>{persona.value}</p>
          </article>
        ))}
      </section>
    </main>
  );
}

function MetricCard({ label, value, helper }: { label: string; value: string; helper: string }) {
  return (
    <article className="oq-metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{helper}</small>
    </article>
  );
}
