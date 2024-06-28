import pytest
import time

from fare_ondemand import calculate_peak_fare

from model import Taximetro

@pytest.fixture
def taximeter():
	return Taximetro()

@pytest.fixture
def fare_move():
	is_move = True
	return calculate_peak_fare(is_move)

@pytest.fixture
def fare_stop():
	is_move = False
	return calculate_peak_fare(is_move)

def test_start(taximeter):
	taximeter.start()
	assert taximeter.start_road == True

def test_to_continue(taximeter):
	taximeter.continue_road()
	assert taximeter.start_road == False

def test_to_stop(taximeter):
	taximeter.stop()
	assert taximeter.start_road == False

def test_start_to_continue(taximeter, fare_move):
	taximeter.start()
	taximeter.continue_road()
	time.sleep(2)
	assert taximeter.in_movement == True
	taximeter.finish_road()
	assert taximeter.fare_total == 2 * fare_move, \
		f"Error, monto esperado: {2 * fare_move}, no: {taximeter.fare_total}"

def test_trip_start_to_finish(taximeter, fare_stop):
	taximeter.start()
	time.sleep(4)
	taximeter.finish_road()
	exp_fare = 4 * fare_stop
	assert taximeter.fare_total == exp_fare,\
		f"El total esperado es: {exp_fare}, no {taximeter.fare_total}"

def test_trip_movement(taximeter, fare_move, fare_stop):
	taximeter.start()
	taximeter.continue_road()
	time.sleep(10)
	taximeter.stop()
	time.sleep(4)
	taximeter.finish_road()
	exp_fare = (10 * fare_move) + (4 * fare_stop)
	assert taximeter.fare_total == exp_fare, \
		f"El total esperado es: {exp_fare}, no {taximeter.fare_total}"
