import React, { useState, useEffect, useRef } from 'react'
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

export default function ExperimentDetail() {
  const { id } = useParams()
  const nav = useNavigate()

  const [expt, setExpt]       = useState(null)
  const [status, setStatus]   = useState(null)
  const [metrics, setMetrics] = useState([])
  const [curves, setCurves]   = useState({})
  const [overview, setOverview] = useState([])
  const [selClient, setSelClient] = useState(null)
  const [selRound,   setSelRound]   = useState(null)

  useEffect(() => {
    axios
      .get(`http://localhost:8000/experiments/${id}/static`)
      .then(r => {
        const data = r.data
        setExpt({ name: data.name })

        // replay the timeline in order:
        data.timeline.forEach(evt => {
          if (evt.type === 'status') {
            setStatus(evt)
          } else if (evt.type === 'metrics') {
            setMetrics(ms => [...ms, evt])

            // build per-client loss‐curve history
            evt.clients.forEach(c => {
              setCurves(cu => ({
                ...cu,
                [c.id]: [
                  ...(cu[c.id] || []),
                  { round: evt.round, loss_curve: c.loss_curve }
                ]
              }))
            })

            // overview = average local / global / alpha
            const avgL = evt.clients.reduce((s,c) => s + c.client_eval_local_acc, 0) / evt.clients.length
            const avgG = evt.clients.reduce((s,c) => s + c.client_eval_global_acc, 0) / evt.clients.length
            const avgA = evt.clients.reduce((s,c) => s + c.client_alpha, 0) / evt.clients.length
            setOverview(o => [...o, { round: evt.round, avgL, avgG, avgA }])
          }
        })
      })
      .catch(console.error)
  }, [id])

  if (!expt) return <p>Loading experiment…</p>

  // same selection logic from your live page
  const latest = [...metrics].reverse().find(m => m.clients.some(c => c.id == selClient))
  const selClientMetrics = latest?.clients.find(c => c.id == selClient)
  const selClientCurve = curves[selClient]?.find(r =>
    r.round === (selRound ?? curves[selClient].slice(-1)[0].round)
  )

  return (
    <div className="dashboard">
      <button onClick={() => nav(-1)}>← Back</button>
      <header><h1>Experiment: {expt.name}</h1></header>

      <div className="status-banner">
        <h2>Round {status?.round} — {status?.running ? 'Running' : 'Finished'}</h2>
        <p>Clock: {status?.virtual_clock.toFixed(1)}s</p>
        <p>Sampled: {status?.sampled_clients.join(', ')}</p>
      </div>

      <section className="global-curve">
        <h3>Global Loss vs Round</h3>
        {metrics.length > 0 ? (
          <LineChart
            width={700}
            height={300}
            data={metrics.map(m => ({
              round: m.round,
              top1:  m.top1,
              top5:  m.top5
            }))}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="round" allowDecimals={false} />
            <YAxis />
            <Tooltip
              formatter={v => v.toFixed(3)}
              labelFormatter={l => `Round ${l}`}
            />
            <Legend verticalAlign="top" height={36} />
            <Line dataKey="top1" name="Top-1 Loss" dot={{ r: 4 }} stroke="#ff4757" strokeWidth={2}/>
            <Line dataKey="top5" name="Top-5 Loss" dot={{ r: 4 }} stroke="#1e90ff" strokeWidth={2}/>
          </LineChart>
        ) : (
          <p>Waiting for first completed round...</p>
        )}
      </section>

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
        {selClient && selClientCurve && (
          <>
            <label>
              Round:&nbsp;
              <select
                value={selRound ?? curves[selClient].slice(-1)[0].round}
                onChange={e => setSelRound(+e.target.value)}
              >
                {curves[selClient].map(r => (
                  <option key={r.round} value={r.round}>
                    Round {r.round}
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
              data={selClientCurve.loss_curve.map((l, i) => ({
                step: i + 1,
                loss: l
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="step" label={{ value: 'Batch Step', position: 'insideBottom' }}/>
              <YAxis label={{ value: 'Loss', angle: -90, position: 'insideLeft' }}/>
              <Tooltip formatter={v => v.toFixed(3)} />
              <Line type="monotone" dataKey="loss" dot={{ r: 3 }} stroke="#273c75" />
            </LineChart>
          </>
        )}
      </section>
    </div>
  )
}
