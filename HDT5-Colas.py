import simpy
import random
import numpy as np

SEMILLA_ALEATORIA = 40
NUEVO_PROCESO = 10
CANTIDAD_RAM = 200
VELOCIDAD_CPU = 3
NUM_CPUS = 2
NUM_PROCESOS = 200

class Proceso:
    def __init__(self, env, nombre, ram, cpus, instrucciones, memoria, tiempo_proceso, tiempo_total):
        self.env = env
        self.nombre = nombre
        self.ram = ram
        self.cpus = cpus
        self.instrucciones = instrucciones
        self.memoria = memoria
        self.tiempo_proceso = tiempo_proceso
        self.tiempo_total = tiempo_total

    def ejecutar(self):
        yield self.env.timeout(random.expovariate(1.0 / NUEVO_PROCESO))
        print(f'Proceso {self.nombre} llega al sistema en {self.env.now}')
        with self.ram.get(self.memoria) as req:
            yield req
            print(f'Proceso {self.nombre} obtiene {self.memoria} de RAM en {self.env.now}')
            with self.cpus.request() as req:
                yield req
                print(f'Proceso {self.nombre} empieza a ejecutarse en la CPU en {self.env.now}')
                while self.instrucciones > 0:
                    if self.instrucciones >= VELOCIDAD_CPU:
                        self.instrucciones -= VELOCIDAD_CPU
                        yield self.env.timeout(1)
                    else:
                        yield self.env.timeout(self.instrucciones / VELOCIDAD_CPU)
                        self.instrucciones = 0
                print(f'Proceso {self.nombre} completa su ejecución en {self.env.now}')
                self.ram.put(self.memoria)
                self.tiempo_total[self.nombre] = self.env.now - self.tiempo_proceso

def generador_procesos(env, ram, cpus, num_procesos, tiempo_total):
    for i in range(num_procesos):
        memoria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        proceso = Proceso(env, f'P{i}', ram, cpus, instrucciones, memoria, env.now, tiempo_total)
        env.process(proceso.ejecutar())
        yield env.timeout(random.expovariate(1.0 / NUEVO_PROCESO))

random.seed(SEMILLA_ALEATORIA)
env = simpy.Environment()
ram = simpy.Container(env, CANTIDAD_RAM, init=CANTIDAD_RAM)
cpus = simpy.Resource(env, capacity=NUM_CPUS)

tiempo_total = {}
env.process(generador_procesos(env, ram, cpus, NUM_PROCESOS, tiempo_total))
env.run()

tiempos = np.array(list(tiempo_total.values()))
print(f"Para {NUM_PROCESOS} procesos, con {CANTIDAD_RAM} de RAM, velocidad de CPU {VELOCIDAD_CPU}, y {NUM_CPUS} CPUs, el tiempo promedio en el sistema es {tiempos.mean()} y la desviación estándar es {tiempos.std()}")