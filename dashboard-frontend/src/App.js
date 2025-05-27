// import React, { useState, useEffect, useRef } from 'react'
// import axios from 'axios'
// import {
//   LineChart,
//   Line,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   Legend,
// } from 'recharts'
// import { mockEvents } from './mockEvents'
// import './App.css'  // see accompanying styling file

// const USE_MOCK = true

// function App() {
//   // experiment list + form
//   const [expts, setExpts] = useState([])
//   const [name, setName] = useState('')
//   const [numClients, setNumClients] = useState(4)
//   const [numExecutors, setNumExecutors] = useState(1)
//   const [loading, setLoading] = useState(false)

//   // live‐view state
//   const [liveExpId, setLiveExpId] = useState(null)
//   const [liveStatus, setLiveStatus] = useState(null)
//   const [liveMetrics, setLiveMetrics] = useState([])
//   const [clientCurves, setClientCurves] = useState({})
//   const [personalizationOverview, setPersonalizationOverview] = useState([])
//   const [selectedClient, setSelectedClient] = useState(null)
//   const [clientRound, setClientRound] = useState(null)

//   const eventSourceRef = useRef(null)

//   // fetch experiments on mount
//   useEffect(() => {
//     axios.get('http://localhost:8000/experiments')
//       .then(res => setExpts(res.data))
//       .catch(err => console.error('Failed fetching experiments', err))
//   }, [])

//   // live SSE / mock hookup
//   useEffect(() => {
//     if (eventSourceRef.current) {
//       eventSourceRef.current.close()
//       eventSourceRef.current = null
//     }
//     setLiveStatus(null)
//     setLiveMetrics([])
//     setClientCurves({})
//     setPersonalizationOverview([])
//     setSelectedClient(null)
//     setClientRound(null)
//     if (!liveExpId) return

//     function handleMetrics(msg) {
//       setLiveMetrics(m => [...m, msg])
//       // per-client loss curves and personalization overview
//       msg.clients.forEach(cm => {
//         setClientCurves(prev => ({
//           ...prev,
//           [cm.id]: {
//             ...(prev[cm.id]||{}),
//             rounds: [...(prev[cm.id]?.rounds||[]), { round: msg.round, loss_curve: cm.loss_curve }]
//           }
//         }))
//       })
//       const avgLocal = msg.clients.reduce((sum,c)=>(sum + c.client_eval_local_acc),0)/msg.clients.length
//       const avgGlobal= msg.clients.reduce((sum,c)=>(sum + c.client_eval_global_acc),0)/msg.clients.length
//       const avgAlpha = msg.clients.reduce((sum,c)=>(sum + c.client_alpha),0)/msg.clients.length
//       setPersonalizationOverview(prev=>[
//         ...prev,
//         { round: msg.round, avgLocal, avgGlobal, avgAlpha }
//       ])
//     }

//     if (USE_MOCK) {
//       let i = 0
//       const t = setInterval(() => {
//         if (i >= mockEvents.length) return clearInterval(t)
//         const msg = mockEvents[i++]  // feed at 1s intervals
//         if (msg.type === 'status') {
//           setLiveStatus(msg)
//         } else {
//           handleMetrics(msg)
//         }
//       }, 1000)
//       return () => clearInterval(t)
//     } else {
//       const es = new EventSource(`http://localhost:8000/experiments/${liveExpId}/stream`)
//       eventSourceRef.current = es
//       es.onmessage = e => {
//         const msg = JSON.parse(e.data)
//         if (msg.type === 'status') setLiveStatus(msg)
//         else handleMetrics(msg)
//       }
//       es.onerror = () => { es.close(); eventSourceRef.current = null }
//       return () => es.close()
//     }
//   }, [liveExpId])

//   // Handlers (create / stop)
//   const createExperiment = async e => {
//     e.preventDefault()
//     setLoading(true)
//     try {
//       await axios.post('http://localhost:8000/experiments', { name, num_clients: numClients, num_executors: numExecutors })
//       setName('')
//       const res = await axios.get('http://localhost:8000/experiments')
//       setExpts(res.data)
//     } catch (err) { console.error(err) }
//     setLoading(false)
//   }
//   const stopExperiment = async id => {
//     await axios.post(`http://localhost:8000/experiments/${id}/stop`)
//     const res = await axios.get('http://localhost:8000/experiments')
//     setExpts(res.data)
//   }

//   // derive metrics for selected client & round
//   const selectedData = selectedClient != null && clientCurves[selectedClient]
//     ? clientCurves[selectedClient].rounds.find(r=>r.round===clientRound ?? Math.max(...clientCurves[selectedClient].rounds.map(o=>o.round)))
//     : null
//   const selectedMetrics = liveMetrics.slice().reverse().find(m=>m.clients.some(c=>String(c.id)===String(selectedClient)))?.clients.find(c=>String(c.id)===String(selectedClient))

//   return (
//     <div className="dashboard">
//       <header><h1>FedScale Dashboard</h1></header>

//       {/* Experiment Form & List */}
//       <section className="controls">
//         <form onSubmit={createExperiment}>
//           <input placeholder="Experiment name" value={name} onChange={e=>setName(e.target.value)} required />
//           <input type="number" min={1} value={numClients} onChange={e=>setNumClients(+e.target.value)} placeholder="Clients" />
//           <input type="number" min={1} value={numExecutors} onChange={e=>setNumExecutors(+e.target.value)} placeholder="Executors" />
//           <button type="submit" disabled={loading}>{loading ? 'Starting…' : 'Start Experiment'}</button>
//         </form>
//         <table className="exp-list">
//           <thead><tr><th>Name</th><th>ID</th><th>Clients</th><th>Status</th><th>Actions</th></tr></thead>
//           <tbody>
//             {expts.map(exp=> (
//               <tr key={exp.id}>
//                 <td>{exp.name}</td>
//                 <td className="monospace">{exp.id.slice(0,8)}…</td>
//                 <td>{exp.num_clients}</td>
//                 <td>{exp.running ? '🟢 Running':'🔴 Stopped'}</td>
//                 <td>
//                   {exp.running && <><button onClick={()=>stopExperiment(exp.id)}>Stop</button><button onClick={()=>setLiveExpId(exp.id)}>Live</button></>}
//                 </td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </section>

//       {/* Live View */}
//       {liveExpId && (
//         <section className="live-view">
//           <div className="status-banner">
//             <h2>Round {liveStatus?.round} — {liveStatus?.running? 'In Progress':'Completed'}</h2>
//             <p>Clock: {liveStatus?.virtual_clock.toFixed(1)}s</p>
//             <p>Sampled: {liveStatus?.sampled_clients.join(', ')}</p>
//           </div>


//           {/* Global Loss Curve */}
//           <div className="global-curve">
//             <h3>Global Loss over Rounds</h3>
//             <LineChart
//               width={700}
//               height={300}
//               data={liveMetrics.map(m => ({ round: m.round, top1: m.top1, top5: m.top5 }))}
//             >
//               <CartesianGrid strokeDasharray="3 3" />
//               <XAxis
//                 dataKey="round"
//                 label={{ value: 'Round', position: 'insideBottom', offset: -5 }}
//                 tickCount={liveMetrics.length}
//                 allowDecimals={false}
//               />
//               <YAxis
//                 label={{ value: 'Loss', angle: -90, position: 'insideLeft', offset: 10 }}
//               />
//               <Tooltip
//                 formatter={value => value.toFixed(3)}
//                 labelFormatter={label => `Round ${label}`}
//               />
//               <Legend verticalAlign="top" height={36} />

//               {/* Top-1 Loss with points */}
//               <Line
//                 type="monotone"
//                 dataKey="top1"
//                 name="Top-1 Loss"
//                 dot={{ r: 4 }}
//                 activeDot={{ r: 6 }}
//                 stroke="#ff4757"
//                 strokeWidth={2}
//               />

//               {/* Top-5 Loss with points */}
//               <Line
//                 type="monotone"
//                 dataKey="top5"
//                 name="Top-5 Loss"
//                 dot={{ r: 4 }}
//                 activeDot={{ r: 6 }}
//                 stroke="#1e90ff"
//                 strokeWidth={2}
//               />
//             </LineChart>
//           </div>

//           {/* Client Tabs */}
//           <div className="client-section">
//             <h3>Client Details</h3>
//             <div className="client-tabs">
//               {Object.keys(clientCurves).map(id=>(
//                 <button key={id} className={String(selectedClient)===String(id)?'active':''} onClick={()=>{setSelectedClient(id); setClientRound(null)}}>
//                   Client {id}
//                 </button>
//               ))}
//             </div>
//             {selectedClient && (
//               <div className="client-detail">
//                 <label>
//                   Round:
//                   <select value={clientRound ?? Math.max(...clientCurves[selectedClient].rounds.map(r=>r.round))} onChange={e=>setClientRound(+e.target.value)}>
//                     {clientCurves[selectedClient].rounds.map(r=>(
//                       <option key={r.round} value={r.round}>Round {r.round}</option>
//                     ))}
//                   </select>
//                 </label>
//                 <div className="cards">
//                   <div className="card">
//                     <h4>Local Acc</h4>
//                     <p>{(selectedMetrics.client_eval_local_acc*100).toFixed(1)}%</p>
//                   </div>
//                   <div className="card">
//                     <h4>Global Acc</h4>
//                     <p>{(selectedMetrics.client_eval_global_acc*100).toFixed(1)}%</p>
//                   </div>
//                   <div className="card">
//                     <h4>Mix α</h4>
//                     <p>{selectedMetrics.client_alpha.toFixed(2)}</p>
//                   </div>
//                 </div>
//                 <LineChart width={600} height={250} data={selectedData?.loss_curve.map((l,i)=>({ step:i+1, loss:l }))}>
//                   <CartesianGrid strokeDasharray="3 3" />
//                   <XAxis dataKey="step" label={{ value: 'Batch Step', position:'insideBottom' }} />
//                   <YAxis label={{ value: 'Loss', angle:-90, position:'insideLeft' }} />
//                   <Tooltip formatter={v=>v.toFixed(3)} />
//                   <Line type="monotone" dataKey="loss" dot={false} />
//                 </LineChart>
//               </div>
//             )}

//             <button className="close-btn" onClick={()=>setLiveExpId(null)}>Close Live View</button>
//           </div>
//         </section>
//       )}
//     </div>
//   )
// }

// export default App


import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import MainPage from './pages/MainPage'
import ExperimentDetail from './pages/ExperimentDetail'
import CompletedExperiment from './pages/CompletedExperiment'

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainPage />} />
      <Route path="/experiments/:id" element={<ExperimentDetail />} />
      <Route path="/experiments/:id/live" element={<ExperimentDetail />} />
      <Route path="/experiments/:id/completed" element={<CompletedExperiment />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
