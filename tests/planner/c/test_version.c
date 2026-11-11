/* Unit test of pp_version() (interfaces/c/pp_planner.h). */

#include <string.h>

#include "pp_planner.h"
#include "pp_test.h"

static void test_version_names_build(void)
{
    const char *text = pp_version();
    PP_CHECK(text != NULL);
    if (text != NULL) {
        PP_CHECK(strncmp(text, "pp_planner ", 11U) == 0);
        PP_CHECK(strstr(text, " commit ") != NULL);
        PP_CHECK(strstr(text, " calibration ") != NULL);
        PP_CHECK(text == pp_version());   /* constant: same string every call */
    }
}

int main(void)
{
    test_version_names_build();
    return PP_TEST_RESULT();
}
