// import React, { useState, useEffect } from 'react'
// import axios from 'axios'
// import { useNavigate } from 'react-router-dom'

// export default function MainPage() {
//   const [expts, setExpts] = useState([])
//   const navigate = useNavigate()
//   const [form, setForm] = useState({
//     name: '',
//     num_clients: 4,
//     num_executors: 1,
//     gradient_policy: 'FedAvg',
//     experiment_mode: 'SIMULATION',
//     backend: 'gloo',
//     engine: 'pytorch',
//     model_zoo: 'vision',
//     model: 'shufflenet_v2_x2_0',
//     data_set: 'CIFAR10',
//     custom_data_file: null,
//     data_dir: '/data',
//     input_shape: '3,32,32',
//     output_dim: 10,
//     num_classes: 10,
//     embedding_file: '',
//     learning_rate: 0.01,
//     min_learning_rate: 0.001,
//     decay_factor: 0.1,
//     decay_round: 3,
//     rounds: 5,
//     local_steps: 1,
//     batch_size: 8,
//     test_bsz: 8,
//     eval_interval: 1,
//     dump_epoch: 5,
//     clip_bound: 1.0,
//     optimize_for: 'Balanced',
//     compression_limit: 0.5,
//     auto_tune: false,
//     alpha_threshold: 0.05,
//     alpha_step: 0.1,
//     data_map_file: null,
//   })

//   useEffect(() => {
//     axios.get('http://localhost:8000/experiments')
//       .then(r => setExpts(r.data))
//       .catch(console.error)
//   }, [])

//   const handleChange = e => {
//     const { name, value, type } = e.target
//     setForm(f => ({ ...f, [name]: type === 'number' ? +value : value }))
//   }

//   // Define start here so onSubmit has a valid handler
//   const start = async e => {
//     e.preventDefault()
//     const { data: newExp } = await axios.post(
//       'http://localhost:8000/experiments',
//       form
//     )
//     navigate(`/experiments/${newExp.id}`)
//   }

//   // Common styles
//   const fieldsetStyle = {
//     border: '1px solid #ddd',
//     borderRadius: '4px',
//     padding: '1rem',
//     width: '100%',
//     boxSizing: 'border-box',
//     margin: '0 auto',
//     maxWidth: '800px'
//   }
//   const legendStyle = { fontWeight: 'bold', padding: '0 0.5rem' }
//   const gridStyle = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }
//   const labelStyle = { display: 'flex', flexDirection: 'column', fontSize: '0.95rem' }
//   const inputStyle = { marginTop: '0.5em', padding: '0.5em', fontSize: '1rem', width: '100%', boxSizing: 'border-box' }
//   const summaryStyle = { cursor: 'pointer', fontWeight: 'bold', outline: 'none', padding: '0.5rem 0' }

//   return (
//     <div className="dashboard" style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
//       <header style={{ marginBottom: '1.5rem' }}><h1>FedScale Control Center</h1></header>
//       <section className="controls" style={{ width: '100%', maxWidth: '800px' }}>
//         <h2 style={{ marginBottom: '1rem' }}>Start New Experiment</h2>
//         <form onSubmit={start} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

//           {/* Main Settings */}
//           <fieldset style={fieldsetStyle}>
//             <legend style={legendStyle}>Main Settings</legend>
//             <div style={gridStyle}>
//               {/* Experiment Name spans full width */}
//               <div style={{ gridColumn: '1 / -1' }}>
//                 <label style={labelStyle}>
//                   Experiment Name:
//                   <input
//                     name="name"
//                     value={form.name}
//                     onChange={handleChange}
//                     type="text"
//                     required
//                     style={inputStyle}
//                   />
//                 </label>
//               </div>
//               {/* System / Scale controls */}
//               <label style={labelStyle}>
//                 Number of Clients:
//                 <input
//                   name="num_clients"
//                   value={form.num_clients}
//                   onChange={handleChange}
//                   type="number"
//                   style={inputStyle}
//                 />
//               </label>
//               <label style={labelStyle}>
//                 Number of Executors:
//                 <input
//                   name="num_executors"
//                   value={form.num_executors}
//                   onChange={handleChange}
//                   type="number"
//                   style={inputStyle}
//                 />
//               </label>
//               <label style={labelStyle}>
//                 Gradient Policy:
//                 <select
//                   name="gradient_policy"
//                   value={form.gradient_policy}
//                   onChange={handleChange}
//                   style={inputStyle}
//                 >
//                   <option value="FedAvg">FedAvg</option>
//                   <option value="fed-yogi">FedYogi</option>
//                   <option value="q-fedavg">Q-FedAvg</option>
//                 </select>
//               </label>
//               {/* <label style={labelStyle}>
//                 Experiment Mode:
//                 <input
//                   name="experiment_mode"
//                   value={form.experiment_mode}
//                   onChange={handleChange}
//                   type="text"
//                   style={inputStyle}
//                 />
//               </label> */}

//             <label style={labelStyle}>
//             Experiment Mode:
//             <select
//                 name="experiment_mode"
//                 value={form.experiment_mode}
//                 onChange={handleChange}
//                 style={inputStyle}
//             >
//                 <option value="SIMULATION">Debug</option>
//                 <option value="production">Production</option>
//             </select>
//             </label>

//               {/* <label style={labelStyle}>
//                 Backend:
//                 <input
//                   name="backend"
//                   value={form.backend}
//                   onChange={handleChange}
//                   type="text"
//                   style={inputStyle}
//                 />
//               </label> */}

//             <label style={labelStyle}>
//             Backend:
//             <select
//                 name="backned"
//                 value={form.backend}
//                 onChange={handleChange}
//                 style={inputStyle}
//             >
//                 <option value="gloo">gloo</option>
//             </select>
//             </label>



//               {/* <label style={labelStyle}>
//                 Engine:
//                 <input
//                   name="engine"
//                   value={form.engine}
//                   onChange={handleChange}
//                   type="text"
//                   style={inputStyle}
//                 />
//               </label> */}
//             <label style={labelStyle}>
//             Engine:
//             <select
//                 name="engine"
//                 value={form.engine}
//                 onChange={handleChange}
//                 style={inputStyle}
//             >
//                 <option value="pytorch">Pytorch</option>
//                 <option value="tensorflow">TensorFlow</option>
//             </select>
//             </label>

//             </div>
//           </fieldset>

//           {/* Collapsible Sections */}
//           <details style={fieldsetStyle}>
//             <summary style={summaryStyle}>Model & Data Selection</summary>
//             <div style={gridStyle}>
//                 {/* {[
//                 'model_zoo',
//                 'model',
//                 'data_set',
//                 'input_shape',
//                 'output_dim',
//                 'num_classes',
//                 'embedding_file'
//                 ].map(k => { */}

//                 {[
//                 'model_zoo',
//                 'model',
//                 'data_set'
//                 ].map(k => {

//                 // MODEL ZOO dropdown
//                 if (k === 'model_zoo') {
//                     return (
//                     <label key={k} style={labelStyle}>
//                         Model Zoo:
//                         <select
//                         name={k}
//                         value={form[k]}
//                         onChange={handleChange}
//                         style={inputStyle}
//                         >
//                         <option value="fedscale-torch-zoo">fedscale-torch-zoo</option>
//                         <option value="torchcv">torchcv</option>
//                         <option value="fedscale-tensorflow-zoo">fedscale-tensorflow-zoo</option>
//                         </select>
//                     </label>
//                     )
//                 }

//                 // MODEL dropdown
//                 if (k === 'model') {
//                     return (
//                     <label key={k} style={labelStyle}>
//                         Model:
//                         <select
//                         name={k}
//                         value={form[k]}
//                         onChange={handleChange}
//                         style={inputStyle}
//                         >
//                         <optgroup label="Computer Vision">
//                             <option value="shufflenet_v2_x2_0">shufflenet_v2_x2_0</option>
//                             <option value="mobilenet">mobilenet</option>
//                             <option value="resnet18">resnet18</option>
//                             <option value="resnet34">resnet34</option>
//                             <option value="resnet50">resnet50</option>
//                             <option value="resnet101">resnet101</option>
//                             <option value="resnet152">resnet152</option>
//                         </optgroup>
//                         <optgroup label="NLP / Text Classification">
//                             <option
//                             value="albert"
//                             title="Albert-based Transformer for text classification"
//                             >
//                             albert
//                             </option>
//                             <option
//                             value="lr"
//                             title="Logistic Regression head over 300-dim embeddings"
//                             >
//                             lr
//                             </option>
//                         </optgroup>
//                         </select>
//                     </label>
//                     )
//                 }

//                 // DATA_SET dropdown
//                 if (k === 'data_set') {
//                     return (
//                     <label key={k} style={{ ...labelStyle, gridColumn: '1 / -1' }}>
//                         Data Set:
//                         <div style={{ display: 'flex', gap: '0.5rem' }}>
//                             <select
//                                 name={k}
//                                 value={form[k]}
//                                 onChange={e => {
//                                     const value = e.target.value;
//                                     if (value === 'custom') {
//                                         setForm(f => ({ ...f, [k]: 'custom', custom_data_file: null }));
//                                     } else {
//                                         setForm(f => ({ ...f, [k]: value, custom_data_file: null }));
//                                     }
//                                 }}
//                                 style={{ ...inputStyle, flex: '1' }}
//                             >
//                                 <optgroup label="CV / Image Datasets">
//                                     <option value="mnist">Mnist</option>
//                                     <option value="cifar10">cifar10</option>
//                                     <option value="imagenet">imagenet</option>
//                                     <option value="emnist">emnist</option>
//                                     <option value="femnist">femnist</option>
//                                     <option value="openImg">openImg</option>
//                                     <option value="inaturalist">inaturalist</option>
//                                 </optgroup>
//                                 <optgroup label="Text / NLP Datasets">
//                                     <option value="amazon">amazon</option>
//                                     <option value="yelp">yelp</option>
//                                     <option value="blog">blog</option>
//                                     <option value="stackoverflow">stackoverflow</option>
//                                 </optgroup>
//                                 <optgroup label="Audio / Speech Datasets">
//                                     <option value="google_speech">google_speech</option>
//                                     <option value="common_voice">common_voice</option>
//                                 </optgroup>
//                                 <optgroup label="Custom Dataset">
//                                     <option value="custom">Upload Custom Dataset...</option>
//                                 </optgroup>
//                             </select>
//                             {form[k] === 'custom' && (
//                                 <div style={{ display: 'flex', gap: '0.5rem', flex: '1' }}>
//                                     <input
//                                         type="file"
//                                         accept=".json,.csv,.txt,.zip,.tar.gz"
//                                         onChange={e => {
//                                             const file = e.target.files[0];
//                                             if (file) {
//                                                 setForm(f => ({ 
//                                                     ...f, 
//                                                     custom_data_file: file,
//                                                     data_set: file.name
//                                                 }));
//                                             }
//                                         }}
//                                         style={{ ...inputStyle, width: 'auto' }}
//                                     />
//                                     {form.custom_data_file && (
//                                         <span style={{ 
//                                             fontSize: '0.9rem', 
//                                             color: '#666',
//                                             alignSelf: 'center',
//                                             whiteSpace: 'nowrap',
//                                             overflow: 'hidden',
//                                             textOverflow: 'ellipsis',
//                                             maxWidth: '200px'
//                                         }}>
//                                             {form.custom_data_file.name}
//                                         </span>
//                                     )}
//                                 </div>
//                             )}
//                         </div>
//                     </label>
//                     )
//                 }

//                 // all other fields
//                 return (
//                     <label key={k} style={labelStyle}>
//                     {k.replace(/_/g, ' ')}:
//                     <input
//                         name={k}
//                         value={form[k]}
//                         onChange={handleChange}
//                         type={typeof form[k] === 'number' ? 'number' : 'text'}
//                         style={inputStyle}
//                     />
//                     </label>
//                 )
//                 })}
//             </div>
//             </details>



//           <details style={{ ...fieldsetStyle, marginBottom: '0' }}>
//             <summary style={summaryStyle}>Training Hyperparameters</summary>
//             <div style={gridStyle}>
//               {['learning_rate','min_learning_rate','decay_factor','decay_round','rounds','local_steps','batch_size','test_bsz','eval_interval','dump_epoch','clip_bound'].map(k => (
//                 <label key={k} style={labelStyle}>
//                   {k.replace(/_/g,' ')}:
//                   <input
//                     name={k}
//                     value={form[k]}
//                     onChange={handleChange}
//                     type={typeof form[k] === 'number' ? 'number' : 'text'}
//                     style={inputStyle}
//                   />
//                 </label>
//               ))}
//             </div>
//           </details>

//           {/* Add new Heterogeneity-Aware Optimization section */}
//           <details style={{ ...fieldsetStyle, marginBottom: '0' }}>
//             <summary style={summaryStyle}>Heterogeneity-Aware Optimization</summary>
//             <div style={gridStyle}>
//               {/* Optimize For Dropdown */}
//               <label style={labelStyle}>
//                 Optimize For:
//                 <select
//                   name="optimize_for"
//                   value={form.optimize_for}
//                   onChange={handleChange}
//                   style={inputStyle}
//                 >
//                   <option value="Fastest Training">Fastest Training</option>
//                   <option value="Balanced">Balanced</option>
//                   <option value="Best Accuracy">Best Accuracy</option>
//                 </select>
//               </label>

//               {/* Compression Limit Number Input */}
//               <label style={labelStyle}>
//                 Compression Limit:
//                 <input
//                   name="compression_limit"
//                   type="number"
//                   min="0.1"
//                   max="1.0"
//                   step="0.1"
//                   value={form.compression_limit}
//                   onChange={handleChange}
//                   style={inputStyle}
//                 />
//               </label>

//               {/* Auto Tune Toggle */}
//               <label style={labelStyle}>
//                 Auto Tune:
//                 <select
//                   name="auto_tune"
//                   value={form.auto_tune.toString()}
//                   onChange={e => setForm(f => ({ ...f, auto_tune: e.target.value === 'true' }))}
//                   style={inputStyle}
//                 >
//                   <option value="true">Enabled</option>
//                   <option value="false">Disabled</option>
//                 </select>
//               </label>
//             </div>
//           </details>

//           {/* Add Self Adaptive Personalization section before the submit button */}
//           <details style={{ ...fieldsetStyle, marginBottom: '0' }}>
//             <summary style={summaryStyle}>Self Adaptive Personalization</summary>
//             <div style={gridStyle}>
//               {/* Alpha Threshold */}
//               <label style={labelStyle}>
//                 α-threshold:
//                 <div style={{ display: 'flex', gap: '0.5rem' }}>
//                   <select
//                     name="alpha_threshold"
//                     value={form.alpha_threshold}
//                     onChange={e => {
//                       const value = parseFloat(e.target.value);
//                       if (!isNaN(value)) {
//                         setForm(f => ({ ...f, alpha_threshold: value }));
//                       }
//                     }}
//                     style={{ ...inputStyle, flex: '1' }}
//                   >
//                     <option value="0.01">0.01</option>
//                     <option value="0.02">0.02</option>
//                     <option value="0.05">0.05</option>
//                     <option value="0.1">0.1</option>
//                     <option value="custom">Custom...</option>
//                   </select>
//                   {form.alpha_threshold === 'custom' && (
//                     <input
//                       type="number"
//                       min="0"
//                       max="1"
//                       step="0.005"
//                       value={form.alpha_threshold}
//                       onChange={e => {
//                         const value = parseFloat(e.target.value);
//                         if (!isNaN(value) && value >= 0 && value <= 1) {
//                           setForm(f => ({ ...f, alpha_threshold: value }));
//                         }
//                       }}
//                       style={{ ...inputStyle, width: '100px' }}
//                     />
//                   )}
//                 </div>
//               </label>

//               {/* Alpha Step */}
//               <label style={labelStyle}>
//                 α-step:
//                 <div style={{ display: 'flex', gap: '0.5rem' }}>
//                   <select
//                     name="alpha_step"
//                     value={form.alpha_step}
//                     onChange={e => {
//                       const value = parseFloat(e.target.value);
//                       if (!isNaN(value)) {
//                         setForm(f => ({ ...f, alpha_step: value }));
//                       }
//                     }}
//                     style={{ ...inputStyle, flex: '1' }}
//                   >
//                     <option value="0.05">0.05</option>
//                     <option value="0.1">0.1</option>
//                     <option value="0.2">0.2</option>
//                     <option value="0.5">0.5</option>
//                     <option value="custom">Custom...</option>
//                   </select>
//                   {form.alpha_step === 'custom' && (
//                     <input
//                       type="number"
//                       min="0"
//                       max="1"
//                       step="0.01"
//                       value={form.alpha_step}
//                       onChange={e => {
//                         const value = parseFloat(e.target.value);
//                         if (!isNaN(value) && value >= 0 && value <= 1) {
//                           setForm(f => ({ ...f, alpha_step: value }));
//                         }
//                       }}
//                       style={{ ...inputStyle, width: '100px' }}
//                     />
//                   )}
//                 </div>
//               </label>

//               {/* Data Map File */}
//               <label style={{ ...labelStyle, gridColumn: '1 / -1' }}>
//                 Data Map File:
//                 <div style={{ display: 'flex', gap: '0.5rem' }}>
//                   <select
//                     name="data_map_file"
//                     value={form.data_map_file}
//                     onChange={handleChange}
//                     style={{ ...inputStyle, flex: '1' }}
//                   >
//                     <option value="">None</option>
//                     <option value="cifar10_dirichlet_0.5.json">cifar10_dirichlet_0.5.json</option>
//                     <option value="femnist_dirichlet_0.5.json">femnist_dirichlet_0.5.json</option>
//                     <option value="amazon_dirichlet_0.5.json">amazon_dirichlet_0.5.json</option>
//                     <option value="custom">Upload Custom...</option>
//                   </select>
//                   {form.data_map_file === 'custom' && (
//                     <input
//                       type="file"
//                       accept=".json"
//                       onChange={e => {
//                         const file = e.target.files[0];
//                         if (file) {
//                           setForm(f => ({ ...f, data_map_file: file.name }));
//                         }
                        
//                       }}
//                       style={{ ...inputStyle, width: 'auto' }}
//                     />
//                   )}
//                 </div>
//               </label>
              
//             </div>
//           </details>

//           {/* Submit Button */}
//           <div style={{ textAlign: 'right' }}>
//             <button type="submit" style={{ padding: '0.75em 1.5em', fontSize: '1rem' }}>
//               Start Experiment
//             </button>
//           </div>
//         </form>
//       </section>

//       {/* Past Experiments */}
//       <section className="controls" style={{ width: '100%', maxWidth: '800px', marginTop: '2rem' }}>
//         <h2 style={{ marginBottom: '1rem' }}>Past Experiments</h2>
//         <table className="exp-list" style={{ width: '100%', borderCollapse: 'collapse' }}>
//           <thead>
//             <tr>
//               <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>Name</th>
//               <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>ID</th>
//               <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>Clients</th>
//               <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>Execs</th>
//               <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>Status</th>
//             </tr>
//           </thead>
//           <tbody>
//             {expts.map(e => (
//               <tr key={e.id} onClick={()=>navigate(`/experiments/${e.id}`)} style={{ cursor:'pointer' }}>
//                 <td style={{ padding: '0.5rem', borderBottom: '1px solid #f0f0f0' }}>{e.name}</td>
//                 <td style={{ padding: '0.5rem', borderBottom: '1px solid #f0f0f0', fontFamily: 'monospace' }}>{e.id.slice(0,8)}…</td>
//                 <td style={{ padding: '0.5rem', borderBottom: '1px solid #f0f0f0' }}>{e.num_clients}</td>
//                 <td style={{ padding: '0.5rem', borderBottom: '1px solid #f0f0f0' }}>{e.num_executors}</td>
//                 <td style={{ padding: '0.5rem', borderBottom: '1px solid #f0f0f0' }}>{e.running? '🟢':'🔴'}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </section>
//     </div>
//   )
// }


// src/pages/MainPage.js

import React, { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

export default function MainPage() {
  const navigate = useNavigate()

  // ---- form state ----
  const [form, setForm] = useState({
    name: '',
    num_clients: 4,
    num_executors: 1,
    gradient_policy: 'FedAvg',
    experiment_mode: 'SIMULATION',
    backend: 'gloo',
    engine: 'pytorch',
    model_zoo: 'vision',
    model: 'shufflenet_v2_x2_0',
    data_set: 'cifar10',
    custom_data_file: null,
    data_dir: '/data',
    input_shape: '3,32,32',
    output_dim: 10,
    num_classes: 10,
    embedding_file: '',
    learning_rate: 0.01,
    min_learning_rate: 0.001,
    decay_factor: 0.1,
    decay_round: 3,
    rounds: 5,
    local_steps: 1,
    batch_size: 8,
    test_bsz: 8,
    eval_interval: 1,
    dump_epoch: 5,
    clip_bound: 1.0,
    optimize_for: 'Balanced',
    compression_limit: 0.5,
    auto_tune: false,
    alpha_threshold: 0.05,
    alpha_step: 0.1,
    data_map_file: null,
  })

  const handleChange = e => {
    const { name, value, type } = e.target
    setForm(f => ({ ...f, [name]: type === 'number' ? +value : value }))
  }

  const start = async e => {
    e.preventDefault()
    try {
      const { data: newExp } = await axios.post(
        'http://18.218.117.22:8000/experiments',
        form
      )
      navigate(`/experiments/${newExp.id}`)
    } catch (err) {
      console.error(err)
      alert('Failed to start experiment')
    }
  }

  // ---- static completed experiments ----
  const staticGroups = [
    {
      id: 'experiment1',
      name: 'Non-IID Image Benchmark (Statistical Efficiency & Personalization)',
      variants: [
        { id: 'fedavg',       name: 'FedAvg on CIFAR-10 (Dirichlet α=0.5)' },
        { id: 'fedprox',      name: 'FedProx on CIFAR-10 (Dirichlet α=0.5)' },
        { id: 'fedyogi',      name: 'FedYoGi on CIFAR-10 (Dirichlet α=0.5)' },
        { id: 'selfadaptive', name: 'Self-Adaptive on CIFAR-10 (Dirichlet α=0.5)' },
      ]
    },
    {
      id: 'experiment3',
      name: 'Ablation: α-Threshold & Step-Size',
      variants: [
        { id: 't1s5',  name: 't=0.01, s=0.05' },
        { id: 't1s10', name: 't=0.01, s=0.10' },
        { id: 't1s20', name: 't=0.01, s=0.20' },
        { id: 't2s5',  name: 't=0.02, s=0.05' },
        { id: 't2s10', name: 't=0.02, s=0.10' },
        { id: 't2s20', name: 't=0.02, s=0.20' },
        { id: 't5s5',  name: 't=0.05, s=0.05' },
        { id: 't5s10', name: 't=0.05, s=0.10' },
        { id: 't5s20', name: 't=0.05, s=0.20' },
      ]
    }
  ]
  const [expanded, setExpanded] = useState({})
  const toggleGroup = gid => setExpanded(e => ({ ...e, [gid]: !e[gid] }))

  // ---- styling reused from before ----
  const fieldsetStyle = {
    border: '1px solid #ddd',
    borderRadius: '4px',
    padding: '1rem',
    width: '100%',
    boxSizing: 'border-box',
    margin: '0 auto',
    maxWidth: '800px'
  }
  const legendStyle = { fontWeight: 'bold', padding: '0 0.5rem' }
  const gridStyle = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }
  const labelStyle = { display: 'flex', flexDirection: 'column', fontSize: '0.95rem' }
  const inputStyle = { marginTop: '0.5em', padding: '0.5em', fontSize: '1rem', width: '100%', boxSizing: 'border-box' }
  const summaryStyle = { cursor: 'pointer', fontWeight: 'bold', outline: 'none', padding: '0.5rem 0' }

  return (
    <div className="dashboard" style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <header style={{ marginBottom: '1.5rem' }}><h1>FedAdapt A Production-Ready Adaptive Federated
      Learning Framework</h1></header>

      {/* --- Start New Experiment --- */}
      <section style={{ marginBottom: '3rem' }}>
        <h2>Start New Experiment</h2>
        <form onSubmit={start} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>

          {/* Main Settings */}
          <fieldset style={fieldsetStyle}>
            <legend style={legendStyle}>Main Settings</legend>
            <div style={gridStyle}>
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={labelStyle}>
                  Experiment Name:
                  <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    type="text"
                    required
                    style={inputStyle}
                  />
                </label>
              </div>
              <label style={labelStyle}>
                Number of Clients:
                <input
                  name="num_clients"
                  value={form.num_clients}
                  onChange={handleChange}
                  type="number"
                  style={inputStyle}
                />
              </label>
              <label style={labelStyle}>
                Number of Executors:
                <input
                  name="num_executors"
                  value={form.num_executors}
                  onChange={handleChange}
                  type="number"
                  style={inputStyle}
                />
              </label>
              <label style={labelStyle}>
                Gradient Policy:
                <select
                  name="gradient_policy"
                  value={form.gradient_policy}
                  onChange={handleChange}
                  style={inputStyle}
                >
                  <option value="FedAvg">FedAvg</option>
                  <option value="fed-yogi">FedYoGi</option>
                  <option value="q-fedavg">Q-FedAvg</option>
                </select>
              </label>
              <label style={labelStyle}>
                Experiment Mode:
                <select
                  name="experiment_mode"
                  value={form.experiment_mode}
                  onChange={handleChange}
                  style={inputStyle}
                >
                  <option value="SIMULATION">Debug</option>
                  <option value="production">Production</option>
                </select>
              </label>
              <label style={labelStyle}>
                Backend:
                <select
                  name="backend"
                  value={form.backend}
                  onChange={handleChange}
                  style={inputStyle}
                >
                  <option value="gloo">gloo</option>
                </select>
              </label>
              <label style={labelStyle}>
                Engine:
                <select
                  name="engine"
                  value={form.engine}
                  onChange={handleChange}
                  style={inputStyle}
                >
                  <option value="pytorch">PyTorch</option>
                  <option value="tensorflow">TensorFlow</option>
                </select>
              </label>
            </div>
          </fieldset>

          {/* Model & Data Selection */}
          <details style={fieldsetStyle}>
            <summary style={summaryStyle}>Model & Data Selection</summary>
            <div style={gridStyle}>
              {['model_zoo','model','data_set','input_shape','output_dim','num_classes','embedding_file'].map(k => {
                // same logic you had before...
                if (k === 'model_zoo') {
                  return (
                    <label key={k} style={labelStyle}>
                      Model Zoo:
                      <select name={k} value={form[k]} onChange={handleChange} style={inputStyle}>
                        <option value="fedscale-torch-zoo">fedscale-torch-zoo</option>
                        <option value="torchcv">torchcv</option>
                        <option value="fedscale-tensorflow-zoo">fedscale-tensorflow-zoo</option>
                      </select>
                    </label>
                  )
                }
                if (k === 'model') {
                  return (
                    <label key={k} style={labelStyle}>
                      Model:
                      <select name={k} value={form[k]} onChange={handleChange} style={inputStyle}>
                        <optgroup label="Computer Vision">
                          <option value="shufflenet_v2_x2_0">shufflenet_v2_x2_0</option>
                          <option value="mobilenet">mobilenet</option>
                          <option value="resnet18">resnet18</option>
                          {/* …other CV models… */}
                        </optgroup>
                        <optgroup label="NLP">
                          <option value="albert">albert</option>
                          <option value="lr">lr</option>
                        </optgroup>
                      </select>
                    </label>
                  )
                }
                if (k === 'data_set') {
                  return (
                    <label key={k} style={{ ...labelStyle, gridColumn: '1 / -1' }}>
                      Data Set:
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <select
                          name={k}
                          value={form[k]}
                          onChange={e => {
                            const v = e.target.value
                            if (v === 'custom') {
                              setForm(f => ({ ...f, [k]: 'custom', custom_data_file: null }))
                            } else {
                              setForm(f => ({ ...f, [k]: v, custom_data_file: null }))
                            }
                          }}
                          style={{ ...inputStyle, flex: '1' }}
                        >
                          <optgroup label="CV">
                            <option value="mnist">mnist</option>
                            <option value="cifar10">cifar10</option>
                            {/* … */}
                          </optgroup>
                          <optgroup label="Custom">
                            <option value="custom">Upload…</option>
                          </optgroup>
                        </select>
                        {form[k] === 'custom' && (
                          <input
                            type="file"
                            accept=".json,.csv"
                            onChange={e => {
                              const file = e.target.files[0]
                              if (file) setForm(f => ({ ...f, custom_data_file: file, data_set: file.name }))
                            }}
                            style={{ ...inputStyle, width: 'auto' }}
                          />
                        )}
                      </div>
                    </label>
                  )
                }
                // input_shape, output_dim, num_classes, embedding_file
                return (
                  <label key={k} style={labelStyle}>
                    {k.replace(/_/g,' ')}:
                    <input
                      name={k}
                      value={form[k]}
                      onChange={handleChange}
                      type={typeof form[k] === 'number' ? 'number' : 'text'}
                      style={inputStyle}
                    />
                  </label>
                )
              })}
            </div>
          </details>

          {/* Training Hyperparameters */}
          <details style={fieldsetStyle}>
            <summary style={summaryStyle}>Training Hyperparameters</summary>
            <div style={gridStyle}>
              {[
                'learning_rate','min_learning_rate','decay_factor','decay_round',
                'rounds','local_steps','batch_size','test_bsz','eval_interval',
                'dump_epoch','clip_bound'
              ].map(k => (
                <label key={k} style={labelStyle}>
                  {k.replace(/_/g,' ')}:
                  <input
                    name={k}
                    value={form[k]}
                    onChange={handleChange}
                    type={typeof form[k] === 'number' ? 'number' : 'text'}
                    style={inputStyle}
                  />
                </label>
              ))}
            </div>
          </details>

          {/* Heterogeneity-Aware Optimization */}
          <details style={fieldsetStyle}>
            <summary style={summaryStyle}>Heterogeneity-Aware Optimization</summary>
            <div style={gridStyle}>
              <label style={labelStyle}>
                Optimize For:
                <select
                  name="optimize_for"
                  value={form.optimize_for}
                  onChange={handleChange}
                  style={inputStyle}
                >
                  <option value="Fastest Training">Fastest Training</option>
                  <option value="Balanced">Balanced</option>
                  <option value="Best Accuracy">Best Accuracy</option>
                </select>
              </label>
              <label style={labelStyle}>
                Compression Limit:
                <input
                  name="compression_limit"
                  type="number"
                  step="0.1"
                  min="0.1"
                  max="1.0"
                  value={form.compression_limit}
                  onChange={handleChange}
                  style={inputStyle}
                />
              </label>
              <label style={labelStyle}>
                Auto Tune:
                <select
                  name="auto_tune"
                  value={form.auto_tune.toString()}
                  onChange={e => setForm(f => ({ ...f, auto_tune: e.target.value === 'true' }))}
                  style={inputStyle}
                >
                  <option value="true">Enabled</option>
                  <option value="false">Disabled</option>
                </select>
              </label>
            </div>
          </details>

          {/* Self Adaptive Personalization */}
          <details style={fieldsetStyle}>
            <summary style={summaryStyle}>Self Adaptive Personalization</summary>
            <div style={gridStyle}>
              <label style={labelStyle}>
                α-threshold:
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    name="alpha_threshold"
                    value={form.alpha_threshold}
                    onChange={handleChange}
                    style={{ ...inputStyle, flex: 1 }}
                  >
                    <option value="0.01">0.01</option>
                    <option value="0.02">0.02</option>
                    <option value="0.05">0.05</option>
                    <option value="0.1">0.1</option>
                    <option value="custom">Custom…</option>
                  </select>
                  {form.alpha_threshold === 'custom' && (
                    <input
                      type="number"
                      step="0.005"
                      min="0"
                      max="1"
                      value={form.alpha_threshold}
                      onChange={handleChange}
                      style={{ ...inputStyle, width: '100px' }}
                    />
                  )}
                </div>
              </label>
              <label style={labelStyle}>
                α-step:
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    name="alpha_step"
                    value={form.alpha_step}
                    onChange={handleChange}
                    style={{ ...inputStyle, flex: 1 }}
                  >
                    <option value="0.05">0.05</option>
                    <option value="0.1">0.1</option>
                    <option value="0.2">0.2</option>
                    <option value="0.5">0.5</option>
                    <option value="custom">Custom…</option>
                  </select>
                  {form.alpha_step === 'custom' && (
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={form.alpha_step}
                      onChange={handleChange}
                      style={{ ...inputStyle, width: '100px' }}
                    />
                  )}
                </div>
              </label>
              <label style={{ ...labelStyle, gridColumn: '1 / -1' }}>
                Data Map File:
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <select
                    name="data_map_file"
                    value={form.data_map_file}
                    onChange={handleChange}
                    style={{ ...inputStyle, flex: 1 }}
                  >
                    <option value="">None</option>
                    <option value="cifar10_dirichlet_0.5.json">cifar10_dirichlet_0.5.json</option>
                    <option value="custom">Upload…</option>
                  </select>
                  {form.data_map_file === 'custom' && (
                    <input
                      type="file"
                      accept=".json"
                      onChange={e => {
                        const file = e.target.files[0]
                        if (file) setForm(f => ({ ...f, data_map_file: file.name }))
                      }}
                      style={{ ...inputStyle, width: 'auto' }}
                    />
                  )}
                </div>
              </label>
            </div>
          </details>

          {/* submit */}
          <div style={{ textAlign: 'right' }}>
            <button 
              type="submit" 
              disabled
              style={{ 
                padding: '0.75em 1.5em', 
                fontSize: '1rem',
                opacity: 0.6,
                cursor: 'not-allowed',
                backgroundColor: '#e0e0e0',
                border: '1px solid #ccc',
                color: '#666'
              }}
            >
              Start Experiment
            </button>
            <div style={{ 
              marginTop: '0.5rem', 
              fontSize: '0.9rem', 
              color: '#666',
              textAlign: 'center'
            }}>
              This is for public preview. Refer to our{' '}
              <a 
                href="http://docs.fedadapt.com.s3-website.us-east-2.amazonaws.com/self_adaptive/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#0066cc', textDecoration: 'underline' }}
              >
                documentation
              </a>
              {' '}for more information.
            </div>
          </div>
        </form>
      </section>

      {/* --- Completed (static) experiments --- */}
      <section>
        <h2>Completed Experiments</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>
                Experiment
              </th>
              <th style={{ textAlign: 'left', padding: '0.5rem', borderBottom: '1px solid #ddd' }}>
                ID
              </th>
            </tr>
          </thead>

          
          <tbody>
            {staticGroups.map(group => (
              <React.Fragment key={group.id}>
                {/* folder row */}
                <tr
                  onClick={() => toggleGroup(group.id)}
                  style={{ cursor: 'pointer', background: '#f5f5f5', fontWeight: 'bold' }}
                >
                  <td style={{ padding: '0.75rem' }}>
                    {expanded[group.id] ? '▼' : '▶'} {group.name}
                  </td>
                  <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>
                    {group.id}
                  </td>
                </tr>

                {/* variant rows */}
                {expanded[group.id] &&
                  group.variants.map(v => (
                    <tr
                      key={v.id}
                      onClick={() =>
                        navigate(`/experiments/${group.id}-${v.id}/completed`)
                      }
                      style={{ cursor: 'pointer' }}
                    >
                      <td style={{ padding: '0.75rem 0.75rem 0.75rem 2.5rem' }}>
                        {v.name}
                      </td>
                      <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>
                        {`${group.id}-${v.id}`}
                      </td>
                    </tr>
                  ))}
              </React.Fragment>
            ))}
          </tbody>


        </table>
      </section>
    </div>
  )
}
