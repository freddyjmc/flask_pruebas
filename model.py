import time
from datetime import datetime
from fare_ondemand import calculate_peak_fare
from Db_psw import Database
import logging

# Configuración de logging
logging.basicConfig(filename='taximetro.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class Taximetro:
    fare_movement = 0.05  # tarifa en movimiento en centimos de euro por segundo
    fare_stop = 0.02  # tarifa en reposo de centimos en euro por segundo

    def __init__(self, user):
        self.start_road = False
        self.last_status_change = None
        self.fare_total = 0
        self.in_movement = False
        self.start_time = None
        self.end_time = None
        self.user = user[0]
        logging.info(f"Taximetro inicializado para el usuario {self.user}")

    def calculate_fare(self):
        now = time.time()
        if self.last_status_change is not None:
            time_elapsed = now - self.last_status_change
            fare = calculate_peak_fare(self.in_movement)
            self.fare_total += round(time_elapsed * fare, 2)
        self.last_status_change = now

    def start(self):
        self.start_road = True
        self.last_status_change = time.time()
        self.start_time = datetime.now()
        logging.info("Comenzar la carrera.")
        print("Comenzar la carrera.")

    def stop(self):
        if self.in_movement:
            self.calculate_fare()
            self.in_movement = False
            logging.info("El taxi se ha detenido.")
            print("El taxi se ha detenido.")
        else:
            print("Inicie el movimiento")

    def continue_road(self):
        if self.start_road and self.in_movement == False:
            self.calculate_fare()
            self.in_movement = True
            logging.info("El taxi está en movimiento.")
            print("El taxi está en movimiento.")
        else:
            print("El taxi ya esta en movimiento.")


    def finish_road(self):
        if self.start_road:
            self.calculate_fare()
            self.start_road = False
            self.end_time = datetime.now()
            logging.info(f"La carrera ha terminado. El total a cobrar es: {self.fare_total:.2f} euros.")
            print(f"La carrera ha terminado. El total a cobrar es: {self.fare_total:.2f} euros.")
            self.save_ride_history()
            db = Database()
            db.add_trip_database(self.start_time, self.end_time, self.fare_total, self.user)
            return self.fare_total
        else:
            print("La carrera no ha sido iniciada")

    def save_ride_history(self):
        with open('rides_history.txt', mode='a', encoding='utf-8') as file:
            file.write(f"Fecha de inicio: {self.start_time}\n")
            file.write(f"Fecha de fin: {self.end_time}\n")
            file.write(f"Total a cobrar: €{self.fare_total:.2f}\n")
            file.write("=======================================\n")
        logging.info("Historial de viaje guardado.")

    def view_history(self):
        try:
            with open('rides_history.txt', mode='r', encoding='utf-8') as file:
                print("Historial de carreras:")
                for line in file:
                    print(line.strip())
            logging.info("Historial de carreras visualizado.")
        except FileNotFoundError:
            print("No hay carreras registradas.")
            logging.warning("Intento de visualizar historial fallido: archivo no encontrado.")

    def history_db(self):
        db = Database()
        db.show_history(self.user)
        logging.info("Historial de la base de datos visualizado.")

    def clear(self):
        self.start_road = False
        self.last_status_change = None
        self.fare_total = 0
        self.in_movement = False
        self.start_time = None
        self.end_time = None
        logging.info("Datos del taxímetro reiniciados.")

