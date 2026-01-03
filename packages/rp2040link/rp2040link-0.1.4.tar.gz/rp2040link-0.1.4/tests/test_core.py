from rp2040link import Pico
from rp2040link.enums import Polarity

class DummyBoard:
    def __init__(self):
        self.calls = []

    def set_pin_mode_digital_output(self, pin):
        self.calls.append(("set_pin_mode_digital_output", int(pin)))

    def digital_write(self, pin, level):
        self.calls.append(("digital_write", int(pin), int(level)))

    def shutdown(self):
        self.calls.append(("shutdown",))

def test_active_low_initial_off_writes_high():
    pico = Pico()
    pico._board = DummyBoard()  # inject dummy
    pico.setup_output.active_low(14, initial_off=True)
    # active_low OFF should be level 1
    assert ("set_pin_mode_digital_output", 14) in pico._board.calls
    assert ("digital_write", 14, 1) in pico._board.calls

def test_active_high_initial_off_writes_low():
    pico = Pico(default_output_polarity=Polarity.ACTIVE_LOW)
    pico._board = DummyBoard()
    pico.setup_output.active_high(15, initial_off=True)
    # active_high OFF should be level 0
    assert ("set_pin_mode_digital_output", 15) in pico._board.calls
    assert ("digital_write", 15, 0) in pico._board.calls

def test_gpio_on_off_levels_follow_polarity():
    pico = Pico()
    pico._board = DummyBoard()
    pico.setup_output.active_low(2, initial_off=True)
    pico.gpio.on(2)
    pico.gpio.off(2)
    # on -> 0, off -> 1
    assert ("digital_write", 2, 0) in pico._board.calls
    assert ("digital_write", 2, 1) in pico._board.calls
