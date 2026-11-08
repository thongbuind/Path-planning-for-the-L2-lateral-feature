// Bản đồ chỉ giữ vị trí, mô tả ngắn và đường dẫn đến Research.

window.SPEC_CARDS = [
  {
    "id": "lateral-controller",
    "x": 403,
    "y": -163,
    "title": "Lateral Controller",
    "summary": "Nhận đường mục tiêu và tính lệnh lái.",
    "research": {
      "doc": "interface-he-thong",
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
      "doc": "interface-he-thong",
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
      "doc": "interface-he-thong",
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
      "doc": "interface-he-thong",
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
      "doc": "interface-he-thong",
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
      "doc": "interface-he-thong",
      "section": "ego-motion"
    }
  },
  {
    "id": "adas-functions",
    "icon": "adas",
    "x": -483,
    "y": 327,
    "title": "Chức năng ADAS",
    "summary": "Quyết định khi nào HWA, LKA và ELK yêu cầu can thiệp.",
    "research": {
      "doc": "chuc-nang-adas",
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
      "doc": "interface-he-thong",
      "section": "vehicle-config"
    }
  },
  {
    "id": "path-planner",
    "group": "primary",
    "icon": "planner",
    "x": -230,
    "y": -173,
    "title": "Path Planner",
    "summary": "Tạo đường mục tiêu cho HWA, LKA và ELK.",
    "research": {
      "doc": "thiet-ke-path-planner",
      "section": "planner-cycle"
    }
  },
  {
    "id": "chuc-nang-adas",
    "kind": "doc",
    "doc": "chuc-nang-adas",
    "x": -2540,
    "y": -650,
    "eyebrow": "Thiết kế · khối Chức năng ADAS giả lập",
    "title": "Chức năng ADAS: khi nào can thiệp",
    "summary": "Khi nào HWA, LKA, ELK được yêu cầu: điều kiện chung, ngưỡng TLC, ý định tài xế, cảnh báo và trường hợp biên, theo UN R79, EU ELKS và Euro NCAP.",
    "status": "Bản nháp"
  },
  {
    "id": "thiet-ke-path-planner",
    "kind": "doc",
    "doc": "thiet-ke-path-planner",
    "x": -2160,
    "y": -650,
    "eyebrow": "Thiết kế · path planner G1",
    "title": "Thiết kế tính năng Path Planner",
    "summary": "Cách planner đáp ứng yêu cầu: interface, chu kỳ chạy, phân xử, path HWA và path can thiệp, giữ giới hạn và chịu lỗi.",
    "status": "Bản nháp"
  },
  {
    "id": "yeu-cau-path-planner",
    "kind": "doc",
    "doc": "yeu-cau-path-planner",
    "x": -2160,
    "y": 160,
    "eyebrow": "Yêu cầu · path planner G1",
    "title": "Yêu cầu phần mềm Path Planner",
    "summary": "Planner phải đạt gì: yêu cầu có ID, nguồn, cách kiểm chứng và trạng thái, là căn cứ để chấm planner.",
    "status": "Bản nháp"
  },
  {
    "id": "trien-khai-path-planner",
    "kind": "doc",
    "doc": "trien-khai-path-planner",
    "x": -1780,
    "y": -650,
    "eyebrow": "Triển khai · path planner G1",
    "title": "Triển khai Path Planner",
    "summary": "Đang chờ kế hoạch tính năng xong. Giữ các ghi chú thuật toán và bảng kỹ thuật ứng viên.",
    "status": "Chờ"
  },
  {
    "id": "benchmark-evaluation",
    "kind": "doc",
    "doc": "benchmark-evaluation",
    "x": -1400,
    "y": -650,
    "eyebrow": "Evaluation · prototype G1",
    "title": "Benchmark và Evaluation",
    "summary": "Thiết kế giả lập, kịch bản, lỗi bơm vào, tiêu chí chấm và cách so sánh các kỹ thuật.",
    "status": "Bản nháp",
    "mergedFrom": {
      "doc": "moi-truong-gia-lap",
      "section": "simulation-design"
    }
  },
  {
    "id": "conventions",
    "icon": "rules",
    "x": 403,
    "y": -483,
    "title": "Quy ước interface",
    "summary": "Quy định cách các khối trao đổi dữ liệu.",
    "research": {
      "doc": "interface-he-thong",
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
      "doc": "benchmark-evaluation",
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
      "doc": "benchmark-evaluation",
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
      "doc": "benchmark-evaluation",
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
      "doc": "benchmark-evaluation",
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
      "doc": "benchmark-evaluation",
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
      "doc": "benchmark-evaluation",
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
      "doc": "thiet-ke-path-planner",
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
      "doc": "benchmark-evaluation",
      "section": "benchmark-run"
    }
  },
  {
    "id": "interface-he-thong",
    "kind": "doc",
    "doc": "interface-he-thong",
    "x": -2540,
    "y": 160,
    "eyebrow": "Thiết kế · prototype G1",
    "title": "Interface và tín hiệu của G1",
    "summary": "Kiểu dữ liệu, đơn vị và quy ước trao đổi giữa các khối.",
    "status": "Bản nháp"
  },
  {
    "id": "diagram-sequence",
    "kind": "diagram",
    "diagram": "sequence",
    "doc": "thiet-ke-path-planner",
    "section": "planner-sequence",
    "x": -930,
    "y": 820,
    "eyebrow": "Góc nhìn động · Thiết kế, mục 3.1",
    "title": "Tuần tự trong một chu kỳ 25 ms",
    "summary": "Ai gửi gì cho ai, theo thứ tự, và deadline của chu kỳ.",
    "lanes": ["Bộ lập lịch", "Lớp nhận", "Planner", "Ego-motion (G4)", "Lateral Controller", "Khối ADAS", "ACC chạy thử"]
  },
  {
    "id": "diagram-states",
    "kind": "diagram",
    "diagram": "states",
    "doc": "thiet-ke-path-planner",
    "section": "arbitration-states",
    "x": -77,
    "y": 820,
    "eyebrow": "Góc nhìn động · Thiết kế, mục 5.1",
    "title": "Chuyển trạng thái phân xử",
    "summary": "Chức năng đang lái đổi thế nào theo từng sự kiện; nét đứt là chỗ chưa có yêu cầu."
  },
  {
    "id": "diagram-latency",
    "kind": "diagram",
    "diagram": "latency",
    "doc": "thiet-ke-path-planner",
    "section": "latency-chain",
    "x": 776,
    "y": 820,
    "eyebrow": "Góc nhìn thời gian · Thiết kế, mục 3.2",
    "title": "Chuỗi trễ từ cảm biến tới bánh xe",
    "summary": "Mỗi đoạn trễ dài bao nhiêu và khối nào bù."
  }
];

window.SPEC_REGIONS = [
  {
    "id": "docs",
    "text": "Báo cáo Research"
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
      "doc": "interface-he-thong",
      "section": "can"
    }
  },
  {
    "id": "e-state",
    "from": "state-estimator",
    "to": "path-planner",
    "label": "v_y, β",
    "research": {
      "doc": "interface-he-thong",
      "section": "state-estimator"
    }
  },
  {
    "id": "e-ego",
    "from": "ego-motion",
    "to": "path-planner",
    "label": "Δx, Δy, Δψ",
    "research": {
      "doc": "interface-he-thong",
      "section": "ego-motion"
    }
  },
  {
    "id": "e-lane",
    "from": "lane-model",
    "to": "path-planner",
    "label": "Vạch làn, cờ sự kiện",
    "research": {
      "doc": "interface-he-thong",
      "section": "lane-model"
    }
  },
  {
    "id": "e-perception",
    "from": "perception",
    "to": "path-planner",
    "label": "Vị trí, vận tốc vật thể",
    "research": {
      "doc": "interface-he-thong",
      "section": "perception"
    }
  },
  {
    "id": "e-functions",
    "from": "adas-functions",
    "to": "path-planner",
    "label": "Yêu cầu, TLC",
    "research": {
      "doc": "chuc-nang-adas",
      "section": "function-requests"
    }
  },
  {
    "id": "e-config",
    "from": "vehicle-config",
    "to": "path-planner",
    "label": "Tham số xe",
    "research": {
      "doc": "interface-he-thong",
      "section": "vehicle-config"
    }
  },
  {
    "id": "e-trajectory",
    "from": "path-planner",
    "to": "lateral-controller",
    "label": "Trajectory (Autoware)",
    "research": {
      "doc": "interface-he-thong",
      "section": "trajectory"
    }
  },
  {
    "id": "e-valid",
    "from": "path-planner",
    "to": "adas-functions",
    "label": "Path hợp lệ, chức năng đang lái",
    "research": {
      "doc": "thiet-ke-path-planner",
      "section": "path-status"
    }
  },
  {
    "id": "e-previous",
    "from": "path-planner",
    "to": "path-planner",
    "label": "Path chu kỳ trước",
    "research": {
      "doc": "thiet-ke-path-planner",
      "section": "planner-cycle"
    }
  }
];
