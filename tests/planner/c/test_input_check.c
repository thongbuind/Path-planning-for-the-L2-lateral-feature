/* Unit tests of T1 counter check (input_check.h): Interface Control Document 4, AUTOSAR E2E
 * Profile 5 statuses. White-box, not part of the benchmark. */

#include "input_check.h"
#include "pp_test.h"

static pp_counter_check_t fresh(void)
{
    pp_counter_check_t c = {false, 0U, 0U};
    return c;
}

static void test_first_message_is_accepted_when_valid(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(!pp_counter_accept(&c, false, 0U, 0U, true, 3U, false));      /* nothing received yet */
    PP_CHECK(!pp_counter_accept(&c, true, 1000U, 7U, false, 3U, false));   /* valid = false */
    PP_CHECK(pp_counter_accept(&c, true, 2000U, 8U, true, 3U, false));
}

static void test_same_delivery_is_not_new(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 1U, true, 3U, false));
    PP_CHECK(!pp_counter_accept(&c, true, 1000U, 1U, true, 3U, false));    /* no new data */
}

static void test_steps_within_the_limit_are_accepted(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 10U, true, 3U, false));
    PP_CHECK(pp_counter_accept(&c, true, 2000U, 11U, true, 3U, false));    /* OK */
    PP_CHECK(pp_counter_accept(&c, true, 3000U, 14U, true, 3U, false));    /* OKSOMELOST, step 3 */
    PP_CHECK(pp_counter_accept(&c, true, 4000U, 0U, true, 3U, false) == false); /* step 242 */
}

static void test_counter_wraps(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 254U, true, 3U, false));
    PP_CHECK(pp_counter_accept(&c, true, 2000U, 255U, true, 3U, false));
    PP_CHECK(pp_counter_accept(&c, true, 3000U, 0U, true, 3U, false));
    PP_CHECK(pp_counter_accept(&c, true, 4000U, 2U, true, 3U, false));
}

static void test_repeated_or_stuck_counter_is_lost(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 5U, true, 3U, false));
    PP_CHECK(!pp_counter_accept(&c, true, 2000U, 5U, true, 3U, false));    /* REPEATED: copy delivered again */
    PP_CHECK(!pp_counter_accept(&c, true, 3000U, 5U, true, 3U, false));    /* stuck */
    PP_CHECK(pp_counter_accept(&c, true, 4000U, 6U, true, 3U, false));
}

static void test_wrong_sequence_is_lost_then_resynchronised(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 20U, true, 3U, false));
    PP_CHECK(!pp_counter_accept(&c, true, 2000U, 24U, true, 3U, false));   /* step 4 > 3 */
    PP_CHECK(pp_counter_accept(&c, true, 3000U, 25U, true, 3U, false));    /* step 1 from 24 */
}

static void test_invalid_message_keeps_the_sequence(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 30U, true, 3U, false));
    PP_CHECK(!pp_counter_accept(&c, true, 2000U, 31U, false, 3U, false));  /* lost, counter followed */
    PP_CHECK(pp_counter_accept(&c, true, 3000U, 32U, true, 3U, false));
}

static void test_resync_after_timeout(void)
{
    pp_counter_check_t c = fresh();
    PP_CHECK(pp_counter_accept(&c, true, 1000U, 40U, true, 3U, false));
    PP_CHECK(!pp_counter_accept(&c, true, 2000U, 50U, true, 3U, false)); /* within timeout */
    PP_CHECK(pp_counter_accept(&c, true, 3000U, 60U, true, 3U, true));  /* held timed out */
    PP_CHECK(!pp_counter_accept(&c, true, 4000U, 60U, true, 3U, true)); /* stuck: never */
}

int main(void)
{
    test_first_message_is_accepted_when_valid();
    test_same_delivery_is_not_new();
    test_steps_within_the_limit_are_accepted();
    test_counter_wraps();
    test_repeated_or_stuck_counter_is_lost();
    test_wrong_sequence_is_lost_then_resynchronised();
    test_invalid_message_keeps_the_sequence();
    test_resync_after_timeout();
    return PP_TEST_RESULT();
}
