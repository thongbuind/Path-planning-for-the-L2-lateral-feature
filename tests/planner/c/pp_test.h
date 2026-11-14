/*
 * Minimal check macros for the C unit tests of the planner units. White box,
 * not part of the benchmark (Software Qualification Test Specification section 3).
 */

#ifndef PP_TEST_H
#define PP_TEST_H

#include <math.h>
#include <stdio.h>

static int pp_test_failures = 0;

#define PP_CHECK(cond)                                                              \
    do {                                                                            \
        if (!(cond)) {                                                              \
            (void)fprintf(stderr, "%s:%d: check failed: %s\n", __FILE__, __LINE__,  \
                          #cond);                                                   \
            pp_test_failures++;                                                     \
        }                                                                           \
    } while (0)

#define PP_CHECK_NEAR(actual, expected, tol)                                        \
    do {                                                                            \
        const double pp_a = (double)(actual);                                       \
        const double pp_e = (double)(expected);                                     \
        if (!(fabs(pp_a - pp_e) <= (double)(tol))) {                                \
            (void)fprintf(stderr, "%s:%d: %s = %.9g, expected %.9g (tol %.3g)\n",   \
                          __FILE__, __LINE__, #actual, pp_a, pp_e, (double)(tol));  \
            pp_test_failures++;                                                     \
        }                                                                           \
    } while (0)

#define PP_TEST_RESULT()                                                            \
    ((pp_test_failures == 0) ? 0 : ((void)fprintf(stderr, "%d failure(s)\n",        \
                                                  pp_test_failures), 1))

#endif /* PP_TEST_H */
