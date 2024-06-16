from __future__ import annotations

import pytest

redun = pytest.importorskip("redun")

from pathlib import Path

from quacc import SETTINGS, flow, job, redecorate, strip_decorator, subflow
from quacc.wflow_tools.customizers import customize_funcs


@pytest.fixture()
def scheduler():
    return redun.Scheduler()



def test_strip_decorators():
    @job
    def add(a, b):
        return a + b

    @flow
    def add2(a, b):
        return a + b

    @subflow
    def add3(a, b):
        return a + b

    stripped_add = strip_decorator(add)
    assert stripped_add(1, 2) == 3

    stripped_add2 = strip_decorator(add2)
    assert stripped_add2(1, 2) == 3

    stripped_add3 = strip_decorator(add3)
    assert stripped_add3(1, 2) == 3


def test_change_settings_redecorate_job(tmp_path_factory, scheduler):
    tmp_dir1 = tmp_path_factory.mktemp("dir1")

    @job
    def write_file_job(name="job.txt"):
        with open(Path(SETTINGS.RESULTS_DIR, name), "w") as f:
            f.write("test file")

    write_file_job = redecorate(
        write_file_job, job(settings_swap={"RESULTS_DIR": tmp_dir1})
    )
    scheduler.run(write_file_job())
    assert Path(tmp_dir1 / "job.txt").exists()


def test_change_settings_redecorate_flow(tmp_path_factory, scheduler):
    tmp_dir2 = tmp_path_factory.mktemp("dir2")

    @job
    def write_file_job(name="job.txt"):
        with open(Path(SETTINGS.RESULTS_DIR, name), "w") as f:
            f.write("test file")

    @flow
    def write_file_flow(name="flow.txt", job_decorators=None):
        write_file_job_ = customize_funcs(
            ["write_file_job"], [write_file_job], decorators=job_decorators
        )
        return write_file_job_(name=name)

    # Test with redecorating a job in a flow
    scheduler.run(
        write_file_flow(
            job_decorators={
                "write_file_job": job(settings_swap={"RESULTS_DIR": tmp_dir2})
            }
        )
    )
    assert Path(tmp_dir2 / "flow.txt").exists()
