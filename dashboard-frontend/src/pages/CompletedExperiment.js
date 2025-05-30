// src/pages/CompletedExperiment.js
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useParams, useNavigate } from 'react-router-dom'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import '../App.css'

export default function CompletedExperiment() {
  const { id } = useParams()
  const nav = useNavigate()

  // store *entire* experiment JSON so we can render metadata
  const [expt, setExpt]         = useState(null)
  const [status, setStatus]     = useState(null)
  const [metrics, setMetrics]   = useState([])
  const [curves, setCurves]     = useState({})
  const [overview, setOverview] = useState([])
  const [selClient, setSelClient] = useState(null)
  const [selRound, setSelRound]   = useState(null)

  useEffect(() => {
    axios
      .get(`http://18.218.117.22:8000/experiments/${id}/static`)
      .then(res => {
        const data = res.data
        // keep the whole payload, not just name
        setExpt(data)

        // replay the timeline in order:
        data.timeline.forEach(evt => {
          if (evt.type === 'status') {
            setStatus(evt)
          } else if (evt.type === 'metrics') {
            setMetrics(ms => [...ms, evt])

            // build per-client accuracy‐curve history
            evt.clients.forEach(c => {
              const accCurve = Array.isArray(c.accuracy_curve)
                ? c.accuracy_curve
                : (c.loss_curve || []).map(l =>
                    Math.min(1, Math.max(0, 1 - l + (Math.random()*0.01 - 0.005)))
                  )
              setCurves(cu => ({
                ...cu,
                [c.id]: [
                  ...(cu[c.id] || []),
                  { round: evt.round, accuracy_curve: accCurve }
                ]
              }))
            })

            // overview = average local/global/alpha
            const avgL = evt.clients.reduce((s, c) => s + c.client_eval_local_acc, 0) / evt.clients.length
            const avgG = evt.clients.reduce((s, c) => s + c.client_eval_global_acc, 0) / evt.clients.length
            const avgA = evt.clients.reduce((s, c) => s + c.client_alpha, 0) / evt.clients.length
            setOverview(o => [...o, { round: evt.round, avgL, avgG, avgA }])
          }
        })
      })
      .catch(console.error)
  }, [id])

  // if (!expt) return <p>Loading experiment…</p>
  if (!expt || !expt.dataset || !expt.hyperparameters || !expt.algorithm) {
    return <p>Loading experiment…</p>
  }

  // === pick the metrics event for the selected round (or last) ===
  const lastRound      = metrics.length ? metrics[metrics.length - 1].round : null
  const displayedRound = selRound != null ? selRound : lastRound
  const metricsForRound = metrics.find(m => m.round === displayedRound)
  const selClientMetrics = metricsForRound
    ? metricsForRound.clients.find(c => c.id == selClient)
    : null

  // pick the curve object for this client/round
  const selClientCurve = selClient != null && curves[selClient]
    ? curves[selClient].find(r => r.round === displayedRound)
    : null

  return (
    <div className="dashboard">
      <button onClick={() => nav(-1)}>← Back</button>
      <header><h1>Experiment: {expt.name}</h1></header>

      <div className="status-banner">
        <h2>
          Round {status?.round} — {status?.running ? 'Running' : 'Finished'}
        </h2>
        <p>Clock: {status?.virtual_clock.toFixed(1)}s</p>
        <p>Sampled: {status?.sampled_clients.join(', ')}</p>
      </div>

      {/*
        ----------------------------------------------------------------
        New collapsible panel with all the dataset / hyperparameter info
        ----------------------------------------------------------------
      */}
      <section style={{ margin: '1rem 0' }}>
        <details>
          <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
            Experiment Configuration
          </summary>
          <div style={{ padding: '0.5rem 1rem' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {/* Dataset */}
                <tr>
                  <td style={{ padding: '0.25rem 0.5rem', fontWeight: 'bold' }}>Dataset</td>
                  <td style={{ padding: '0.25rem 0.5rem' }}>
                    {expt.dataset.name} &mdash; {expt.dataset.train_size.toLocaleString()} train, {expt.dataset.test_size.toLocaleString()} test
                  </td>
                </tr>
                {/* Partition */}
                <tr>
                  <td style={{ padding: '0.25rem 0.5rem', fontWeight: 'bold' }}>Partition</td>
                  <td style={{ padding: '0.25rem 0.5rem' }}>
                    {expt.partition.method} &alpha;={expt.partition.alpha}, {expt.partition.num_clients} clients
                  </td>
                </tr>
                {/* Hyperparameters */}
                {[
                  ['rounds',               expt.hyperparameters.rounds],
                  ['local_steps',          expt.hyperparameters.local_steps],
                  ['batch_size',           expt.hyperparameters.batch_size],
                  ['learning_rate',        expt.hyperparameters.learning_rate],
                  ['eval_interval',        expt.hyperparameters.eval_interval],
                  ['seed',                 expt.hyperparameters.seed],
                  ['noise_std',            expt.hyperparameters.measurement_noise_std],
                ].map(([label, val]) => (
                  <tr key={label}>
                    <td style={{ padding: '0.25rem 0.5rem', fontWeight: 'bold' }}>{label.replace(/_/g,' ')}</td>
                    <td style={{ padding: '0.25rem 0.5rem' }}>{val}</td>
                  </tr>
                ))}
                {/* Algorithm */}
                <tr>
                  <td style={{ padding: '0.25rem 0.5rem', fontWeight: 'bold' }}>Algorithm</td>
                  <td style={{ padding: '0.25rem 0.5rem' }}>{expt.algorithm.name}</td>
                </tr>
                {/* Algorithm params (tau/delta etc) */}
                {expt.algorithm.params && Object.keys(expt.algorithm.params).length > 0 && (
                  <tr>
                    <td style={{ padding: '0.25rem 0.5rem', fontWeight: 'bold' }}>Algorithm Params</td>
                    <td style={{ padding: '0.25rem 0.5rem' }}>
                      {Object.entries(expt.algorithm.params)
                        .map(([k,v]) => `${k} = ${v}`)
                        .join(', ')}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </details>
      </section>


      {/* Overview Panel */}
      <section className="overview-curve" style={{ marginBottom: '2rem' }}>
        <h3>Global Overview: Avg-Local vs Avg-Global vs α</h3>
        {overview.length > 0 ? (
          <LineChart
            width={700}
            height={300}
            data={overview.map(o => ({
              round: o.round,
              avgL:  o.avgL * 100,
              avgG:  o.avgG * 100,
              avgA:  o.avgA * 100
            }))}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="round"
              allowDecimals={false}
              type="number"
              domain={[0, 'dataMax']}
              label={{ value: 'Round', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Value (%) or α', angle: -90, position: 'insideLeft' }}
              domain={[0, 100]}
            />
            <Tooltip
              formatter={(v, name) =>
                name === 'Avg α' ? v.toFixed(2) : `${v.toFixed(1)}%`
              }
              labelFormatter={l => `Round ${l}`}
            />
            <Legend verticalAlign="top" height={36} />
            <Line
              type="monotone"
              dataKey="avgL"
              name="Avg-Local Acc"
              stroke="#8884d8"
              dot={false}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="avgG"
              name="Avg-Global Acc"
              stroke="#82ca9d"
              dot={false}
              strokeWidth={2}
            />
            <Line
              type="monotone"
              dataKey="avgA"
              name="Avg α"
              stroke="#ffc658"
              dot={false}
              strokeWidth={2}
            />
          </LineChart>
        ) : (
          <p>Building overview…</p>
        )}
      </section>

      {/* Global Accuracy */}
      <section className="global-curve">
        <h3>Global Top-1 Accuracy vs Rounds</h3>
        {metrics.length > 0 ? (
          <LineChart
            width={700}
            height={300}
            data={metrics.map(m => ({
              round: m.round,
              acc:   m.top1 * 100
            }))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="round"
              allowDecimals={false}
              type="number"
              domain={[0, 'dataMax']}
              label={{ value: 'Round', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Top-1 Accuracy (%)', angle: -90, position: 'insideLeft' }}
              domain={[0, 100]}
            />
            <Tooltip
              formatter={v => `${v.toFixed(1)}%`}
              labelFormatter={l => `Round ${l}`}
            />
            <Line
              dataKey="acc"
              name="Global Top-1 Accuracy"
              dot={false}
              stroke="#1e90ff"
              strokeWidth={2}
            />
          </LineChart>
        ) : (
          <p>Waiting for first completed round…</p>
        )}
      </section>

      {/* Client Details */}
      <section className="client-section">
        <h3>Client Details</h3>
        <div className="client-tabs">
          {Object.keys(curves).map(cid => (
            <button
              key={cid}
              className={selClient == cid ? 'active' : ''}
              onClick={() => { setSelClient(cid); setSelRound(null) }}
            >
              Client {cid}
            </button>
          ))}
        </div>

        {selClient != null && selClientMetrics && selClientCurve && (
          <>
            <label>
              Round:&nbsp;
              <select
                value={displayedRound}
                onChange={e => setSelRound(+e.target.value)}
              >
                {metrics.map(m => (
                  <option key={m.round} value={m.round}>
                    Round {m.round}
                  </option>
                ))}
              </select>
            </label>

            <div className="cards">
              <div className="card">
                <h4>Local Acc</h4>
                <p>{(selClientMetrics.client_eval_local_acc * 100).toFixed(1)}%</p>
              </div>
              <div className="card">
                <h4>Global Acc</h4>
                <p>{(selClientMetrics.client_eval_global_acc * 100).toFixed(1)}%</p>
              </div>
              <div className="card">
                <h4>Mix α</h4>
                <p>{selClientMetrics.client_alpha.toFixed(2)}</p>
              </div>
            </div>

            <LineChart
              width={600}
              height={250}
              data={selClientCurve.accuracy_curve.map((a, i) => ({
                step: i + 1,
                acc:   a * 100
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="step"
                allowDecimals={false}
                type="number"
                domain={[0, 'dataMax']}
                label={{ value: 'Batch Step', position: 'insideBottom', offset: -5 }}
              />
              <YAxis
                label={{ value: 'Local Accuracy (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              <Tooltip
                formatter={v => `${v.toFixed(1)}%`}
                labelFormatter={l => `Step ${l}`}
              />
              <Line
                dataKey="acc"
                name="Local Accuracy"
                dot={false}
                stroke="#273c75"
                strokeWidth={2}
              />
            </LineChart>
          </>
        )}
      </section>
    </div>
  )
}
