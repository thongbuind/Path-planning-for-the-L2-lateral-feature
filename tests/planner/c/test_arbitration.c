/* T9 request ownership, completion, and preemption (PP-SWR-030 to 047). */

#include "arbitration.h"
#include "pp_test.h"

static pp_arbitration_input_t available(const pp_function_requests_t *req)
{
    const pp_arbitration_input_t in = {
        .requests = req, .path_available = true, .hwa_available = true,
        .can_start = {true, true}, .can_continue = {true, true}, .hold_s = 0.25,
    };
    return in;
}

static void test_completion_waits_and_belongs_to_its_function(void)
{
    pp_arbitration_memory_t mem = {0};
    pp_function_requests_t req = {0};
    pp_arbitration_input_t in = available(&req);
    pp_arbitration_t out;
    req.requests[0].state = PP_REQUEST_STATE_REQUEST;
    req.requests[1].state = PP_REQUEST_STATE_REQUEST;
    req.requests[2].state = PP_REQUEST_STATE_REQUEST;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.starting && out.active_function == PP_ACTIVE_FUNCTION_ELK);
    PP_CHECK(out.lka_phase == PP_INTERVENTION_PHASE_NONE);

    in.t0_us = 25000U;
    in.can_finish[1] = true;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(!out.starting && out.elk_phase == PP_INTERVENTION_PHASE_ACTIVE);
    in.t0_us = 200000U;
    in.can_finish[1] = false;
    pp_arbitrate(&mem, &in, &out);
    in.t0_us = 225000U;
    in.can_finish[1] = true;
    pp_arbitrate(&mem, &in, &out);
    in.t0_us = 450000U;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.elk_phase == PP_INTERVENTION_PHASE_ACTIVE);
    in.t0_us = 475000U;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.starting && out.active_function == PP_ACTIVE_FUNCTION_LKA);
    PP_CHECK(out.elk_phase == PP_INTERVENTION_PHASE_COMPLETED);
    PP_CHECK(out.lka_phase == PP_INTERVENTION_PHASE_ACTIVE);

    in.t0_us += PP_PLANNER_PERIOD_US;
    req.requests[2].state = PP_REQUEST_STATE_STANDBY;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_LKA);
    PP_CHECK(out.elk_phase == PP_INTERVENTION_PHASE_NONE);
}

static void test_late_and_expired_requests_require_a_new_request(void)
{
    pp_arbitration_memory_t mem = {0};
    pp_function_requests_t req = {0};
    pp_arbitration_input_t in = available(&req);
    pp_arbitration_t out;
    req.requests[2].state = PP_REQUEST_STATE_REQUEST;
    in.elk_too_late = true;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_NONE);
    in.elk_too_late = false;
    in.t0_us += PP_PLANNER_PERIOD_US;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_NONE);

    req.requests[2].state = PP_REQUEST_STATE_STANDBY;
    in.t0_us += PP_PLANNER_PERIOD_US;
    pp_arbitrate(&mem, &in, &out);
    req.requests[2].state = PP_REQUEST_STATE_REQUEST;
    in.t0_us += PP_PLANNER_PERIOD_US;
    in.requests_rx_us = in.t0_us;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.starting && out.active_function == PP_ACTIVE_FUNCTION_ELK);
    in.t0_us = in.requests_rx_us + PP_INTERVENTION_MAX_US - PP_PLANNER_PERIOD_US;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_ELK);
    in.t0_us += PP_PLANNER_PERIOD_US;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.cancelled && out.active_function == PP_ACTIVE_FUNCTION_NONE);
    PP_CHECK(out.elk_phase == PP_INTERVENTION_PHASE_NONE);
}

static void test_invalid_path_blocks_current_request(void)
{
    pp_arbitration_memory_t mem = {0};
    pp_function_requests_t req = {0};
    pp_arbitration_input_t in = available(&req);
    pp_arbitration_t out;
    req.requests[1].state = PP_REQUEST_STATE_REQUEST;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_LKA);
    in.path_available = false;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_NONE);
    in.path_available = true;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.active_function == PP_ACTIVE_FUNCTION_NONE);
    req.requests[1].state = PP_REQUEST_STATE_STANDBY;
    pp_arbitrate(&mem, &in, &out);
    req.requests[1].state = PP_REQUEST_STATE_REQUEST;
    pp_arbitrate(&mem, &in, &out);
    PP_CHECK(out.starting && out.active_function == PP_ACTIVE_FUNCTION_LKA);
}

int main(void)
{
    test_completion_waits_and_belongs_to_its_function();
    test_late_and_expired_requests_require_a_new_request();
    test_invalid_path_blocks_current_request();
    return PP_TEST_RESULT();
}
