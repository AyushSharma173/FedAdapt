// src/mockEvents.js

// A small sequence of “status” + “metrics” events, just like your real SSE.
export const mockEvents = [
    // === Round 1 status (sent a few times) ===
    {
      type: 'status',
      round: 1,
      running: true,
      virtual_clock: 0.0,
      sampled_clients: ['1','2','3','4'],
    },
    { /* duplicate to simulate polling */ 
      type: 'status',
      round: 1,
      running: true,
      virtual_clock: 0.0,
      sampled_clients: ['1','2','3','4'],
    },
  
    // === Round 1 metrics ===
    {
      type: 'metrics',
      round: 1,
      test_loss: 2.3027,
      top1: 0.103,
      top5: 0.504,
      clients: [
        {
          id: '1',
          loss: 2.764,
          utility: 464,
          duration: 0.1,
          loss_curve: [2.36, 2.88, 2.77, 3.80, 2.67],
          client_eval_local_acc: 0.12,
          client_eval_global_acc: 0.11,
          client_alpha: 0.50,
        },
        {
          id: '2',
          loss: 3.505,
          utility: 961,
          duration: 0.1,
          loss_curve: [2.48, 2.37, 4.02, 4.18, 5.29],
          client_eval_local_acc: 0.09,
          client_eval_global_acc: 0.10,
          client_alpha: 0.60,
        },
        {
          id: '3',
          loss: 4.289,
          utility: 960,
          duration: 0.1,
          loss_curve: [4.24, 2.88, 3.14, 4.67, 5.51],
          client_eval_local_acc: 0.08,
          client_eval_global_acc: 0.095,
          client_alpha: 0.40,
        },
        {
          id: '4',
          loss: 3.374,
          utility: 650,
          duration: 0.1,
          loss_curve: [3.06, 2.23, 3.91, 3.78, 3.90],
          client_eval_local_acc: 0.11,
          client_eval_global_acc: 0.105,
          client_alpha: 0.55,
        },
      ]
    },
  
    // === Round 2 status ===
    {
      type: 'status',
      round: 2,
      running: true,
      virtual_clock: 180.0,
      sampled_clients: ['1','2','3','4'],
    },
  
    // === Round 2 metrics ===
    {
      type: 'metrics',
      round: 2,
      test_loss: 2.323,
      top1: 0.163,
      top5: 0.651,
      clients: [
        {
          id: '1',
          loss: 2.402,
          utility: 480,
          duration: 0.1,
          loss_curve: [2.40, 2.47, 2.23, 2.37, 2.28],
          client_eval_local_acc: 0.15,
          client_eval_global_acc: 0.12,
          client_alpha: 0.52,
        },
        {
          id: '2',
          loss: 2.304,
          utility: 530,
          duration: 0.1,
          loss_curve: [2.32, 2.38, 2.59, 2.15, 2.34],
          client_eval_local_acc: 0.13,
          client_eval_global_acc: 0.11,
          client_alpha: 0.48,
        },
        {
          id: '3',
          loss: 2.306,
          utility: 600,
          duration: 0.1,
          loss_curve: [2.29, 2.13, 2.15, 2.30, 2.02],
          client_eval_local_acc: 0.14,
          client_eval_global_acc: 0.125,
          client_alpha: 0.60,
        },
        {
          id: '4',
          loss: 2.281,
          utility: 620,
          duration: 0.1,
          loss_curve: [2.27, 2.13, 2.15, 2.02, 2.12],
          client_eval_local_acc: 0.16,
          client_eval_global_acc: 0.13,
          client_alpha: 0.57,
        },
      ]
    },
  
    // === Final status (experiment ends) ===
    {
      type: 'status',
      round: 3,
      running: false,
      virtual_clock: 240.0,
      sampled_clients: ['1','2','3','4'],
    },
  ]
  