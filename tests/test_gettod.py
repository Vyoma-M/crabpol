"""Unit tests for `Get_TOD` wrappers.

These tests mock out filesystem I/O (FITS and ASCII reads) so they run
as lightweight unit tests without Planck data files.
"""

import numpy as np
from types import SimpleNamespace
import os
import pytest
import gettod
from gettod import Get_TOD, GetTODConfig, TOD


class DummyHDUList:
    def __init__(self, data):
        self._hdu = SimpleNamespace(data=data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def __getitem__(self, idx):
        if idx == 1:
            return self._hdu
        raise IndexError


def make_structured_data(n=4):
    dtype = [
        ("theta", float),
        ("phi", float),
        ("qweight", float),
        ("uweight", float),
        ("signal", float),
    ]
    arr = np.zeros(n, dtype=dtype)
    arr["theta"] = np.linspace(0.1, 1.0, n)
    arr["phi"] = np.linspace(0.2, 1.1, n)
    arr["qweight"] = 0.5
    arr["uweight"] = 0.2
    arr["signal"] = np.arange(n)
    return arr


def test_tod(monkeypatch, tmp_path):
    # prepare fake data folder
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "M1").mkdir()
    (data_dir / "PR2-3").mkdir()

    # patch utils.get_dets to return one detector
    monkeypatch.setattr(gettod.utils, "get_dets", lambda freq: ["DET1"])

    # patch fits.open to return our dummy HDU list
    struct = make_structured_data(n=5)
    monkeypatch.setattr(gettod.fits, "open", lambda path: DummyHDUList(struct))

    cfg = GetTODConfig(data_path=str(data_dir), nside=8, freq=100)
    loader = Get_TOD(config=cfg)

    tod = loader.assemble_tod()
    assert isinstance(tod, TOD)
    assert tod.signal.size == 5
    assert tod.pixels.size == 5
    assert tod.weights.shape[1] == 5


def test_tod_withcc(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "M1").mkdir()
    prdir = data_dir / "PR2-3"
    prdir.mkdir()

    monkeypatch.setattr(gettod.utils, "get_dets", lambda freq: ["DET1"])
    struct = make_structured_data(n=3)
    monkeypatch.setattr(gettod.fits, "open", lambda path: DummyHDUList(struct))

    # prepare a fake CC table
    fake_cc = {"UCxCC": np.array([2.0]), "Detector-name": np.array(["DET1"])}
    monkeypatch.setattr(gettod.ascii, "read", lambda path: fake_cc)

    cfg = GetTODConfig(
        data_path=str(data_dir), nside=8, freq=100, withcc=True, bg_subtraction=False
    )
    loader = Get_TOD(config=cfg)

    tod = loader.tod_withcc()
    assert isinstance(tod, TOD)
    # signal should be scaled by UCxCC (2.0)
    assert np.all(tod.signal == struct["signal"].ravel() * 2.0)
