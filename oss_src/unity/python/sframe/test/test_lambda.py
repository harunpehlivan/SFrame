'''
Copyright (C) 2016 Turi
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
'''
import multiprocessing
import time
import unittest
import logging
import array
from ..connect import main as glconnect
from ..cython import cy_test_utils


def fib(i):
    return 1 if i <= 2 else fib(i - 1) + fib(i - 2)


class LambdaTests(unittest.TestCase):

    def test_simple_evaluation(self):
        x = 3
        self.assertEqual(glconnect.get_unity().eval_lambda(lambda y: y + x, 0), 3)
        self.assertEqual(glconnect.get_unity().eval_lambda(lambda y: y + x, 1), 4)
        self.assertEqual(glconnect.get_unity().eval_lambda(lambda x: x.upper(), 'abc'), 'ABC')
        self.assertEqual(glconnect.get_unity().eval_lambda(lambda x: x.lower(), 'ABC'), 'abc')
        self.assertEqual(glconnect.get_unity().eval_lambda(fib, 1), 1)

    def test_exception(self):
        x = 3
        self.assertRaises(RuntimeError, glconnect.get_unity().eval_lambda, lambda y: x / y, 0)
        self.assertRaises(
            RuntimeError,
            glconnect.get_unity().parallel_eval_lambda,
            lambda y: x / y,
            [0 for _ in range(10)],
        )

    def test_parallel_evaluation(self):
        xin = 33
        repeat = 8
        # execute the task bulk using one process to get a baseline
        start_time = time.time()
        glconnect.get_unity().eval_lambda(lambda x: [fib(i) for i in x], [xin]*repeat)
        single_thread_time = time.time() - start_time
        logging.info(f"Single thread lambda eval takes {single_thread_time} secs")

        # execute the task in parallel
        start_time = time.time()
        ans_list = glconnect.get_unity().parallel_eval_lambda(lambda x: fib(x), [xin]*repeat)
        multi_thread_time = time.time() - start_time
        logging.info(f"Multi thread lambda eval takes {multi_thread_time} secs")

        # test the speed up by running in parallel
        nproc = multiprocessing.cpu_count()
        if (nproc > 1 and multi_thread_time > (single_thread_time / 1.5)):
            logging.warning(
                f"Slow parallel processing: single thread takes {single_thread_time} secs, multithread on {nproc} procs takes {multi_thread_time} secs"
            )


        # test accuracy
        ans = fib(xin)
        for a in ans_list:
            self.assertEqual(a, ans)

    @unittest.skip("Disabling crash recovery test")
    def test_crash_recovery(self):
        import time, sys
        ls = range(1000)

        def good_fun(x):
            return x

        def bad_fun(x):
            if (x+1) % 251 == 0:
                cy_test_utils.force_exit_fun()  # this will force the worker process to exit
            return x
        self.assertRaises(RuntimeError, lambda: glconnect.get_unity().parallel_eval_lambda(lambda x: bad_fun(x), ls))
        glconnect.get_unity().parallel_eval_lambda(lambda x: good_fun(x), ls)
