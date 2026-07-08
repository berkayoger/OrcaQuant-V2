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
  disclaimer: string;
  market_overview: MarketOverview;
  radar: RadarItem[];
  assets: CockpitAsset[];
  personas: Persona[];
};

const fallbackCockpit: CockpitPayload = {
  module: "market_cockpit",
  status: "frontend_fallback",
  investment_advice: false,
  data_source: "frontend_fallback_until_api_connects",
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
      top_risk: "Risk orta bölgede; piyasa genel yönüyle doğrulanmalı."
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
      top_risk: "Piyasa ani yön değiştirebilir."
    }
  ],
  assets: [],
  personas: [
    { key: "pro_analyst", title: "Analiz bilen kullanıcı", value: "Teknik, hacim ve risk verilerini tek kokpitte görür." },
    { key: "new_investor", title: "Analiz bilmeyen yatırımcı", value: "Sinyalleri sade risk/avantaj dilinde okur." },
    { key: "opportunity_hunter", title: "Fırsat arayan kullanıcı", value: "Orca Radar yeni izlenebilir varlıkları öne çıkarır." }
  ]
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

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

export default function DashboardPage() {
  const [cockpit, setCockpit] = useState<CockpitPayload>(fallbackCockpit);
  const [loading, setLoading] = useState(true);
  const [apiState, setApiState] = useState<"live" | "fallback">("fallback");

  useEffect(() => {
    let cancelled = false;

    async function loadCockpit() {
      try {
        const response = await fetch(`${API_BASE_URL}/dashboard/`);
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
  }, []);

  const assets = useMemo(() => cockpit.assets.length ? cockpit.assets : cockpit.radar.map((item) => ({
    ...item,
    theme: "MVP radar",
    price: 0,
    volume_score: item.technical_score,
    plain_language_summary: item.summary,
    advantages: [item.top_advantage],
    risks: [item.top_risk]
  })), [cockpit.assets, cockpit.radar]);

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
        </div>
      </section>

      <section className="oq-grid oq-grid-4">
        <MetricCard label="Piyasa modu" value={regimeLabel(cockpit.market_overview.regime)} helper={cockpit.data_source.replaceAll("_", " ")} />
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
            </div>
            <div className="oq-score-block">
              <span>{item.label}</span>
              <strong>{scoreText(item.opportunity_score)}</strong>
              <small>{riskLabel(item.risk_level)} · {formatChange(item.change_24h_pct)}</small>
            </div>
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
            <div className="oq-asset-metrics">
              <span>Teknik {scoreText(asset.technical_score)}</span>
              <span>Risk {scoreText(asset.risk_score)}</span>
              <span>{formatChange(asset.change_24h_pct)}</span>
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
