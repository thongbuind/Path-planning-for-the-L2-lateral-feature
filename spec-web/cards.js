// Bản đồ chỉ giữ vị trí, mô tả ngắn và đường dẫn đến tài liệu kỹ thuật.

window.SPEC_CARDS = [
  {
    "id": "lateral-controller",
    "region": "system",
    "x": 403,
    "y": -163,
    "title": "Lateral Controller",
    "summary": "Nhận đường mục tiêu và tính lệnh lái.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "trajectory"
    }
  },
  {
    "id": "lane-model",
    "icon": "lane",
    "x": -930,
    "y": -163,
    "title": "Lane Model",
    "summary": "Cung cấp hình học và chất lượng của các vạch làn.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "lane-model"
    }
  },
  {
    "id": "sensors",
    "icon": "sensor",
    "x": -110,
    "y": -650,
    "title": "Cảm biến",
    "summary": "Cung cấp tín hiệu IMU, tốc độ xe và góc lái.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "can"
    }
  },
  {
    "id": "perception",
    "icon": "object",
    "x": -930,
    "y": 157,
    "title": "Perception",
    "summary": "Cung cấp danh sách vật thể xung quanh xe.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "perception"
    }
  },
  {
    "id": "state-estimator",
    "icon": "estimate",
    "x": -483,
    "y": -639,
    "title": "Ước lượng trạng thái xe",
    "summary": "Ước lượng vận tốc ngang và góc trượt của xe.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "state-estimator"
    }
  },
  {
    "id": "ego-motion",
    "icon": "ego",
    "x": -850,
    "y": -470,
    "title": "Ego-motion",
    "summary": "Cung cấp chuyển động của xe để planner bù trễ và nối path.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "ego-motion"
    }
  },
  {
    "id": "adas-function-specification",
    "region": "system",
    "icon": "adas",
    "x": -483,
    "y": 327,
    "title": "Chức năng ADAS",
    "summary": "Quyết định khi nào HWA, LKA và ELK yêu cầu can thiệp.",
    "research": {
      "doc": "adas-function-specification",
      "section": "adas-role"
    }
  },
  {
    "id": "vehicle-config",
    "icon": "config",
    "x": -930,
    "y": 480,
    "title": "Cấu hình xe",
    "summary": "Cung cấp kích thước và giới hạn lái của xe.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "vehicle-config"
    }
  },
  {
    "id": "path-planner",
    "region": "system",
    "group": "primary",
    "icon": "planner",
    "x": -266,
    "y": -173,
    "title": "Path Planner",
    "summary": "Tạo đường mục tiêu cho HWA, LKA và ELK.",
    "research": {
      "doc": "path-planner-software-architectural-design",
      "section": "planner-cycle"
    }
  },
  {
    "id": "eps",
    "region": "system",
    "icon": "steer",
    "x": 403,
    "y": 157,
    "title": "EPS",
    "summary": "Chấp hành lệnh lái; giảm mô-men theo dốc khi path không hợp lệ.",
    "research": {
      "doc": "path-planner-hazard-analysis-and-risk-assessment",
      "section": "safety-item"
    }
  },
  {
    "id": "longitudinal",
    "icon": "car",
    "x": 403,
    "y": -483,
    "title": "Khối dọc (ACC)",
    "summary": "Chỉnh tốc độ theo xe trước và theo cua, đọc giới hạn từ planner.",
    "research": {
      "doc": "path-planner-software-architectural-design",
      "section": "curve-strategy"
    }
  },
  {
    "id": "hmi",
    "icon": "flag",
    "x": -483,
    "y": 640,
    "title": "HMI",
    "summary": "Đèn, âm thanh, rung báo tài xế.",
    "research": {
      "doc": "adas-function-specification",
      "section": "adas-warnings"
    }
  },
  // Thẻ tài liệu xếp theo thứ tự trong danh mục.
  {
    "id": "mentor-report",
    "kind": "doc",
    "doc": "mentor-report",
    "main": true,
    "eyebrow": "Summary · Path Planner",
    "title": "Mentor Report",
    "summary": "Tóm tắt 2 trang: hệ thống, thiết kế chính, tuân thủ, kiểm chứng, an toàn và việc cần mentor hỗ trợ."
  },
  {
    "id": "path-planner-software-requirements-specification",
    "kind": "doc",
    "doc": "path-planner-software-requirements-specification",
    "renamedFrom": ["path-planner-software-requirements", "yeu-cau-path-planner"],
    "main": true,
    "eyebrow": "Requirements · Path Planner",
    "title": "Software Requirements Specification",
    "summary": "Requirement, performance target, ODD, giả định và giới hạn calibration parameter; căn cứ để chấm planner."
  },
  {
    "id": "path-planner-software-architectural-design",
    "kind": "doc",
    "doc": "path-planner-software-architectural-design",
    "renamedFrom": ["path-planner-feature-design", "thiet-ke-path-planner"],
    "main": true,
    "eyebrow": "Design · Path Planner",
    "title": "Software Architectural Design",
    "summary": "Thành phần, chu kỳ, reference line, arbitration, path HWA, LKA, ELK, fault handling và calibration parameter."
  },
  {
    "id": "path-planner-architecture-decision-records",
    "kind": "doc",
    "doc": "path-planner-architecture-decision-records",
    "renamedFrom": ["path-planner-architecture-decision-record", "path-planner-design-decisions"],
    "main": true,
    "eyebrow": "ADR · Path Planner",
    "title": "Architecture Decision Records",
    "summary": "Các quyết định thiết kế, bối cảnh, phương án đã xét và hệ quả."
  },
  {
    "id": "path-planner-software-detailed-design",
    "kind": "doc",
    "doc": "path-planner-software-detailed-design",
    "renamedFrom": ["path-planner-implementation", "trien-khai-path-planner"],
    "main": true,
    "eyebrow": "Detailed Design · Path Planner",
    "title": "Software Detailed Design",
    "summary": "Thuật toán T1 đến T11, cấu trúc code và calibration parameter cấp thuật toán."
  },
  {
    "id": "path-planner-interface-control-document",
    "kind": "doc",
    "doc": "path-planner-interface-control-document",
    "renamedFrom": ["path-planner-interfaces", "g1-interfaces-and-signals", "interface-he-thong"],
    "eyebrow": "Interface · Path Planner",
    "title": "Interface Control Document",
    "summary": "11 message của planner: trường, kiểu, đơn vị, tần số, timeout."
  },
  {
    "id": "adas-function-specification",
    "kind": "doc",
    "doc": "adas-function-specification",
    "renamedFrom": ["adas-functions", "chuc-nang-adas"],
    "eyebrow": "Function Specification · ADAS",
    "title": "ADAS Function Specification",
    "summary": "Khi nào HWA, LKA, ELK được yêu cầu: khả dụng, ý định tài xế, kích hoạt, cảnh báo, theo UN R79, EU ELKS và Euro NCAP."
  },
  {
    "id": "path-planner-hazard-analysis-and-risk-assessment",
    "kind": "doc",
    "doc": "path-planner-hazard-analysis-and-risk-assessment",
    "renamedFrom": ["safety-analysis", "path-planner-safety-analysis"],
    "eyebrow": "Safety · HARA",
    "title": "Hazard Analysis and Risk Assessment (HARA)",
    "summary": "Item definition, hazard, S, E, C và ASIL đề xuất, safety goal, SOTIF; bản gửi phòng an toàn.",
    "status": "Chờ review"
  },
  {
    "id": "path-planner-software-qualification-test-specification",
    "kind": "doc",
    "doc": "path-planner-software-qualification-test-specification",
    "renamedFrom": ["benchmark-evaluation"],
    "eyebrow": "Test · Path Planner",
    "title": "Software Qualification Test Specification",
    "summary": "Simulator, vehicle profiles, test case, fault injection, tiêu chí đạt, chỉ số và flexibility.",
    "mergedFrom": {
      "doc": "moi-truong-gia-lap",
      "section": "simulation-design"
    }
  },
  {
    "id": "sim-vehicle",
    "group": "sim",
    "icon": "car",
    "title": "Mô hình xe",
    "summary": "Mô phỏng chuyển động của xe và các tác động gây trôi làn.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "sim-vehicle"
    }
  },
  {
    "id": "sim-sensors",
    "group": "sim",
    "icon": "camera",
    "title": "Mô hình cảm biến",
    "summary": "Sinh tín hiệu cảm biến từ môi trường giả lập.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "sim-sensors"
    }
  },
  {
    "id": "sim-scenarios",
    "group": "sim",
    "icon": "flag",
    "title": "Kịch bản và bơm lỗi",
    "summary": "Tạo tình huống lái và lỗi đầu vào cho benchmark.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "benchmark-scenarios"
    }
  },
  {
    "id": "sim-controller",
    "group": "sim",
    "icon": "steer",
    "title": "Controller và EPS chạy thử",
    "summary": "Bám đường mục tiêu và mô phỏng bộ chấp hành lái.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "sim-controller"
    }
  },
  {
    "id": "sim-acc",
    "group": "sim",
    "icon": "clock",
    "title": "ACC chạy thử",
    "summary": "Tạo kế hoạch tốc độ và gia tốc dọc khi chạy thử.",
    "research": {
      "doc": "path-planner-software-architectural-design",
      "section": "acc-stub"
    }
  },
  {
    "id": "sim-eval",
    "group": "sim",
    "icon": "chart",
    "title": "Ghi log và đánh giá",
    "summary": "Ghi dữ liệu để chạy lại và tính chỉ số đánh giá.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "benchmark-run"
    }
  },
  {
    "id": "diagram-modes",
    "kind": "diagram",
    "diagram": "modes",
    "doc": "adas-function-specification",
    "section": "adas-modes",
    "region": "strategy",
    "eyebrow": "Chức năng · ADAS Function Specification, mục 9.1",
    "title": "Trạng thái của từng chức năng",
    "summary": "OFF, STANDBY, REQUEST và điều kiện chuyển, theo off, standby, active mode của R79."
  },
  {
    "id": "diagram-states",
    "kind": "diagram",
    "diagram": "states",
    "doc": "path-planner-software-architectural-design",
    "section": "arbitration-states",
    "region": "strategy",
    "eyebrow": "Chức năng · Software Architectural Design, mục 5.1",
    "title": "Arbitration state",
    "summary": "Chức năng đang lái (active_function) đổi thế nào theo từng sự kiện."
  },
  {
    "id": "diagram-curve",
    "kind": "diagram",
    "diagram": "curve",
    "doc": "path-planner-software-architectural-design",
    "section": "curve-strategy",
    "region": "strategy",
    "eyebrow": "Chiến lược điều khiển · Software Architectural Design, mục 6.2 · R171 5.3.7.1.3",
    "title": "Tốc độ và gia tốc ngang khi vào cua",
    "summary": "Path planner và khối dọc phối hợp thế nào qua từng pha."
  },
  {
    "id": "diagram-limits",
    "kind": "diagram",
    "diagram": "limits",
    "doc": "path-planner-software-architectural-design",
    "section": "design-limits",
    "region": "safety",
    "eyebrow": "Giới hạn vận hành · R79 Annex 6, 3.2.3 · 5.6.2.3.1",
    "title": "Dải tốc độ và giới hạn quyền lái",
    "summary": "Mỗi chức năng hoạt động ở tốc độ nào và được lái mạnh tới đâu.",
    "extra": [{ "doc": "adas-function-specification", "section": "adas-availability" }]
  },
  {
    "id": "diagram-ladder",
    "kind": "diagram",
    "diagram": "ladder",
    "doc": "path-planner-software-architectural-design",
    "section": "degradation",
    "region": "safety",
    "eyebrow": "Khái niệm an toàn · Software Architectural Design, mục 8.3 · R79 Annex 6, 3.4.3",
    "title": "Bậc suy giảm",
    "summary": "Mất biên làn hoặc input thì hệ thống còn làm được gì, và báo tài xế khi nào."
  },
  {
    "id": "diagram-sequence",
    "kind": "diagram",
    "diagram": "sequence",
    "doc": "path-planner-software-architectural-design",
    "section": "planner-sequence",
    "region": "dynamics",
    "eyebrow": "Luồng tín hiệu · Software Architectural Design, mục 3.2",
    "title": "Tuần tự trong một chu kỳ 25 ms",
    "summary": "Ai gửi gì cho ai, theo thứ tự, và deadline của chu kỳ.",
    "lanes": ["Bộ lập lịch", "Input check", "Planner", "Ego-motion", "Lateral Controller", "Chức năng ADAS", "Khối dọc"],
    "own": ["Input check", "Planner"]
  },
  {
    "id": "diagram-latency",
    "kind": "diagram",
    "diagram": "latency",
    "doc": "path-planner-software-architectural-design",
    "section": "latency-chain",
    "region": "dynamics",
    "eyebrow": "Thời gian · Software Architectural Design, mục 3.3",
    "title": "Chuỗi trễ từ cảm biến tới bánh xe",
    "summary": "Mỗi đoạn trễ dài bao nhiêu và khối nào bù."
  }
];

window.SPEC_REGIONS = [
  {
    "id": "docs",
    "text": "Tài liệu kỹ thuật"
  },
  {
    "id": "vehicle",
    "text": "Hệ thống trên xe",
    "note": "R79 Annex 6, 3.3: khung tím là The System, phần còn lại là hệ thống khác của xe"
  },
  {
    "id": "system",
    "text": "The System"
  },
  {
    "id": "simulation",
    "text": "Kiểm chứng SIL",
    "note": "Không phải phần mềm trên xe; simulator gọi đúng thư viện planner sẽ bàn giao"
  },
  {
    "id": "strategy",
    "text": "Chức năng và chiến lược điều khiển",
    "note": "R79 Annex 6, 3.2; R171 5.3.7.1.3. Vẽ từ bảng trong tài liệu; bấm sơ đồ để xem bảng"
  },
  {
    "id": "safety",
    "text": "Giới hạn vận hành và khái niệm an toàn",
    "note": "R79 Annex 6, 3.2.3 và 3.4.3"
  },
  {
    "id": "dynamics",
    "text": "Luồng tín hiệu và thời gian",
    "note": "R79 Annex 6, 3.3.4"
  }
];

window.SPEC_EDGES = [
  {
    "id": "e-sensors",
    "from": "sensors",
    "to": "path-planner",
    "label": "CAN · r, a_x, a_y, v, góc lái",
    "can": true,
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "can"
    }
  },
  {
    "id": "e-state",
    "from": "state-estimator",
    "to": "path-planner",
    "label": "v_y, β",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "state-estimator"
    }
  },
  {
    "id": "e-ego",
    "from": "ego-motion",
    "to": "path-planner",
    "label": "Δx, Δy, Δψ",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "ego-motion"
    }
  },
  {
    "id": "e-lane",
    "from": "lane-model",
    "to": "path-planner",
    "label": "Vạch làn, cờ sự kiện",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "lane-model"
    }
  },
  {
    "id": "e-perception",
    "from": "perception",
    "to": "path-planner",
    "label": "Vị trí, vận tốc vật thể",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "perception"
    }
  },
  {
    "id": "e-functions",
    "from": "adas-function-specification",
    "to": "path-planner",
    "label": "Yêu cầu, TLC",
    "research": {
      "doc": "adas-function-specification",
      "section": "function-requests"
    }
  },
  {
    "id": "e-config",
    "from": "vehicle-config",
    "to": "path-planner",
    "label": "Tham số xe",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "vehicle-config"
    }
  },
  {
    "id": "e-trajectory",
    "from": "path-planner",
    "to": "lateral-controller",
    "label": "Trajectory, PathStatus",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "trajectory"
    }
  },
  {
    "id": "e-valid",
    "from": "path-planner",
    "to": "adas-function-specification",
    "label": "Path hợp lệ, chức năng đang lái",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "path-status"
    }
  },
  {
    "id": "e-limits",
    "from": "path-planner",
    "to": "longitudinal",
    "label": "LateralLimits: v_max, khoảng cách, cờ",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "lateral-limits"
    }
  },
  {
    "id": "e-longplan",
    "from": "longitudinal",
    "to": "path-planner",
    "label": "LongitudinalPlan",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "longitudinal-plan"
    }
  },
  {
    "id": "e-eps",
    "from": "lateral-controller",
    "to": "eps",
    "label": "Lệnh lái",
    "research": {
      "doc": "path-planner-hazard-analysis-and-risk-assessment",
      "section": "safety-item"
    }
  },
  {
    "id": "e-hmi",
    "from": "adas-function-specification",
    "to": "hmi",
    "label": "Cảnh báo",
    "research": {
      "doc": "adas-function-specification",
      "section": "adas-warnings"
    }
  }
];
