from model import Taximetro
import time
from logger import log_info, log_warning, log_error

def main(user):
    taximetro = Taximetro(user)

    log_info("Bienvenido al Taxímetro Digital! Programa iniciado.")
    print("Bienvenido al Taxímetro Digital!")
    print('''Estos son los comandos disponibles: 
          - "E" para empezar 
          - "P" para parar 
          - "C" para continuar
          - "F" para finalizar
          - "H" para visualizar el Historial
          - "X" para salir
            con ellos puede usar el programa.\n''')

    while True:
        comando = input("Ingrese un comando: ").upper()
        if comando == "E":
            taximetro.start()
            log_info(f"Comando {comando}: Taxímetro iniciado.")
        elif comando == "P":
            taximetro.stop()
            log_info(f"Comando {comando}: Taxímetro detenido.")
        elif comando == "C":
            taximetro.continue_road()
            log_info(f"Comando {comando}: Taxímetro continuado.")
        elif comando == "F":
            taximetro.finish_road()
            taximetro.clear()
            log_info(f"Comando {comando}: Taxímetro finalizado y reiniciado.")
        elif comando == "H":
            taximetro.history_db()
            log_info(f"Comando {comando}: Historial visualizado.")
        elif comando == "X":
            print("Gracias por usar nuestro taximetro.")
            log_info("Programa terminado por el usuario.")
            break
        else:
            print("Comando inválido. Intente de nuevo.")
            log_warning("Comando inválido ingresado.")

if __name__ == "__main__":
    user = "Usuario predeterminado"  # Asumiendo que se obtiene el nombre de usuario de alguna manera
    main(user)