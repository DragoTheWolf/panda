"""Regression checks for selecting firmware on original C3 versus H7 boards."""
from unittest.mock import Mock

import pytest

from panda import Panda, PandaDFU
from panda.python.constants import McuType


@pytest.mark.parametrize("hw_type,mcu", [
  (Panda.HW_TYPE_DOS, McuType.F4),
  (Panda.HW_TYPE_RED_PANDA, McuType.H7),
  (Panda.HW_TYPE_TRES, McuType.H7),
  (Panda.HW_TYPE_CUATRO, McuType.H7),
])
def test_firmware_selection(hw_type, mcu):
  p = Panda.__new__(Panda)
  p.get_type = Mock(return_value=hw_type)
  assert p.get_mcu_type() == mcu
  assert mcu.config.app_address == (0x8004000 if mcu == McuType.F4 else 0x8020000)
  assert mcu.config.app_fn == ("panda.bin.signed" if mcu == McuType.F4 else "panda_h7.bin.signed")


@pytest.mark.parametrize("hw_type", [b'\x00', b'\x08', b'\xff'])
def test_unknown_board_is_not_assumed_f4(hw_type):
  p = Panda.__new__(Panda)
  p.get_type = Mock(return_value=hw_type)
  with pytest.raises(ValueError):
    p.get_mcu_type()


def test_dfu_serial_uses_mcu_specific_conversion():
  serial = '010002000300040005000600'
  assert PandaDFU.st_serial_to_dfu_serial(serial, McuType.F4) == '000800100004'
  assert PandaDFU.st_serial_to_dfu_serial(serial, McuType.H7) == '000800060004'
