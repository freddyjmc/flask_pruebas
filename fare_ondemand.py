import datetime

def calculate_peak_fare(in_movement):
    current_time = datetime.datetime.now()
    hour = current_time.hour

    # Definir horas pico
    if (hour < 12) or (hour >= 22):
        if in_movement:
            return 0.1  # Tarifa en movimiento durante horas pico
        else:
            return   0.04  # Tarifa en espera durante horas pico
    else:
        if in_movement:
            return  0.05  # Tarifa en movimiento durante horas no pico
        else:
            return  0.02  # Tarifa en espera durante horas no pico
        
