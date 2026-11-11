// Bản đồ chỉ giữ vị trí, mô tả ngắn và đường dẫn đến tài liệu kỹ thuật.

window.SPEC_CARDS = [
  {
    "id": "lateral-controller",
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
    "x": -850,
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
    "x": -110,
    "y": 334,
    "title": "Cấu hình xe",
    "summary": "Cung cấp kích thước và giới hạn lái của xe.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "vehicle-config"
    }
  },
  {
    "id": "path-planner",
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
  // Hàng đầu: báo cáo tổng quan.
  {
    "id": "mentor-report",
    "kind": "doc",
    "doc": "mentor-report",
    "main": true,
    "eyebrow": "Summary · Path Planner",
    "title": "Mentor Report",
    "summary": "Tóm tắt 2 trang: hệ thống, thiết kế chính, tuân thủ, kiểm chứng, an toàn và việc cần mentor hỗ trợ.",
    "x": -2540,
    "y": -650
  },
  // Hàng thứ hai: tài liệu chính, đọc từ trái sang phải.
  {
    "id": "path-planner-software-requirements-specification",
    "kind": "doc",
    "doc": "path-planner-software-requirements-specification",
    "renamedFrom": ["path-planner-software-requirements", "yeu-cau-path-planner"],
    "main": true,
    "eyebrow": "Requirements · Path Planner",
    "title": "Software Requirements Specification",
    "summary": "Requirement, performance target, ODD, giả định và giới hạn calibration parameter; căn cứ để chấm planner.",
    "x": -2540,
    "y": -80
  },
  {
    "id": "path-planner-software-architectural-design",
    "kind": "doc",
    "doc": "path-planner-software-architectural-design",
    "renamedFrom": ["path-planner-feature-design", "thiet-ke-path-planner"],
    "main": true,
    "eyebrow": "Design · Path Planner",
    "title": "Software Architectural Design",
    "summary": "Thành phần, chu kỳ, reference line, arbitration, path HWA, LKA, ELK, fault handling và calibration parameter.",
    "x": -2160,
    "y": -80
  },
  {
    "id": "path-planner-architecture-decision-records",
    "kind": "doc",
    "doc": "path-planner-architecture-decision-records",
    "renamedFrom": ["path-planner-architecture-decision-record", "path-planner-design-decisions"],
    "main": true,
    "eyebrow": "ADR · Path Planner",
    "title": "Architecture Decision Records",
    "summary": "12 quyết định thiết kế, mỗi quyết định có bối cảnh, phương án bị loại và hệ quả.",
    "x": -1780,
    "y": -80
  },
  {
    "id": "path-planner-software-detailed-design",
    "kind": "doc",
    "doc": "path-planner-software-detailed-design",
    "renamedFrom": ["path-planner-implementation", "trien-khai-path-planner"],
    "main": true,
    "eyebrow": "Detailed Design · Path Planner",
    "title": "Software Detailed Design",
    "summary": "Thuật toán T1 đến T11, cấu trúc code và calibration parameter cấp thuật toán.",
    "x": -1400,
    "y": -80
  },
  // Hàng thứ ba: tài liệu tra cứu.
  {
    "id": "path-planner-interface-control-document",
    "kind": "doc",
    "doc": "path-planner-interface-control-document",
    "renamedFrom": ["path-planner-interfaces", "g1-interfaces-and-signals", "interface-he-thong"],
    "eyebrow": "Interface · Path Planner",
    "title": "Interface Control Document",
    "summary": "11 message của planner: trường, kiểu, đơn vị, tần số, timeout.",
    "x": -2540,
    "y": 730
  },
  {
    "id": "adas-function-specification",
    "kind": "doc",
    "doc": "adas-function-specification",
    "renamedFrom": ["adas-functions", "chuc-nang-adas"],
    "eyebrow": "Function Specification · ADAS",
    "title": "ADAS Function Specification",
    "summary": "Khi nào HWA, LKA, ELK được yêu cầu: khả dụng, ý định tài xế, kích hoạt, cảnh báo, theo UN R79, EU ELKS và Euro NCAP.",
    "x": -2160,
    "y": 730
  },
  {
    "id": "path-planner-hazard-analysis-and-risk-assessment",
    "kind": "doc",
    "doc": "path-planner-hazard-analysis-and-risk-assessment",
    "renamedFrom": ["safety-analysis", "path-planner-safety-analysis"],
    "eyebrow": "Safety · HARA",
    "title": "Hazard Analysis and Risk Assessment (HARA)",
    "summary": "Item definition, hazard, S, E, C và ASIL đề xuất, safety goal, SOTIF; bản gửi phòng an toàn.",
    "status": "Chờ review",
    "x": -1780,
    "y": 730
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
    },
    "x": -1400,
    "y": 730
  },
  {
    "id": "conventions",
    "icon": "rules",
    "x": 403,
    "y": -483,
    "title": "Quy ước interface",
    "summary": "Quy định cách các khối trao đổi dữ liệu.",
    "research": {
      "doc": "path-planner-interface-control-document",
      "section": "header"
    }
  },
  {
    "id": "sim-scheduler",
    "group": "sim",
    "icon": "clock",
    "x": 883,
    "y": -650,
    "title": "Bộ lập lịch",
    "summary": "Điều phối thời điểm chạy các khối và giao message.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "sim-scheduler"
    }
  },
  {
    "id": "sim-can",
    "group": "sim",
    "icon": "bus",
    "x": 1236.333,
    "y": -650,
    "title": "Bus CAN ảo",
    "summary": "Mô phỏng truyền tín hiệu khung gầm qua CAN.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "sim-can"
    }
  },
  {
    "id": "sim-vehicle",
    "group": "sim",
    "icon": "car",
    "x": 883,
    "y": -390,
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
    "x": 1236.333,
    "y": -390,
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
    "x": 883,
    "y": -130,
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
    "x": 1236.333,
    "y": -130,
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
    "x": 1236.333,
    "y": 130,
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
    "x": 883,
    "y": 130,
    "title": "Ghi log và đánh giá",
    "summary": "Ghi dữ liệu để chạy lại và tính chỉ số đánh giá.",
    "research": {
      "doc": "path-planner-software-qualification-test-specification",
      "section": "benchmark-run"
    }
  },
  {
    "id": "diagram-sequence",
    "kind": "diagram",
    "diagram": "sequence",
    "doc": "path-planner-software-architectural-design",
    "section": "planner-sequence",
    "x": -930,
    "y": 820,
    "eyebrow": "Góc nhìn động · Software Architectural Design, mục 3.2",
    "title": "Tuần tự trong một chu kỳ 25 ms",
    "summary": "Ai gửi gì cho ai, theo thứ tự, và deadline của chu kỳ.",
    "lanes": ["Bộ lập lịch", "Input check", "Planner", "Ego-motion", "Lateral Controller", "Chức năng ADAS", "Khối dọc"],
    "own": ["Input check", "Planner"]
  },
  {
    "id": "diagram-states",
    "kind": "diagram",
    "diagram": "states",
    "doc": "path-planner-software-architectural-design",
    "section": "arbitration-states",
    "x": -77,
    "y": 820,
    "eyebrow": "Góc nhìn động · Software Architectural Design, mục 5.1",
    "title": "Arbitration state",
    "summary": "Chức năng đang lái (active_function) đổi thế nào theo từng sự kiện."
  },
  {
    "id": "diagram-latency",
    "kind": "diagram",
    "diagram": "latency",
    "doc": "path-planner-software-architectural-design",
    "section": "latency-chain",
    "x": 776,
    "y": 820,
    "eyebrow": "Góc nhìn thời gian · Software Architectural Design, mục 3.3",
    "title": "Chuỗi trễ từ cảm biến tới bánh xe",
    "summary": "Mỗi đoạn trễ dài bao nhiêu và khối nào bù."
  }
];

window.SPEC_REGIONS = [
  {
    "id": "docs",
    "text": "Technical Documents"
  },
  {
    "id": "vehicle",
    "text": "Phần mềm trên xe"
  },
  {
    "id": "simulation",
    "text": "Môi trường giả lập",
    "note": "Không phải phần mềm trên xe"
  },
  {
    "id": "dynamics",
    "text": "Kiến trúc động của Path Planner",
    "note": "Vẽ từ bảng trong tài liệu Thiết kế; bấm sơ đồ để xem bảng chi tiết"
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
    "label": "Trajectory (Autoware)",
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
    "id": "e-previous",
    "from": "path-planner",
    "to": "path-planner",
    "label": "Path chu kỳ trước",
    "research": {
      "doc": "path-planner-software-architectural-design",
      "section": "planner-cycle"
    }
  }
];
