# Path Planner Implementation (Pending)

**Status is pending.** This report will describe **how to implement** the G1 path planner. It will specify the algorithms for each part and the selected path planning technique. Work will begin once the Path Planner Feature Design report completes the feature plan. This report currently collects algorithm notes and comments. **Implementation is pending.**

**Relationship to other reports**

| Report | Relationship to this report |
|---|---|
| Path Planner Feature Design | Provides the **feature plan**, including expected behavior, limits and fault handling. This report will specify **how to implement** each part |
| Benchmark and Evaluation | Provides the comparison of candidate techniques used to select the primary technique (T7) |
| ADAS Functions | Shares the DLC, v_lat and TLC calculation with the ADAS module (T6) |

## 1. Implementation notes

| # | Topic | Section in Path Planner Feature Design | Work needed |
|---|---|---|---|
| T1 | Delay compensation | Section 3 | Define how to transform the lane model using ego motion from the capture timestamp. Handle abnormal timestamps. Verify with a 0–200 ms delay sweep and loss of clock synchronization. Measure yaw rate filter delay by cross-correlating raw and filtered signals, then record it as a configuration parameter. This directly affects accuracy and safety |
| T2 | Reference path | Section 4 | Define the algorithm for two markings, one marking plus remembered width, width changes at exits and merges, double markings and the switch from L1 to L2 during a lane change. Define how to check boundary consistency at two time scales using per-frame, parallelism and width thresholds. Specify how to confirm a real lane change |
| T3 | Noise fallback | Section 4.1 | Set the reference rate limit and jerk weight. Balance oscillation against response delay |
| T4 | c0 jump | Section 4 | Define a smooth path stitching algorithm, including the connector shape, center shift rate and how to stay within the continuity thresholds |
| T5 | c2 fusion | Section 4 | Set weights for camera c2, r/v and path history |
| T6 | Initial path state | Section 4.2 | Set the threshold for switching from the previous path to a fresh calculation from measurements. Use a shared function with the ADAS module |
| T7 | Primary technique | Entire report | Survey and select a technique. Document at least one rejected alternative and the reason, as required by the assignment. Use the results from Benchmark and Evaluation |

## 2. Candidate techniques

The assignment requires a survey and selection of a technique, with at least one rejected alternative and the reason for rejecting it. The selection is open. Benchmark and Evaluation will compare the options on the same scenarios.

| Technique | Approach | Expected strengths | Expected weaknesses |
|---|---|---|---|
| Time-parameterized quintic or clothoid | Connect the current state to the target state in T seconds. Select T from the feature and TLC | Low computational cost. Limits can be checked analytically. Easy to run on an ECU | Requires an explicit lane boundary check and a new choice of T when the check fails |
| Frenet sampling (Werling et al. 2010) | Generate quintic paths with different targets and T values. Pick the path with the lowest cost in jerk, duration and deviation that meets the limits | Selects the best path in the sampled set and can handle boundaries. The same approach can extend to a longitudinal trajectory | More computation. Results depend on the sampling grid and can jump between paths across cycles |
| Lateral offset optimization (QP or MPC) | Optimize d(s) with lane boundary constraints. ELK tightens the boundaries and increases the a_y limit | Enforces boundaries and limits explicitly. One formulation covers all three features | Highest computational cost. Requires a real-time solver. A feasible solution is hard to guarantee |

## References

- G1 assignment (`G1_Path_Planning.pdf`), Techniques to investigate
- Werling, Ziegler, Kammel, Thrun (2010), Optimal trajectory generation for dynamic street scenarios in a Frenet frame, ICRA
