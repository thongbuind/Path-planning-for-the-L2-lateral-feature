/* English labels for the simulation. The URL language takes precedence over the saved site preference. */
(() => {
  const requested = new URLSearchParams(location.search).get('lang');
  let saved = 'vi';
  try { saved = localStorage.getItem('spec-web.language') || 'vi'; } catch (_) {}
  const en = requested ? requested === 'en' : saved === 'en';
  document.documentElement.lang = en ? 'en' : 'vi';
  if (!en) return;
  const words = {
    'SIL, chạy thời gian thực':'Real-time SIL', '0,5×':'0.5×', 'Đổi giao diện sáng tối':'Toggle light and dark theme',
    'Chọn ca mô phỏng':'Select a simulation case', 'Chạy planner':'Run planner', 'Chạy lại':'Run again',
    'Đang kết nối server…':'Connecting to server…', 'Tình huống':'Scenario', 'Biến thể':'Variants', 'Lỗi tiêm':'Injected faults',
    'Tìm: S1, cua, xe tải, xi-nhan…':'Search: S1, curve, truck, turn signal…', 'Tìm tình huống':'Search scenarios',
    'Lọc theo chức năng':'Filter by function', 'Lỗi bắt đầu':'Fault trigger', 'Theo định nghĩa của lỗi':'As defined by the fault',
    'Khi LKA can thiệp':'When LKA intervenes', 'Khi ELK can thiệp':'When ELK intervenes', 'Khi LKA hoặc ELK can thiệp':'When LKA or ELK intervenes',
    'Môi trường':'Environment', 'Xe, seed, ACC':'Vehicle, seed, ACC', 'Xe':'Vehicle', 'Theo kịch bản':'As defined by the scenario',
    'Tắt':'Off', 'Bật, đọc LateralLimits':'On, use LateralLimits', 'Bật, bỏ qua LateralLimits':'On, ignore LateralLimits',
    'Màn hình mô phỏng':'Simulation view', 'Bản đồ lộ trình':'Route map', 'Điều khiển lượt chạy':'Run controls',
    'Tạm dừng hoặc tiếp tục (Space)':'Pause or resume (Space)', 'Dừng lượt chạy':'Stop run', 'Tốc độ chạy':'Playback speed',
    'Không canh nhịp: chạy nhanh nhất máy cho phép':'Unpaced: run as fast as the machine permits', 'Tối đa':'Maximum',
    'Thời gian mô phỏng, kéo để xem lại khi đã tạm dừng hoặc chạy xong':'Simulation time; drag to review when paused or finished',
    'Dạng hiển thị':'Display mode', 'Biểu đồ':'Chart', 'Bảng':'Table', 'Biểu đồ theo thời gian':'Time-series charts',
    'Biểu đồ chức năng, lệch tâm làn, a_y, góc vô lăng và thời gian tính, vẽ dần theo thời gian chạy':'Function, lane offset, a_y, steering wheel angle and computation time plotted during the run',
    'Thông số':'Parameters', 'Kết quả':'Results', 'Bài thử đã chọn':'Selected test', 'Tất cả':'All', 'Khác':'Other', 'Bỏ hết lỗi':'Clear all faults',
    'Mặt đường ướt, μ = 0,5':'Wet road, μ = 0.5', 'Camera trễ 150 ms (mặc định 100)':'Camera latency 150 ms (default 100)',
    'Nhiễu cảm biến vật thể ×1,5 (mưa)':'Object sensor noise ×1.5 (rain)', 'Đang khởi động simulator…':'Starting simulator…',
    'Đang khởi động simulator và nạp planner…':'Starting simulator and loading planner…', 'Đang chấm kết quả…':'Evaluating results…',
    'Chọn tình huống và lỗi ở bên trái, rồi bấm Chạy planner. Planner thật chạy theo thời gian thực trên máy này.':'Select a scenario and faults on the left, then select Run planner. The actual planner runs in real time on this machine.',
    'Thông số của planner và của xe sẽ cập nhật theo từng chu kỳ 25 ms khi lượt chạy bắt đầu.':'Planner and vehicle parameters update every 25 ms once the run starts.',
    'Chưa có lượt chạy.':'No run yet.', 'Tốc độ':'Speed', 'Vô lăng':'Steering wheel', 'Lệch tâm làn, + trái':'Lane-center offset, + left', 'DLC trái':'Left DLC', 'DLC phải':'Right DLC',
    'a_y, lọc R79':'a_y, R79-filtered', 'Góc vô lăng':'Steering wheel angle', 'Vào':'Inputs', 'Ra':'Outputs', 'mỗi 25 ms, 40 Hz':'every 25 ms, 40 Hz',
    'Yêu cầu chức năng':'Function requests', 'TLC của LKA, ELK':'LKA, ELK TLC', 'Tầm nhìn lane model':'Lane model view range',
    'Tuổi dữ liệu camera':'Camera data age', 'Chức năng đang lái':'Active steering function', 'Path hợp lệ':'Valid path', 'Path không hợp lệ':'Invalid path',
    'Giới hạn ngang':'Lateral limit', 'Horizon quan sát':'Observed horizon', 'Thời gian tính':'Computation time',
    'Không có lỗi hay điều kiện xấu: ca chuẩn.':'No faults or adverse conditions: nominal case.', 'suốt lượt chạy':'throughout the run',
    'Điều kiện':'Conditions', 'chấm sáng khi đang tác động':'lit while active', 'Lệch tâm lớn nhất':'Maximum lane-center offset',
    'DLC nhỏ nhất':'Minimum DLC', 'a_y lớn nhất, lọc R79':'Maximum a_y, R79-filtered', 'Thời gian tính lớn nhất':'Maximum computation time',
    'Số liệu đến giờ':'Metrics so far', 'Kết luận của evaluator (tiêu chí, chỉ tiêu hiệu năng) có sau khi lượt chạy kết thúc.':'The evaluator results (criteria and performance targets) are available when the run ends.',
    'Đạt toàn bộ tiêu chí áp dụng':'All applicable criteria passed', 'Đạt':'Pass', 'Không đạt':'Fail', 'Tiêu chí':'Criteria',
    'cả lượt chạy, trượt xếp trước':'entire run, failures first', 'Chỉ tiêu hiệu năng':'Performance targets', 'cả lượt chạy':'entire run',
    'Đã dừng':'Stopped', 'Tạm dừng':'Paused', 'Đang chấm':'Evaluating', 'Đang chạy':'Running', 'Có':'Yes', 'Không':'No',
    'vạch thật':'ground-truth marking', 'vạch lane model':'lane model marking', 'Lệch tâm làn':'Lane-center offset',
    'a_y xe, lọc R79':'Vehicle a_y, R79-filtered', 'mép làn':'lane boundary', 'chu kỳ 25 ms':'25 ms cycle',
    'Chức năng':'Function', 'Lỗi đang tiêm':'Active injected faults', 'Giới hạn':'Limit', 'Thời điểm':'Time',
    'Lệch tâm (cm)':'Lane offset (cm)', 'DLC nhỏ nhất (cm)':'Minimum DLC (cm)', 'a_y lọc (m/s²)':'Filtered a_y (m/s²)',
    'Vô lăng (°)':'Steering wheel (°)', 'Thời gian tính (ms)':'Computation time (ms)', 'Không có chức năng':'No active function'
  };
  function translate(value) {
    const trimmed = value.trim();
    if (Object.hasOwn(words, trimmed)) return value.replace(trimmed, words[trimmed]);
    return value.replace(/^Không đọc được danh mục từ server \((.*?)\)\. Mô phỏng cần máy chủ cục bộ\. Chạy: (.*?) rồi mở (.*)$/, 'Cannot load the catalog from the server ($1). Simulation requires a local server. Run: $2, then open $3')
      .replace(/^Trang cần server để chạy planner thật\. Chạy: (.*?) rồi mở (.*)$/, 'The actual planner requires a server. Run: $1, then open $2')
      .replace(/^Không kết nối được server\. Mô phỏng cần máy chủ cục bộ\. Chạy: (.*?) rồi mở (.*)$/, 'Cannot connect to the server. Simulation requires a local server. Run: $1, then open $2')
      .replace(/^Server từ chối yêu cầu \((.*?)\)$/, 'Server rejected the request ($1)')
      .replace(/(\d+) xe khác$/, '$1 other vehicles')
      .replace(/^Mất kết nối với server giữa chừng$/, 'Connection to the server was lost during the run')
      .replace(/^Lượt chạy kết thúc đột ngột$/, 'The run ended unexpectedly')
      .replace(/^Đặt lỗi (.*?) và môi trường của tổ hợp (.*)$/, 'Set faults $1 and the environment for combination $2')
      .replace(/^(.*?): trục cơ sở (.*?) m, rộng (.*?) m, (.*?) kg$/, '$1: wheelbase $2 m, width $3 m, $4 kg')
      .replace(/^Planner thật \(libpp_planner\) chạy trong simulator SIL của repo, mỗi lần bấm Chạy\. Bản (.*)\.$/, 'The actual planner (libpp_planner) runs in the repository SIL simulator each time Run is selected. Version $1.')
      .replace(/^giới hạn R79: (.*?) liên tục, (.*?) trong ≤ (.*?) s$/, 'R79 limit: $1 continuous, $2 for ≤ $3 s')
      .replace(/^Camera trễ (.*?) ms \(mặc định (.*?) ms\)$/, 'Camera latency $1 ms (default $2 ms)')
      .replace(/^Mặt đường ướt, μ = (.*)$/, 'Wet road, μ = $1').replace(/^Nhiễu cảm biến vật thể ×(.*)$/, 'Object sensor noise ×$1')
      .replace(/^Trễ EPS thật (.*) ms$/, 'Actual EPS delay $1 ms')
      .replace(/^Nhiễu vạch/, 'Lane marking noise').replace(/^Mất vạch/, 'Lane marking loss').replace(/^Mất mọi biên$/, 'All boundaries lost')
      .replace(/^Mất mọi vạch và biên đường$/, 'All lane markings and road edges lost')
      .replace(/^c0 nhảy/, 'c0 jump').replace(/không có cờ/g, 'unflagged').replace(/^Tầm nhìn lane model:/, 'Lane model view range:')
      .replace(/^Lỗi lane model:/, 'Lane model fault:').replace(/^Ego-motion lỗi$/, 'Ego-motion fault').replace(/^Ego-motion không hợp lệ$/, 'Invalid ego-motion')
      .replace(/^Mất (\d+) gói (.*?) liên tiếp, cứ (\d+) gói một lần$/, 'Loss of $1 consecutive $2 packets every $3 packets')
      .replace(/^Mất 1 trong (\d+) gói (.*)$/, 'Loss of 1 in $1 $2 packets')
      .replace(/^Counter (.*?) đứng yên$/, '$1 counter stuck').replace(/^Counter (.*?) nhảy (.*)$/, '$1 counter skips $2').replace(/^Counter (.*?) lặp$/, '$1 counter repeats')
      .replace(/^Stamp (.*?) sớm \+(.*?) ms so với thời điểm nhận$/, '$1 timestamp $2 ms ahead of reception')
      .replace(/^CRC sai trên khung (.*)$/, 'Incorrect CRC on $1 frame').replace(/^valid = false trên (.*)$/, 'valid = false on $1')
      .replace(/^Jitter ±(.*?) ms trên (.*)$/, 'Jitter ±$1 ms on $2').replace(/^Gói (.*?) đến muộn sau gói mới hơn$/, '$1 packet arrives after a newer packet')
      .replace(/^Ngừng gửi (.*)$/, '$1 transmission stopped').replace(/^(.*?) ngoài dải: (.*)$/, '$1 out of range: $2')
      .replace(/^Lỗi cảm biến (.*?): (.*)$/, '$1 sensor fault: $2')
      .replace(/trái ngoài \(L2\)/g, 'outer left (L2)').replace(/trái làn mình \(L1\)/g, 'ego-lane left (L1)')
      .replace(/phải làn mình \(R1\)/g, 'ego-lane right (R1)').replace(/phải ngoài \(R2\)/g, 'outer right (R2)')
      .replace(/^Mất chuỗi gói$/, 'Packet burst loss').replace(/^Mất gói$/, 'Packet loss').replace(/^Counter đứng yên$/, 'Counter stuck')
      .replace(/^Counter nhảy$/, 'Counter skip').replace(/^Counter lặp$/, 'Counter repeat').replace(/^Stamp sớm$/, 'Future timestamp')
      .replace(/^CRC sai$/, 'Incorrect CRC').replace(/^Gói đến muộn$/, 'Late packet').replace(/^Ngừng gửi$/, 'Transmission stopped').replace(/^Ngoài dải$/, 'Out of range')
      .replace(/^khi LKA can thiệp$/, 'when LKA intervenes').replace(/^khi ELK can thiệp$/, 'when ELK intervenes')
      .replace(/^khi LKA hoặc ELK can thiệp$/, 'when LKA or ELK intervenes').replace(/ → hết$/, ' → end')
      .replace(/^Chạm/, 'Reached').replace(/^Sẵn sàng: /, 'Ready: ').replace(/không lỗi/g, 'no faults').replace(/(\d+) lỗi/g, '$1 faults')
      .replace(/^Đang chạy · /, 'Running · ').replace(/tối đa/g, 'maximum').replace(/^Tạm dừng ở /, 'Paused at ')
      .replace(/^Đã dừng ở /, 'Stopped at ').replace(/^Xong · /, 'Finished · ').replace(/Không đạt/g, 'Fail').replace(/Đạt/g, 'Pass')
      .replace(/^Trượt (\d+) tiêu chí$/, '$1 criteria failed').replace(/ tiêu chí áp dụng cho ca này/, ' criteria apply to this case')
      .replace(/\. Trượt: /, '. Failed: ').replace(/ · đo /, ' · measured ').replace(/ · giới hạn /, ' · limit ')
      .replace(/^Tầm nhìn lane model /, 'Lane model view range ').replace(/^Quỹ đạo (.+) s, 31 điểm$/, 'Trajectory $1 s, 31 points')
      .replace(/\. Thời gian tính là đồng hồ thật của máy, gồm cả adapter SIL \(ctypes\), đo trong lúc chạy thời gian thực\.$/, '. Computation time is wall-clock time on this machine, including the SIL adapter (ctypes), measured during real-time execution.')
      .replace(/^Lỗi: /, 'Faults: ').replace(/ đang lái$/, ' in control').replace(/ đã chọn$/, ' selected');
  }
  function visit(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      if (node.parentElement && /^(SCRIPT|STYLE|TEXTAREA)$/.test(node.parentElement.tagName)) return;
      const translated = translate(node.nodeValue); if (translated !== node.nodeValue) node.nodeValue = translated;
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      for (const attr of ['title', 'aria-label', 'placeholder']) if (node.hasAttribute(attr)) {
        const value = node.getAttribute(attr), translated = translate(value);
        if (translated !== value) node.setAttribute(attr, translated);
      }
      node.childNodes.forEach(visit);
    }
  }
  visit(document.body);
  new MutationObserver(records => records.forEach(r => {
    if (r.type === 'characterData') visit(r.target);
    else if (r.type === 'attributes') visit(r.target);
    else r.addedNodes.forEach(visit);
  })).observe(document.body, { subtree:true, childList:true, characterData:true, attributes:true, attributeFilter:['title','aria-label','placeholder'] });
})();
