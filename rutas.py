import pandas as pd
import matplotlib.pyplot as plt

ARCHIVO_DATOS = "datos_distribucion_tiendas.xlsx"
ARCHIVO_DISTANCIAS = "matriz_distancias.xlsx"
ARCHIVO_COSTOS = "matriz_costos_combustible.xlsx"

datos = pd.read_excel(ARCHIVO_DATOS)
matriz_distancias = pd.read_excel(ARCHIVO_DISTANCIAS).to_numpy(dtype=float)
matriz_costos = pd.read_excel(ARCHIVO_COSTOS).to_numpy(dtype=float)

##Numeración e identificación de las ubicaciones
datos["Nodo"] = range(1, len(datos) + 1)

centros = datos[datos["Tipo"] == "Centro de Distribución"]
tiendas = datos[datos["Tipo"] == "Tienda"]

print("ARCHIVOS CARGADOS CORRECTAMENTE")
print("--------------------------------")
print("Total de ubicaciones:", len(datos))
print("Centros de distribución:", len(centros))
print("Tiendas:", len(tiendas))
print("Tamaño de la matriz de distancias:", matriz_distancias.shape)
print("Tamaño de la matriz de costos:", matriz_costos.shape)

print("\nPRIMERAS UBICACIONES")
print(datos[["Nodo", "Tipo", "Nombre"]].head(12).to_string(index=False))

##asignacion de tiendas al centro más cercano
asignaciones = {}

for centro in range(10):
    asignaciones[centro] = []

for tienda in range(10, len(datos)):
    distancias_a_centros = matriz_distancias[tienda, 0:10] 
    #medimos la distancia desde una sucursal hacia los primeros 10 nodos
    centro_cercano = distancias_a_centros.argmin() 
    #con el uso de argim() obtenemos la distancia más pequeña, es decir, la más cercana
    asignaciones[centro_cercano].append(tienda) 
    #aqui la sucursal es agreagada al grupo del centro más cercano

print("\nASIGNACIÓN DE TIENDAS")
print("---------------------")

for centro, lista_tiendas in asignaciones.items():
    nodos = [tienda + 1 for tienda in lista_tiendas]

    print(
        f"Centro {centro + 1}: "
        f"{len(lista_tiendas)} tiendas -> {nodos}"
    )

##rutas inciales
def crear_ruta_inicial(centro, lista_tiendas):
    tiendas_sin_visitar = lista_tiendas.copy()
    ruta = [centro]
    ubicacion_actual = centro

    while tiendas_sin_visitar:
        siguiente_tienda = min(
            tiendas_sin_visitar, #contiene las sucursales que todavía no se han agregado a la ruta
            key=lambda tienda: matriz_distancias[ubicacion_actual][tienda]
            #se consulta la distancia desde ubicacion_actual hasta cada tienda pendiente
            #la función min va a devolver la sucursal que presenta 
            #la menor distancia y la almacena en siguiente_tienda
        )

        ruta.append(siguiente_tienda)#La sucursal se agrega a la ruta
        tiendas_sin_visitar.remove(siguiente_tienda)#se elimina de las sucursales pendientes  
        ubicacion_actual = siguiente_tienda#se convierte en la nueva ubicación actual

    ruta.append(centro)#se vuelve a buscar la sucursal más cercana

    return ruta

##calcular la distancia
def calcular_distancia(ruta):
    distancia_total = 0

    for posicion in range(len(ruta) - 1):
        origen = ruta[posicion]
        destino = ruta[posicion + 1]

        distancia_total += matriz_distancias[origen][destino]

    return distancia_total

##calcular el costo por ruta
def calcular_costo(ruta):
    costo_total = 0

    for posicion in range(len(ruta) - 1):
        origen = ruta[posicion]
        destino = ruta[posicion + 1]

        costo_total += matriz_costos[origen][destino]

    return costo_total

###########rutas inicialesS
rutas_iniciales = {}
distancias_iniciales = {}
costos_iniciales = {}

print("\n CALCULO DE LAS RUTAS INICIALES")
print("----------------")

for centro, lista_tiendas in asignaciones.items():
    ruta = crear_ruta_inicial(centro, lista_tiendas)
    distancia = calcular_distancia(ruta)
    costo = calcular_costo(ruta)

    rutas_iniciales[centro] = ruta
    distancias_iniciales[centro] = distancia
    costos_iniciales[centro] = costo

    nodos = [ubicacion + 1 for ubicacion in ruta]
    recorrido = " -> ".join(map(str, nodos))

    print(f"\nCentro {centro + 1}")
    print("Ruta:", recorrido)
    print(f"Distancia: {distancia:.2f}")
    print(f"Costo: {costo:.2f}")

distancia_total_inicial = sum(distancias_iniciales.values())
costo_total_inicial = sum(costos_iniciales.values())

print("\nRESULTADO INICIAL")
print("-----------------")
print(f"Distancia total: {distancia_total_inicial:.2f}")
print(f"Costo total: {costo_total_inicial:.2f}")    

##################
#Busqueda Tabú implementada
MAX_ITERACIONES = 200
DURACION_TABU = 7
LIMITE_SIN_MEJORA = 50


def busqueda_tabu(ruta_inicial):
    ruta_actual = ruta_inicial.copy()
    mejor_ruta = ruta_inicial.copy()

    mejor_distancia = calcular_distancia(mejor_ruta)

    lista_tabu = {}
    historial = [mejor_distancia]
    iteraciones_sin_mejora = 0

    for iteracion in range(1, MAX_ITERACIONES + 1):
        mejor_vecino = None
        distancia_vecino = float("inf")
        mejor_movimiento = None

        for posicion_1 in range(1, len(ruta_actual) - 2):
            for posicion_2 in range(posicion_1 + 1, len(ruta_actual) - 1):
                tienda_1 = ruta_actual[posicion_1]
                tienda_2 = ruta_actual[posicion_2]

                movimiento = tuple(sorted((tienda_1, tienda_2)))

                ruta_vecina = ruta_actual.copy()#copia la ruta actual

                ruta_vecina[posicion_1], ruta_vecina[posicion_2] = (#intercambia dos sucursales
                    ruta_vecina[posicion_2],
                    ruta_vecina[posicion_1]
                )
                #calcula la distancia de la nueva ruta
                nueva_distancia = calcular_distancia(ruta_vecina)

                #revisamos que el intercambio no este prohibido
                movimiento_tabu = (
                    lista_tabu.get(movimiento, 0) >= iteracion
                )
                #todavía puede aceptarse cuando mejora la mejor distancia encontrada.
                criterio_aspiracion = nueva_distancia < mejor_distancia

                if not movimiento_tabu or criterio_aspiracion:
                    if nueva_distancia < distancia_vecino:
                        mejor_vecino = ruta_vecina
                        distancia_vecino = nueva_distancia
                        mejor_movimiento = movimiento

        if mejor_vecino is None:
            break
        ##Actualizamos la lista
        ruta_actual = mejor_vecino
        #registramos/guardamos el movimiento
        lista_tabu[mejor_movimiento] = (
            iteracion + DURACION_TABU
        )

        lista_tabu = {
            movimiento: vencimiento
            for movimiento, vencimiento in lista_tabu.items()
            if vencimiento > iteracion
        }
        #Conservamos la mejor solución encontrada, 
        # aunque temporalmente explore una ruta con mayor distancia
        if distancia_vecino < mejor_distancia:
            mejor_ruta = ruta_actual.copy()
            mejor_distancia = distancia_vecino
            iteraciones_sin_mejora = 0
        else:
            iteraciones_sin_mejora += 1

        historial.append(mejor_distancia)
        #la búsqueda termina cuando alcanza el límite establecido
        if iteraciones_sin_mejora >= LIMITE_SIN_MEJORA:
            break
    #devuelve la mejor ruta
    return mejor_ruta, mejor_distancia, historial 
    



##optimizar rutas##############
###imprimir resultaods
rutas_optimizadas = {}
distancias_optimizadas = {}
costos_optimizados = {}
historiales = {}

print("\nRUTAS OPTIMIZADAS")
print("-----------------")

for centro, ruta_inicial in rutas_iniciales.items():
    mejor_ruta, mejor_distancia, historial = busqueda_tabu(
        ruta_inicial
    )

    mejor_costo = calcular_costo(mejor_ruta)

    rutas_optimizadas[centro] = mejor_ruta
    distancias_optimizadas[centro] = mejor_distancia
    costos_optimizados[centro] = mejor_costo
    historiales[centro] = historial

    nodos = [ubicacion + 1 for ubicacion in mejor_ruta]
    recorrido = " -> ".join(map(str, nodos))

    mejora = (
        (distancias_iniciales[centro] - mejor_distancia)
        / distancias_iniciales[centro]
    ) * 100

    print(f"\nCentro {centro + 1}")
    print("Ruta:", recorrido)
    print(
        f"Distancia inicial: "
        f"{distancias_iniciales[centro]:.2f}"
    )
    print(f"Distancia optimizada: {mejor_distancia:.2f}")
    print(f"Costo optimizado: {mejor_costo:.2f}")
    print(f"Mejora: {mejora:.2f}%")

distancia_total_optimizada = sum(
    distancias_optimizadas.values()
)

costo_total_optimizado = sum(
    costos_optimizados.values()
)

mejora_total = (
    (distancia_total_inicial - distancia_total_optimizada)
    / distancia_total_inicial
) * 100

print("\nRESULTADO FINAL")
print("---------------")
print(f"Distancia inicial: {distancia_total_inicial:.2f}")
print(f"Distancia optimizada: {distancia_total_optimizada:.2f}")
print(f"Costo inicial: {costo_total_inicial:.2f}")
print(f"Costo optimizado: {costo_total_optimizado:.2f}")
print(f"Mejora total: {mejora_total:.2f}%")


##codigo para generar las graficas
numeros_centros = [
    centro + 1 for centro in rutas_iniciales
]

valores_iniciales = [
    distancias_iniciales[centro]
    for centro in rutas_iniciales
]

valores_optimizados = [
    distancias_optimizadas[centro]
    for centro in rutas_iniciales
]

posiciones = list(range(len(numeros_centros)))
ancho = 0.35

plt.figure(figsize=(11, 6))

plt.bar(
    [posicion - ancho / 2 for posicion in posiciones],
    valores_iniciales,
    width=ancho,
    label="Distancia inicial",
    color="steelblue"
)

plt.bar(
    [posicion + ancho / 2 for posicion in posiciones],
    valores_optimizados,
    width=ancho,
    label="Distancia optimizada",
    color="seagreen"
)

plt.xlabel("Centro de distribución")
plt.ylabel("Distancia")
plt.title("Comparación de distancias por centro")
plt.xticks(posiciones, numeros_centros)
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()

plt.savefig(
    "comparacion_distancias.png",
    dpi=300
)

plt.close()


##grafica que muestra la evolucion de la optimizacion
plt.figure(figsize=(11, 6))

for centro, historial in historiales.items():
    iteraciones = range(len(historial))

    plt.plot(
        iteraciones,
        historial,
        label=f"Centro {centro + 1}"
    )

plt.xlabel("Iteración")
plt.ylabel("Mejor distancia encontrada")
plt.title("Evolución de la Búsqueda Tabú")
plt.legend(ncol=2)
plt.grid(linestyle="--", alpha=0.4)
plt.tight_layout()

plt.savefig(
    "evolucion_busqueda_tabu.png",
    dpi=300
)

plt.close()

print("\nGráficas generadas correctamente.")


################################
#exportar excel
resumen_resultados = []

for centro in rutas_iniciales:
    distancia_inicial = distancias_iniciales[centro]
    distancia_optimizada = distancias_optimizadas[centro]

    costo_inicial = costos_iniciales[centro]
    costo_optimizado = costos_optimizados[centro]

    ruta_inicial = " -> ".join(
        str(nodo + 1)
        for nodo in rutas_iniciales[centro]
    )

    ruta_optimizada = " -> ".join(
        str(nodo + 1)
        for nodo in rutas_optimizadas[centro]
    )

    porcentaje_mejora = (
        (distancia_inicial - distancia_optimizada)
        / distancia_inicial
    ) * 100

    resumen_resultados.append({
        "Centro": f"Centro {centro + 1}",
        "Cantidad de tiendas": len(asignaciones[centro]),
        "Ruta inicial": ruta_inicial,
        "Ruta optimizada": ruta_optimizada,
        "Distancia inicial": round(distancia_inicial, 2),
        "Distancia optimizada": round(distancia_optimizada, 2),
        "Distancia reducida": round(
            distancia_inicial - distancia_optimizada,
            2
        ),
        "Costo inicial": round(costo_inicial, 2),
        "Costo optimizado": round(costo_optimizado, 2),
        "Ahorro": round(costo_inicial - costo_optimizado, 2),
        "Mejora": f"{porcentaje_mejora:.2f}%",
        "Iteraciones": len(historiales[centro]) - 1
    })

resumen_resultados.append({
    "Centro": "TOTAL",
    "Cantidad de tiendas": 90,
    "Ruta inicial": "",
    "Ruta optimizada": "",
    "Distancia inicial": round(distancia_total_inicial, 2),
    "Distancia optimizada": round(
        distancia_total_optimizada,
        2
    ),
    "Distancia reducida": round(
        distancia_total_inicial - distancia_total_optimizada,
        2
    ),
    "Costo inicial": round(costo_total_inicial, 2),
    "Costo optimizado": round(costo_total_optimizado, 2),
    "Ahorro": round(
        costo_total_inicial - costo_total_optimizado,
        2
    ),
    "Mejora": f"{mejora_total:.2f}%",
    "Iteraciones": ""
})

tabla_resultados = pd.DataFrame(resumen_resultados)

#exportar hoja con asignacion de tiendas
detalle_asignaciones = []

for centro, lista_tiendas in asignaciones.items():
    for tienda in lista_tiendas:
        detalle_asignaciones.append({
            "Centro asignado": f"Centro {centro + 1}",
            "Nodo de la tienda": tienda + 1,
            "Nombre": datos.iloc[tienda]["Nombre"],
            "Nivel": datos.iloc[tienda]["Nivel_Tienda"],
            "Distancia al centro": round(
                matriz_distancias[centro][tienda],
                2
            )
        })

tabla_asignaciones = pd.DataFrame(detalle_asignaciones)

with pd.ExcelWriter(
    "resultados_rutas.xlsx",
    engine="openpyxl"
) as escritor:
    tabla_resultados.to_excel(
        escritor,
        sheet_name="Resumen",
        index=False
    )

    tabla_asignaciones.to_excel(
        escritor,
        sheet_name="Asignaciones",
        index=False
    )

print("Archivo resultados_rutas.xlsx generado correctamente.")



####################################################################
#PRUEBAS DE FUNCIONALIDAD
def ejecutar_pruebas():
    pruebas = []

    def comprobar(nombre, condicion):
        estado = "CORRECTO" if condicion else "ERROR"
        pruebas.append(condicion)
        print(f"[{estado}] {nombre}")

    print("\nPRUEBAS DE FUNCIONALIDAD")
    print("------------------------")

    comprobar(
        "Se cargaron 100 ubicaciones",
        len(datos) == 100
    )

    comprobar(
        "Se identificaron 10 centros",
        len(centros) == 10
    )

    comprobar(
        "Se identificaron 90 tiendas",
        len(tiendas) == 90
    )

    comprobar(
        "La matriz de distancias es de 100 x 100",
        matriz_distancias.shape == (100, 100)
    )

    comprobar(
        "La matriz de costos es de 100 x 100",
        matriz_costos.shape == (100, 100)
    )

    tiendas_asignadas = []

    for lista_tiendas in asignaciones.values():
        tiendas_asignadas.extend(lista_tiendas)

    comprobar(
        "Las 90 tiendas fueron asignadas",
        len(tiendas_asignadas) == 90
    )

    comprobar(
        "No existen tiendas repetidas",
        len(set(tiendas_asignadas)) == 90
    )

    comprobar(
        "Todas las tiendas correctas fueron asignadas",
        set(tiendas_asignadas) == set(range(10, 100))
    )

    rutas_correctas = True

    for centro, ruta in rutas_optimizadas.items():
        tiendas_ruta = ruta[1:-1]

        if ruta[0] != centro or ruta[-1] != centro:
            rutas_correctas = False

        if len(tiendas_ruta) != len(set(tiendas_ruta)):
            rutas_correctas = False

        if set(tiendas_ruta) != set(asignaciones[centro]):
            rutas_correctas = False

    comprobar(
        "Todas las rutas comienzan y terminan en su centro",
        rutas_correctas
    )

    comprobar(
        "La distancia optimizada no supera la inicial",
        distancia_total_optimizada <= distancia_total_inicial
    )

    relacion_costos_correcta = True

    for centro in rutas_optimizadas:
        distancia = distancias_optimizadas[centro]
        costo = costos_optimizados[centro]

        if abs(costo - distancia * 0.15) > 0.0001:
            relacion_costos_correcta = False

    comprobar(
        "El costo corresponde a distancia por 0.15",
        relacion_costos_correcta
    )

    pruebas_correctas = sum(pruebas)
    total_pruebas = len(pruebas)

    print("------------------------")
    print(
        f"Pruebas superadas: "
        f"{pruebas_correctas} de {total_pruebas}"
    )

    if pruebas_correctas == total_pruebas:
        print("Todas las pruebas fueron exitosas.")
    else:
        print("Existen pruebas que requieren revisión.")


ejecutar_pruebas()
