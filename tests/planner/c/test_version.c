#include <string.h>

#include "pp_planner.h"
#include "pp_test.h"

static void check_version(const char *text, const char *prefix, const char *again)
{
    PP_CHECK(text != NULL);
    if (text != NULL) {
        PP_CHECK(strncmp(text, prefix, strlen(prefix)) == 0);
        PP_CHECK(strstr(text, " commit ") != NULL);
        PP_CHECK(strstr(text, " calibration ") != NULL);
        PP_CHECK(text == again);
    }
}

static void test_version_names_build(void)
{
    check_version(pp_lcc_version(), "pp_lcc ", pp_lcc_version());
    check_version(pp_lkaelk_version(), "pp_lkaelk ", pp_lkaelk_version());
    PP_CHECK(strstr(pp_lcc_version(), " t7 ") != NULL);
}

int main(void)
{
    test_version_names_build();
    return PP_TEST_RESULT();
}
