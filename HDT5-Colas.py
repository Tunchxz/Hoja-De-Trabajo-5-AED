# Universidad del Valle de Guatemala
# Facultad de Ingeniería
# Departamento de Ciencias de la Computación
# CC2016 - Algoritmos y Estructura de Datos
# Cristian Túnnchez - 231359
# Guatemala, 3 de marzo de 2024

import simpy
import random
import numpy as np

# Establecemos una semilla para la generación de números aleatorios
SEMILLA_ALEATORIA = 40
# Intervalo para la llegada de nuevos procesos
NUEVO_PROCESO = 10
# Cantidad total de memoria RAM
CANTIDAD_RAM = 100
# Velocidad del CPU (número de instrucciones por unidad de tiempo)
VELOCIDAD_CPU = 3
# Número de CPUs
NUM_CPUS = 1
# Número de procesos
NUM_PROCESOS = 50

class Proceso:
    def __init__(self, env, nombre, ram, cpus, instrucciones, memoria, tiempo_proceso, tiempo_total):
        # Inicializamos los atributos del proceso
        self.env = env
        self.nombre = nombre
        self.ram = ram
        self.cpus = cpus
        self.instrucciones = instrucciones
        self.memoria = memoria
        self.tiempo_proceso = tiempo_proceso
        self.tiempo_total = tiempo_total

    def ejecutar(self):
        # El proceso llega al sistema operativo (estado "New")
        yield self.env.timeout(random.expovariate(1.0 / NUEVO_PROCESO))
        print(f'Proceso {self.nombre} llega al sistema en {self.env.now}')
        
        # El proceso solicita memoria RAM (si hay suficiente, pasa a "Ready")
        with self.ram.get(self.memoria) as req:
            yield req
            print(f'Proceso {self.nombre} obtiene {self.memoria} de RAM en {self.env.now}')
            
            # El proceso espera por el CPU
            with self.cpus.request() as req:
                print(f'Proceso {self.nombre} empieza a ejecutarse en la CPU en {self.env.now}')
                yield req
                
                # El CPU atiende al proceso (estado "Running")
                print(f'Proceso {self.nombre} empezó a correr en {self.env.now}')
                while self.instrucciones:
                    if self.instrucciones > VELOCIDAD_CPU:
                        self.instrucciones -= VELOCIDAD_CPU
                    else:
                        self.instrucciones = 0
                    
                    # El proceso deja el CPU
                    yield self.env.timeout(1)
                    print(f'Proceso {self.nombre} ha ejecutado {VELOCIDAD_CPU} instrucciones en {self.env.now}')
                    
                    # Si el proceso aún tiene instrucciones, puede pasar a "Waiting" o volver a "Ready"
                    if random.randint(1, 2) == 1 and self.instrucciones:
                        print(f'Proceso {self.nombre} pasa a realizar tareas I/O en {self.env.now}')
                        yield self.env.timeout(1)
                
                # Si el proceso no tiene más instrucciones pasa a "terminado" y libera los recursos.
                print(f'Proceso {self.nombre} completa su ejecución en {self.env.now}')
            self.ram.put(self.memoria)
            self.tiempo_total[self.nombre] = self.env.now - self.tiempo_proceso

def generador_procesos(env, ram, cpus, num_procesos, tiempo_total):
    # Generamos procesos durante el tiempo de simulación
    for i in range(num_procesos):
        memoria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        proceso = Proceso(env, f'P{i}', ram, cpus, instrucciones, memoria, env.now, tiempo_total)
        env.process(proceso.ejecutar())
        yield env.timeout(random.expovariate(1.0 / NUEVO_PROCESO))

# Establecemos la semilla aleatoria
random.seed(SEMILLA_ALEATORIA)
# Creamos el entorno de simulación
env = simpy.Environment()
# Creamos la memoria RAM como un recurso tipo Container
ram = simpy.Container(env, CANTIDAD_RAM, init=CANTIDAD_RAM)
# Creamos el CPU como un recurso tipo Resource
cpus = simpy.Resource(env, capacity=NUM_CPUS)  # Mantenemos una sola cola para solicitar CPUs

# Diccionario para almacenar el tiempo total de cada proceso
tiempo_total = {}

# Iniciamos el generador de procesos
env.process(generador_procesos(env, ram, cpus, NUM_PROCESOS, tiempo_total))
# Ejecutamos la simulación
env.run()
tiempos = np.array(list(tiempo_total.values()))
print(f"Para {NUM_PROCESOS} procesos, con {CANTIDAD_RAM} de RAM, velocidad de CPU {VELOCIDAD_CPU}, y {NUM_CPUS} CPUs, el tiempo promedio en el sistema es {tiempos.mean()} y la desviación estándar es {tiempos.std()}")