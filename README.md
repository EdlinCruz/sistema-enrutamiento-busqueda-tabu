# Sistema de enrutamiento con Búsqueda Tabú

Proyecto para optimizar las rutas de distribución de productos desde 10 centros de distribución hacia 90 sucursales ubicadas en Culiacán, Sinaloa.

La solución utiliza el algoritmo heurístico de Búsqueda Tabú para reducir la distancia total recorrida y el costo estimado de combustible.

## Funcionamiento general

El programa realiza el siguiente proceso:

1. Lee la tabla de distribución y las matrices de distancia y costo.
2. Identifica los 10 centros de distribución y las 90 sucursales.
3. Asigna cada sucursal a su centro de distribución más cercano.
4. Construye una ruta inicial mediante el método del vecino más cercano.
5. Optimiza cada ruta mediante Búsqueda Tabú.
6. Calcula la distancia, el costo y el porcentaje de mejora.
7. Genera un archivo de resultados y gráficas comparativas.
8. Ejecuta pruebas para comprobar que las rutas sean válidas.

## Archivos del proyecto

- `rutas.py`: código principal del sistema.
- `datos_distribucion_tiendas.xlsx`: información de centros y sucursales.
- `matriz_distancias.xlsx`: distancias entre las 100 ubicaciones.
- `matriz_costos_combustible.xlsx`: costos de combustible entre ubicaciones.
- `resultados_rutas.xlsx`: rutas iniciales y optimizadas.
- `comparacion_distancias.png`: comparación de las distancias por centro.
- `evolucion_busqueda_tabu.png`: evolución del algoritmo durante las iteraciones.

## Requisitos

- Python 3
- pandas
- numpy
- matplotlib
- openpyxl

## Instalación

Instalar las librerías necesarias con el siguiente comando:

```bash
pip install -r requirements.txt

## Configuración de la Búsqueda Tabú

- Máximo de iteraciones: 200.
- Duración de un movimiento tabú: 7 iteraciones.
- Límite sin mejora: 50 iteraciones.
- Movimiento utilizado: intercambio de dos sucursales dentro de una ruta.
- El centro de distribución permanece fijo al inicio y al final de cada recorrido.

## Resultados principales

- Distancia inicial: 225.24 km.
- Distancia optimizada: 203.47 km.
- Reducción: 21.78 km.
- Mejora obtenida: 9.67 %.
- Costo inicial: 33.79 unidades de costo.
- Costo optimizado: 30.52 unidades de costo.
- Ahorro: 3.27 unidades de costo.
- Pruebas superadas: 11 de 11.

## Autor

Eduar Yair Aguirre Ceballos 
Edlin Jaqueline Cruz Camargo 
Instituto Tecnológico de México, Campus Culiacán